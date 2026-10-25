"""
Official Strands Agent Tool Implementation for CostCircuitBreaker.

Provides the `@tool` interface compatible with Strands Agents SDK and Amazon Bedrock.
Can be plugged directly into any Strands Agent instance.
"""

import json
from strands import tool
from core.circuit_breaker import CostCircuitBreaker, CircuitStatus

@tool
def evaluate_aws_cost_circuit_breaker(architecture_spec: str, budget_limit: float = 50.0) -> str:
    """
    Evaluates proposed AWS CloudFormation, Terraform, or architectural resource specs
    against the project's monthly budget constraint.
    
    Acts as a deterministic safety gate:
    - If projected cost <= budget: Returns APPROVED with resource line-item costs.
    - If projected cost > budget: TRIPS THE CIRCUIT, HALTS DEPLOYMENT, and returns
      a structured line-item audit and an architecturally equivalent Serverless alternative.

    Args:
        architecture_spec: The CloudFormation template, Terraform plan, or resource list.
        budget_limit: Maximum allowed monthly spend in USD (default is $50.00).

    Returns:
        JSON string containing verdict, cost breakdown, and serverless re-architecture plan.
    """
    evaluation = CostCircuitBreaker.evaluate(
        architecture_spec=architecture_spec,
        budget_limit=budget_limit
    )

    # Convert evaluation into clean agent-consumable JSON payload
    payload = {
        "status": evaluation.status.value,
        "action": evaluation.action,
        "verdict": evaluation.verdict,
        "budget_limit_usd": evaluation.budget_limit,
        "projected_monthly_cost_usd": evaluation.projected_monthly_cost,
        "budget_delta_usd": evaluation.budget_delta,
        "budget_delta_percent": evaluation.budget_delta_percent,
        "major_cost_offenders": [
            {
                "resource_id": r.resource_id,
                "resource_type": r.resource_type,
                "monthly_cost_usd": r.monthly_cost,
                "drivers": r.cost_drivers
            }
            for r in evaluation.cost_summary.major_cost_offenders
        ],
        "all_resources": [
            {
                "resource_id": r.resource_id,
                "resource_type": r.resource_type,
                "monthly_cost_usd": r.monthly_cost
            }
            for r in evaluation.cost_summary.resources
        ]
    }

    if evaluation.rearchitect_plan:
        payload["serverless_rearchitect_recommendation"] = {
            "optimized_monthly_cost_usd": evaluation.rearchitect_plan.optimized_monthly_cost,
            "monthly_savings_usd": evaluation.rearchitect_plan.total_monthly_savings,
            "percentage_savings": evaluation.rearchitect_plan.percentage_savings,
            "replacements": [
                {
                    "legacy": rep.legacy_resource,
                    "legacy_cost_usd": rep.legacy_monthly_cost,
                    "recommended_serverless": rep.recommended_serverless_service,
                    "new_cost_usd": rep.recommended_monthly_cost,
                    "savings_usd": rep.monthly_savings,
                    "rationale": rep.architectural_rationale
                }
                for rep in evaluation.rearchitect_plan.replacements
            ],
            "serverless_template_snippet": evaluation.rearchitect_plan.serverless_template_snippet
        }

    return json.dumps(payload, indent=2)

def get_tool_metadata():
    """Returns registration metadata for hackathon submission documentation."""
    return {
        "tool_name": "evaluate_aws_cost_circuit_breaker",
        "sdk": "strands-agents 1.62.0",
        "primary_aws_services": ["Amazon Bedrock", "AWS Lambda", "AWS Pricing / Budgets"],
        "purpose": "Deterministic FinOps safety gate preventing runaway cloud deployment costs",
        "deterministic_policy": "Hard threshold: projected_cost <= budget_limit (Default $50/mo)"
    }
