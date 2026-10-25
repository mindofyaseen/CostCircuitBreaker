"""
Base Agent (The Baseline Without Tool).

Demonstrates the fatal flaw of autonomous cloud engineering agents:
generating expensive, monolithic architectures without financial awareness,
causing catastrophic bill shocks on the AWS account.
"""

from typing import Dict, Any

class BaseCloudDevOpsAgent:
    """
    The unaugmented AI DevOps Agent.
    
    Can write CloudFormation or Terraform from natural language requirements,
    but has zero concept of AWS pricing or monthly budget ceilings.
    """

    AGENT_NAME = "Baseline-DevOpsAgent-v1"
    DESCRIPTION = "Autonomous CloudFormation/Terraform Synthesizer without Cost Verification"

    def __init__(self, model_name: str = "amazon.nova-micro-v1:0"):
        self.model_name = model_name
        self.tools = []  # No safety tools attached

    def plan_and_deploy(self, requirement: str, candidate_architecture: str) -> Dict[str, Any]:
        """
        Baseline agent behavior:
        Takes the user requirement, accepts the candidate architecture,
        and naively marks it as 'APPROVED_FOR_DEPLOYMENT' without any financial checks.
        """
        # Baseline agent hallucination: assumes bigger/more clusters = better performance
        return {
            "agent": self.AGENT_NAME,
            "status": "APPROVED_WITHOUT_SAFETY_CHECKS",
            "verdict": "Architecture generated and marked ready for CloudFormation stack creation.",
            "financial_awareness": "NONE (Missing CostCircuitBreaker Tool)",
            "safety_action": "PROCEED_WITH_DEPLOYMENT",
            "raw_architecture_spec": candidate_architecture,
            "warning": "CRITICAL RISK: Candidate architecture has not been evaluated against budget."
        }
