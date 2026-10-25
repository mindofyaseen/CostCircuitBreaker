"""
AWS Lambda Function Handler for CostCircuitBreaker.

Exposes evaluate_aws_cost_circuit_breaker as a serverless microservice
callable via Amazon API Gateway HTTP API or direct Lambda Invoke.
"""

import json
from core.circuit_breaker import CostCircuitBreaker

def lambda_handler(event, context):
    """
    AWS Lambda entry point.
    
    Accepts:
    {
      "body": "{\"architecture_spec\": \"...\", \"budget_limit\": 50.0}"
    }
    """
    try:
        # Support both API Gateway proxy integration and direct payload
        body_raw = event.get("body", event)
        if isinstance(body_raw, str):
            payload = json.loads(body_raw)
        else:
            payload = body_raw

        spec = payload.get("architecture_spec", "")
        budget = float(payload.get("budget_limit", 50.0))

        if not spec:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing 'architecture_spec' in request body."})
            }

        # Deterministic evaluation
        evaluation = CostCircuitBreaker.evaluate(architecture_spec=spec, budget_limit=budget)

        response_body = {
            "status": evaluation.status.value,
            "action": evaluation.action,
            "verdict": evaluation.verdict,
            "budget_limit_usd": evaluation.budget_limit,
            "projected_monthly_cost_usd": evaluation.projected_monthly_cost,
            "budget_delta_usd": evaluation.budget_delta,
            "cost_summary": {
                "total_monthly_usd": evaluation.cost_summary.total_monthly_cost,
                "major_offenders_count": len(evaluation.cost_summary.major_cost_offenders)
            }
        }

        if evaluation.rearchitect_plan:
            response_body["rearchitect_plan"] = {
                "optimized_cost_usd": evaluation.rearchitect_plan.optimized_monthly_cost,
                "savings_usd": evaluation.rearchitect_plan.total_monthly_savings,
                "savings_percent": evaluation.rearchitect_plan.percentage_savings
            }

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(response_body)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
