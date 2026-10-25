"""
Circuit Breaker Core Decision Engine for CostCircuitBreaker.

Evaluates proposed cloud architectures against deterministic financial policies
and halts runaway deployments before they hit the AWS account.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from core.pricing_engine import AWSPricingEngine, ArchitectureCostSummary, ResourceCostEstimate
from core.template_parser import TemplateParser
from core.rearchitect_synthesizer import RearchitectSynthesizer, RearchitectResult

class CircuitStatus(str, Enum):
    PASS = "PASS"
    CIRCUIT_TRIPPED = "CIRCUIT_TRIPPED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"

class CircuitBreakerEvaluation(BaseModel):
    status: CircuitStatus
    verdict: str
    action: str
    budget_limit: float
    projected_monthly_cost: float
    budget_delta: float
    budget_delta_percent: float
    cost_summary: ArchitectureCostSummary
    rearchitect_plan: Optional[RearchitectResult] = None
    compliance_hash: str = ""
    evaluation_timestamp: str = ""

class CostCircuitBreaker:
    """The Autonomous FinOps Safety Guard for AI DevOps Agents."""

    DEFAULT_BUDGET = 50.0  # $50/month standard dev/hobby threshold

    @classmethod
    def evaluate(
        cls,
        architecture_spec: str,
        budget_limit: float = DEFAULT_BUDGET,
        project_name: str = "Cloud Workload"
    ) -> CircuitBreakerEvaluation:
        """
        Parses the candidate architecture, evaluates deterministic costs,
        and trips the circuit if projected costs exceed budget.
        """
        # 1. Parse raw architecture / template into normalized resources
        resources = TemplateParser.parse(architecture_spec)

        if not resources:
            return CircuitBreakerEvaluation(
                status=CircuitStatus.REVIEW_REQUIRED,
                verdict="Empty or Unparseable Architecture Spec",
                action="MANUAL_REVIEW",
                budget_limit=budget_limit,
                projected_monthly_cost=0.0,
                budget_delta=0.0,
                budget_delta_percent=0.0,
                cost_summary=ArchitectureCostSummary(
                    total_monthly_cost=0.0,
                    resources=[],
                    major_cost_offenders=[],
                    audit_notes=["No recognizable AWS resources detected in candidate spec."]
                )
            )

        # 2. Calculate deterministic cost summary
        cost_summary = AWSPricingEngine.evaluate_architecture(resources)
        projected = cost_summary.total_monthly_cost
        delta = round(projected - budget_limit, 2)
        delta_pct = round((delta / budget_limit) * 100, 1) if budget_limit > 0 else 0.0

        # 3. Decision Boundary: The Circuit Gate
        if projected <= budget_limit:
            # PASS
            return CircuitBreakerEvaluation(
                status=CircuitStatus.PASS,
                verdict=f"APPROVED: Projected monthly cost of ${projected:.2f} is within budget of ${budget_limit:.2f}.",
                action="DEPLOYMENT_PERMITTED",
                budget_limit=budget_limit,
                projected_monthly_cost=projected,
                budget_delta=delta,
                budget_delta_percent=delta_pct,
                cost_summary=cost_summary,
                rearchitect_plan=None
            )
        else:
            # CIRCUIT TRIPPED - HALT DEPLOYMENT
            rearchitect = RearchitectSynthesizer.synthesize(resources, projected)
            
            offender_str = ", ".join([f"{o.resource_id} (${o.monthly_cost:.2f})" for o in cost_summary.major_cost_offenders[:3]])
            verdict = (
                f"BLOCKED: Projected spend of ${projected:.2f}/mo violates monthly budget of ${budget_limit:.2f}/mo "
                f"({delta_pct}% overage). Major cost drivers: {offender_str}."
            )

            return CircuitBreakerEvaluation(
                status=CircuitStatus.CIRCUIT_TRIPPED,
                verdict=verdict,
                action="HALT_DEPLOYMENT_AND_REWRITE",
                budget_limit=budget_limit,
                projected_monthly_cost=projected,
                budget_delta=delta,
                budget_delta_percent=delta_pct,
                cost_summary=cost_summary,
                rearchitect_plan=rearchitect
            )
