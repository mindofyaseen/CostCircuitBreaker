"""
Rearchitect Synthesizer for CostCircuitBreaker.

Transforms expensive, monolithic, or runaway AWS architectures into
cost-efficient, serverless, pay-per-use architectures meeting the same functional goals.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field

class ArchitectureReplacement(BaseModel):
    legacy_resource: str
    legacy_monthly_cost: float
    recommended_serverless_service: str
    recommended_monthly_cost: float
    monthly_savings: float
    architectural_rationale: str

class RearchitectResult(BaseModel):
    original_monthly_cost: float
    optimized_monthly_cost: float
    total_monthly_savings: float
    percentage_savings: float
    replacements: List[ArchitectureReplacement]
    serverless_template_snippet: str
    well_architected_pillars_addressed: List[str]

class RearchitectSynthesizer:
    """Synthesizes high-cost resources into modern AWS Serverless patterns."""

    @classmethod
    def synthesize(cls, resources: List[Dict[str, Any]], original_cost: float) -> RearchitectResult:
        replacements: List[ArchitectureReplacement] = []
        new_total_cost = 0.0

        for res in resources:
            res_type = res.get("Type", "")
            res_id = res.get("Id", "resource")
            props = res.get("Properties", {})
            qty = res.get("Quantity", 1)

            # 1. NAT Gateway Replacement
            if "NATGateway" in res_type or "NatGateway" in res_type:
                leg_cost = 32.85 * qty
                new_cost = 0.0  # VPC S3/DynamoDB Gateway endpoints are 100% free
                replacements.append(ArchitectureReplacement(
                    legacy_resource=f"{qty}x AWS NAT Gateway ({res_id})",
                    legacy_monthly_cost=round(leg_cost, 2),
                    recommended_serverless_service="AWS VPC Gateway Endpoints (S3/DynamoDB) + Direct Lambda egress",
                    recommended_monthly_cost=0.0,
                    monthly_savings=round(leg_cost, 2),
                    architectural_rationale="Gateway Endpoints for S3 and DynamoDB are completely free of hourly and data charges, eliminating costly NAT Gateways for internal AWS traffic."
                ))
                new_total_cost += new_cost

            # 2. OpenSearch / Elasticsearch Cluster Replacement
            elif "OpenSearch" in res_type or "Elasticsearch" in res_type:
                leg_cost = 480.0
                new_cost = 8.50
                replacements.append(ArchitectureReplacement(
                    legacy_resource=f"Provisioned OpenSearch Cluster ({res_id})",
                    legacy_monthly_cost=round(leg_cost, 2),
                    recommended_serverless_service="Amazon Bedrock Knowledge Bases / OpenSearch Serverless (On-Demand)",
                    recommended_monthly_cost=new_cost,
                    monthly_savings=round(leg_cost - new_cost, 2),
                    architectural_rationale="Replaced 24/7 dedicated compute and master instances with pay-per-search indexing, scaling down to $0 when idle."
                ))
                new_total_cost += new_cost

            # 3. RDS Multi-AZ or heavy database
            elif "RDS" in res_type or "DBInstance" in res_type:
                leg_cost = 383.0
                new_cost = 6.20
                replacements.append(ArchitectureReplacement(
                    legacy_resource=f"Provisioned Multi-AZ RDS Instance ({res_id})",
                    legacy_monthly_cost=round(leg_cost, 2),
                    recommended_serverless_service="Amazon DynamoDB (On-Demand) / Aurora Serverless v2 (0.5 ACU min)",
                    recommended_monthly_cost=new_cost,
                    monthly_savings=round(leg_cost - new_cost, 2),
                    architectural_rationale="Switched to on-demand serverless capacity with automatic scale-to-zero during off-peak hours, preserving multi-AZ durability at fraction of the cost."
                ))
                new_total_cost += new_cost

            # 4. EC2 Instances (Worker fleets or web servers)
            elif "EC2::Instance" in res_type:
                leg_cost = 244.80 * qty
                new_cost = 3.50
                replacements.append(ArchitectureReplacement(
                    legacy_resource=f"{qty}x Dedicated EC2 Instance ({res_id})",
                    legacy_monthly_cost=round(leg_cost, 2),
                    recommended_serverless_service="AWS Lambda + Amazon SQS Dead-Letter Queues",
                    recommended_monthly_cost=new_cost,
                    monthly_savings=round(leg_cost - new_cost, 2),
                    architectural_rationale="Event-driven serverless compute executes only when work arrives, eliminating idle server burn while autoscaling instantaneously."
                ))
                new_total_cost += new_cost

            # 5. Provisioned IOPS / io2 Volumes
            elif "EC2::Volume" in res_type or "EBS" in res_type:
                leg_cost = 650.0
                new_cost = 4.00
                replacements.append(ArchitectureReplacement(
                    legacy_resource=f"Provisioned IOPS io2 Volume ({res_id})",
                    legacy_monthly_cost=round(leg_cost, 2),
                    recommended_serverless_service="AWS EBS gp3 baseline (3000 free IOPS) or Amazon S3 tiered storage",
                    recommended_monthly_cost=new_cost,
                    monthly_savings=round(leg_cost - new_cost, 2),
                    architectural_rationale="Over-provisioned IOPS removed. Standard gp3 includes 3,000 baseline IOPS free of charge, saving 99% without sacrificing read latency for standard workloads."
                ))
                new_total_cost += new_cost

            # 6. ALB Load Balancer
            elif "LoadBalancer" in res_type:
                leg_cost = 16.43 * qty
                new_cost = 1.00
                replacements.append(ArchitectureReplacement(
                    legacy_resource=f"Application Load Balancer ({res_id})",
                    legacy_monthly_cost=round(leg_cost, 2),
                    recommended_serverless_service="Amazon API Gateway (HTTP API)",
                    recommended_monthly_cost=new_cost,
                    monthly_savings=round(leg_cost - new_cost, 2),
                    architectural_rationale="HTTP APIs charge purely per million requests ($1.00/M) rather than an always-on hourly baseline charge."
                ))
                new_total_cost += new_cost

            else:
                # Retain low-cost or serverless components
                new_total_cost += 2.00

        # Baseline safety for small ancillary serverless components
        new_total_cost = max(2.50, round(new_total_cost, 2))
        savings = max(0.0, round(original_cost - new_total_cost, 2))
        pct_savings = round((savings / original_cost * 100), 1) if original_cost > 0 else 0.0

        # Generate sample clean Serverless CloudFormation snippet
        snippet = """# Generated by CostCircuitBreaker Rearchitect Engine
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Cost-Optimized Serverless Architecture (Budget Compliant)'
Resources:
  HttpApiGateway:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      Name: CostOptimizedServiceApi
      ProtocolType: HTTP

  ComputeFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: WorkloadProcessor
      Runtime: python3.12
      Handler: index.handler
      MemorySize: 512
      Timeout: 15

  ServerlessStorage:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: WorkloadState
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH
"""

        return RearchitectResult(
            original_monthly_cost=round(original_cost, 2),
            optimized_monthly_cost=new_total_cost,
            total_monthly_savings=savings,
            percentage_savings=pct_savings,
            replacements=replacements,
            serverless_template_snippet=snippet,
            well_architected_pillars_addressed=[
                "Cost Optimization (Pillar 5): Eliminated idle capacity & over-provisioning",
                "Operational Excellence (Pillar 1): Managed serverless primitives require zero OS patching",
                "Reliability (Pillar 3): High multi-AZ availability built into Lambda & DynamoDB by default"
            ]
        )
