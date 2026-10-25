"""
AWS Pricing Engine for CostCircuitBreaker.

Provides deterministic, auditable cost estimation for AWS resource primitives
based on official AWS pricing rates (us-east-1 reference region).
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ResourceCostEstimate(BaseModel):
    resource_id: str
    resource_type: str
    quantity: int = 1
    unit_hourly_cost: float = 0.0
    monthly_cost: float = 0.0
    cost_drivers: List[str] = Field(default_factory=list)
    is_major_offender: bool = False

class ArchitectureCostSummary(BaseModel):
    total_monthly_cost: float
    resources: List[ResourceCostEstimate]
    major_cost_offenders: List[ResourceCostEstimate]
    currency: str = "USD"
    reference_region: str = "us-east-1"
    audit_notes: List[str] = Field(default_factory=list)

class AWSPricingEngine:
    """Deterministic AWS pricing catalog and cost calculator."""

    # Baseline monthly hours (730 hours in average month)
    HOURS_PER_MONTH = 730

    # Official AWS US-East-1 reference rates
    EC2_RATES = {
        "t3.nano": 0.0052,
        "t3.micro": 0.0104,
        "t3.small": 0.0208,
        "t3.medium": 0.0416,
        "t3.large": 0.0832,
        "m6g.medium": 0.0385,
        "m6g.large": 0.0770,
        "m6g.xlarge": 0.1540,
        "c6i.large": 0.0850,
        "c6i.xlarge": 0.1700,
        "c6i.2xlarge": 0.3400,
        "p4de.24xlarge": 32.7726,  # GPU powerhouse ($23.9k/mo)
    }

    RDS_RATES = {
        "db.t3.micro": 0.017,
        "db.t3.small": 0.034,
        "db.t3.medium": 0.068,
        "db.m6g.large": 0.133,
        "db.m6g.xlarge": 0.266,
        "db.r6g.xlarge": 0.380,
    }

    OPENSEARCH_RATES = {
        "t3.small.search": 0.036,
        "m6g.large.search": 0.133,
        "m6g.xlarge.search": 0.266,
        "c6g.2xlarge.search": 0.446,
    }

    NAT_GATEWAY_HOURLY = 0.045  # $32.85/mo per gateway
    ALB_HOURLY = 0.0225         # $16.43/mo baseline
    IDLE_EIP_HOURLY = 0.005     # $3.65/mo per unattached/idle IPv4
    
    # EBS & Storage rates (monthly per GB or unit)
    EBS_GP3_GB_MONTH = 0.08
    EBS_IO2_GB_MONTH = 0.125
    IO2_PROVISIONED_IOPS_MONTH = 0.065   # 10,000 IOPS = $650/mo!
    GP3_PROVISIONED_IOPS_MONTH = 0.005   # Above 3000 free baseline

    # Serverless alternatives baseline estimates
    SERVERLESS_ESTIMATES = {
        "AWS::Lambda::Function": 2.50,      # Typical microservice 1M-5M invocations
        "AWS::DynamoDB::Table": 3.00,       # On-demand read/write for small-med workload
        "AWS::S3::Bucket": 1.20,            # 50GB storage + transfers
        "AWS::ApiGateway::HttpApi": 1.00,   # 1M HTTP API requests
        "AWS::SQS::Queue": 0.40,            # 1M messages
    }

    @classmethod
    def estimate_resource(cls, res: Dict[str, Any]) -> ResourceCostEstimate:
        """Estimates monthly cost for a single resource primitive."""
        res_type = res.get("Type", "")
        res_id = res.get("Id", res.get("LogicalResourceId", "UnknownResource"))
        props = res.get("Properties", {})
        qty = int(res.get("Quantity", 1))

        hourly = 0.0
        monthly = 0.0
        drivers = []

        # 1. NAT Gateway (The silent wallet killer)
        if "NATGateway" in res_type or "NatGateway" in res_type:
            hourly = cls.NAT_GATEWAY_HOURLY * qty
            monthly = hourly * cls.HOURS_PER_MONTH
            drivers.append(f"{qty}x NAT Gateway @ ${cls.NAT_GATEWAY_HOURLY}/hr idle charge")

        # 2. EC2 Instance
        elif "EC2::Instance" in res_type or "EC2" in res_type and "Instance" in res_type:
            instance_type = props.get("InstanceType", "t3.medium")
            base_hourly = cls.EC2_RATES.get(instance_type, 0.08)
            hourly = base_hourly * qty
            monthly = hourly * cls.HOURS_PER_MONTH
            drivers.append(f"{qty}x {instance_type} @ ${base_hourly}/hr")
            
            # Additional root volume
            vol_size = props.get("BlockDeviceMappings", [{}])[0].get("Ebs", {}).get("VolumeSize", 30) if props.get("BlockDeviceMappings") else 30
            ebs_monthly = vol_size * cls.EBS_GP3_GB_MONTH * qty
            monthly += ebs_monthly
            drivers.append(f"{vol_size}GB gp3 EBS (${ebs_monthly:.2f}/mo)")

        # 3. RDS Database Instance / Cluster
        elif "RDS::DBInstance" in res_type or "RDS" in res_type:
            db_class = props.get("DBInstanceClass", "db.m6g.large")
            multi_az = props.get("MultiAZ", False)
            base_hourly = cls.RDS_RATES.get(db_class, 0.133)
            multiplier = 2.0 if multi_az else 1.0
            hourly = base_hourly * multiplier * qty
            monthly = hourly * cls.HOURS_PER_MONTH
            
            az_note = "Multi-AZ (2x instance cost)" if multi_az else "Single-AZ"
            drivers.append(f"{qty}x {db_class} {az_note} @ ${hourly:.3f}/hr")
            
            allocated_storage = props.get("AllocatedStorage", 100)
            storage_cost = allocated_storage * 0.115 * qty
            monthly += storage_cost
            drivers.append(f"{allocated_storage}GB RDS Storage (${storage_cost:.2f}/mo)")

        # 4. OpenSearch / Elasticsearch Cluster
        elif "OpenSearchService::Domain" in res_type or "Elasticsearch" in res_type:
            cluster_config = props.get("ClusterConfig", {})
            instance_type = cluster_config.get("InstanceType", "m6g.large.search")
            instance_count = cluster_config.get("InstanceCount", 2)
            dedicated_master = cluster_config.get("DedicatedMasterEnabled", False)
            master_count = cluster_config.get("DedicatedMasterCount", 3) if dedicated_master else 0
            
            data_node_rate = cls.OPENSEARCH_RATES.get(instance_type, 0.133)
            data_hourly = data_node_rate * instance_count
            master_hourly = (cls.OPENSEARCH_RATES.get("m6g.large.search", 0.133) * master_count) if dedicated_master else 0.0
            
            hourly = (data_hourly + master_hourly) * qty
            monthly = hourly * cls.HOURS_PER_MONTH
            drivers.append(f"{instance_count}x {instance_type} data nodes (${data_hourly * cls.HOURS_PER_MONTH:.2f}/mo)")
            if dedicated_master:
                drivers.append(f"{master_count}x Dedicated Master nodes (${master_hourly * cls.HOURS_PER_MONTH:.2f}/mo)")

        # 5. Elastic Load Balancer (ALB)
        elif "ElasticLoadBalancingV2::LoadBalancer" in res_type or "LoadBalancer" in res_type:
            hourly = cls.ALB_HOURLY * qty
            monthly = hourly * cls.HOURS_PER_MONTH
            drivers.append(f"{qty}x Application Load Balancer baseline ($16.43/mo)")

        # 6. EBS Provisioned IOPS (Extreme cost driver)
        elif "EC2::Volume" in res_type or "EBS" in res_type:
            vol_type = props.get("VolumeType", "gp3")
            size = props.get("Size", 100)
            iops = props.get("Iops", 3000)
            
            if vol_type == "io2":
                monthly = (size * cls.EBS_IO2_GB_MONTH) + (iops * cls.IO2_PROVISIONED_IOPS_MONTH)
                drivers.append(f"{size}GB io2 (${size * cls.EBS_IO2_GB_MONTH:.2f}) + {iops} Provisioned IOPS (${iops * cls.IO2_PROVISIONED_IOPS_MONTH:.2f}/mo)")
            else:
                extra_iops = max(0, iops - 3000)
                monthly = (size * cls.EBS_GP3_GB_MONTH) + (extra_iops * cls.GP3_PROVISIONED_IOPS_MONTH)
                drivers.append(f"{size}GB gp3 + {extra_iops} Extra IOPS")

        # 7. Unattached / Idle Elastic IP
        elif "EC2::EIP" in res_type or "ElasticIP" in res_type:
            is_idle = props.get("Unattached", True)
            if is_idle:
                hourly = cls.IDLE_EIP_HOURLY * qty
                monthly = hourly * cls.HOURS_PER_MONTH
                drivers.append(f"{qty}x Idle IPv4 Elastic IP @ $0.005/hr ($3.65/mo per IP)")

        # 8. Serverless Primitives (Low-cost champions)
        elif res_type in cls.SERVERLESS_ESTIMATES:
            est = cls.SERVERLESS_ESTIMATES[res_type] * qty
            monthly = est
            hourly = monthly / cls.HOURS_PER_MONTH
            drivers.append(f"Serverless pay-per-use baseline (~${est:.2f}/mo)")

        else:
            # Fallback estimation for generic resources
            monthly = 5.0 * qty
            hourly = monthly / cls.HOURS_PER_MONTH
            drivers.append("Standard managed service baseline (~$5.00/mo)")

        # Mark major offenders (anything >= $50/mo on a single resource)
        is_major = monthly >= 50.0

        return ResourceCostEstimate(
            resource_id=res_id,
            resource_type=res_type,
            quantity=qty,
            unit_hourly_cost=round(hourly, 4),
            monthly_cost=round(monthly, 2),
            cost_drivers=drivers,
            is_major_offender=is_major
        )

    @classmethod
    def evaluate_architecture(cls, resources: List[Dict[str, Any]]) -> ArchitectureCostSummary:
        """Evaluates the entire proposed architecture and returns complete breakdown."""
        estimates: List[ResourceCostEstimate] = []
        total_monthly = 0.0

        for r in resources:
            est = cls.estimate_resource(r)
            estimates.append(est)
            total_monthly += est.monthly_cost

        # Sort resources by cost descending
        estimates.sort(key=lambda x: x.monthly_cost, reverse=True)
        major_offenders = [e for e in estimates if e.is_major_offender or e.monthly_cost >= 40.0]

        notes = []
        if any("NATGateway" in e.resource_type for e in estimates):
            notes.append("ALERT: High-cost NAT Gateways detected. Consider VPC Endpoints or Serverless architecture.")
        if any(e.monthly_cost > 300 for e in estimates):
            notes.append("CRITICAL: Enterprise-tier always-on clusters detected in candidate spec.")

        return ArchitectureCostSummary(
            total_monthly_cost=round(total_monthly, 2),
            resources=estimates,
            major_cost_offenders=major_offenders,
            audit_notes=notes
        )
