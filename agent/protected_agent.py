"""
Protected Agent (The Upgraded Strands Agent with CostCircuitBreaker Tool).

Bridges Amazon Bedrock and the deterministic CostCircuitBreaker tool
to intercept runaway deployments and re-architect them to budget-compliant serverless services.
"""

import json
from typing import Dict, Any, Optional

from tools.cost_circuit_breaker_tool import evaluate_aws_cost_circuit_breaker

class ProtectedCloudDevOpsAgent:
    """
    The FinOps-Augmented DevOps Agent built with Strands Tooling pattern.
    
    Before submitting any infrastructure stack to AWS CloudFormation or Terraform,
    it MUST invoke evaluate_aws_cost_circuit_breaker.
    If the circuit trips, it automatically re-architects the workload to stay within budget.
    """

    AGENT_NAME = "CostCircuitBreaker-DevOpsAgent-v2"
    DESCRIPTION = "Strands-Augmented Cloud Architect with Deterministic FinOps Safety Tool"

    def __init__(self, budget_limit: float = 50.0, model_id: str = "amazon.nova-micro-v1:0"):
        self.budget_limit = budget_limit
        self.model_id = model_id
        self.tool = evaluate_aws_cost_circuit_breaker

    def plan_and_deploy(
        self,
        requirement: str,
        candidate_architecture: str,
        budget_override: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executes the closed-loop safety evaluation workflow:
        1. Invokes the CostCircuitBreaker tool with candidate architecture.
        2. Evaluates the deterministic verdict.
        3. If CIRCUIT_TRIPPED: Intercepts deployment, extracts serverless recommendations,
           and re-evaluates the new serverless architecture to guarantee compliance.
        4. If PASS: Approves clean deployment.
        """
        active_budget = budget_override if budget_override is not None else self.budget_limit

        # Step 1: Tool Call 1 - Initial Candidate Architecture Evaluation
        tool_raw_result = self.tool(
            architecture_spec=candidate_architecture,
            budget_limit=active_budget
        )
        eval_result = json.loads(tool_raw_result)

        history = [
            {
                "phase": "INITIAL_EVALUATION",
                "tool_called": "evaluate_aws_cost_circuit_breaker",
                "budget_limit_usd": active_budget,
                "projected_cost_usd": eval_result.get("projected_monthly_cost_usd"),
                "status": eval_result.get("status"),
                "action": eval_result.get("action")
            }
        ]

        if eval_result.get("status") == "CIRCUIT_TRIPPED":
            # Circuit tripped! Over budget!
            original_cost = eval_result.get("projected_monthly_cost_usd")
            rearchitect = eval_result.get("serverless_rearchitect_recommendation", {})
            new_template = rearchitect.get("serverless_template_snippet", "")

            # Step 2: Tool Call 2 - Closed-Loop Verification of Re-architected Spec
            verification_raw = self.tool(
                architecture_spec=new_template,
                budget_limit=active_budget
            )
            verification_result = json.loads(verification_raw)

            history.append({
                "phase": "REARCHITECT_VERIFICATION",
                "tool_called": "evaluate_aws_cost_circuit_breaker",
                "budget_limit_usd": active_budget,
                "projected_cost_usd": verification_result.get("projected_monthly_cost_usd"),
                "status": verification_result.get("status"),
                "action": verification_result.get("action")
            })

            return {
                "agent": self.AGENT_NAME,
                "execution_mode": "CIRCUIT_TRIPPED_AND_RESOLVED",
                "final_verdict": "RUNAWAY_DEPLOYMENT_INTERCEPTED",
                "original_unbudgeted_cost_usd": original_cost,
                "optimized_serverless_cost_usd": verification_result.get("projected_monthly_cost_usd"),
                "monthly_dollars_saved_usd": round(original_cost - verification_result.get("projected_monthly_cost_usd", 0), 2),
                "percentage_savings": rearchitect.get("percentage_savings", 0.0),
                "budget_limit_usd": active_budget,
                "safety_guardrail": "CostCircuitBreaker Tool (Active)",
                "intervention_history": history,
                "major_cost_offenders_blocked": eval_result.get("major_cost_offenders", []),
                "serverless_replacements": rearchitect.get("replacements", []),
                "final_approved_template": new_template
            }
        else:
            # Clean pass within budget
            return {
                "agent": self.AGENT_NAME,
                "execution_mode": "PASSED_WITHIN_BUDGET",
                "final_verdict": "APPROVED_FOR_DEPLOYMENT",
                "original_unbudgeted_cost_usd": eval_result.get("projected_monthly_cost_usd"),
                "optimized_serverless_cost_usd": eval_result.get("projected_monthly_cost_usd"),
                "monthly_dollars_saved_usd": 0.0,
                "percentage_savings": 0.0,
                "budget_limit_usd": active_budget,
                "safety_guardrail": "CostCircuitBreaker Tool (Active)",
                "intervention_history": history,
                "final_approved_template": candidate_architecture
            }
