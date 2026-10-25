"""
Template Parser for CostCircuitBreaker.

Parses CloudFormation templates (JSON/YAML), Terraform JSON state/plans,
or architectural resource manifests into normalized resource lists.
"""

import json
import re
from typing import List, Dict, Any
import yaml

class TemplateParser:
    """Parses infrastructure as code (IaC) and architecture manifests."""

    @classmethod
    def parse(cls, raw_content: str) -> List[Dict[str, Any]]:
        """
        Parses raw text (JSON, YAML, or structured lines) into normalized resource list.
        """
        raw_content = raw_content.strip()

        # 1. Try parsing as JSON
        if raw_content.startswith("{"):
            try:
                data = json.loads(raw_content)
                return cls._extract_from_dict(data)
            except Exception:
                pass

        # 2. Try parsing as YAML
        try:
            data = yaml.safe_load(raw_content)
            if isinstance(data, dict):
                return cls._extract_from_dict(data)
            elif isinstance(data, list):
                return cls._extract_from_list(data)
        except Exception:
            pass

        # 3. Fallback: Parse line-by-line / heuristic regex extraction
        return cls._extract_heuristic(raw_content)

    @classmethod
    def _extract_from_dict(cls, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        resources: List[Dict[str, Any]] = []

        # CloudFormation pattern: {"Resources": { "LogicalId": { "Type": "...", "Properties": {...} } }}
        if "Resources" in data and isinstance(data["Resources"], dict):
            for logical_id, res_obj in data["Resources"].items():
                if isinstance(res_obj, dict):
                    resources.append({
                        "Id": logical_id,
                        "Type": res_obj.get("Type", "Unknown"),
                        "Properties": res_obj.get("Properties", {}),
                        "Quantity": 1
                    })
            return resources

        # Terraform JSON plan / state pattern
        if "resource_changes" in data and isinstance(data["resource_changes"], list):
            for rc in data["resource_changes"]:
                res_type = rc.get("type", "")
                cfn_type = cls._terraform_to_cfn_type(res_type)
                props = rc.get("change", {}).get("after", {}) or {}
                resources.append({
                    "Id": rc.get("address", rc.get("name", "tf_res")),
                    "Type": cfn_type,
                    "Properties": props,
                    "Quantity": 1
                })
            return resources

        # Simplified key-value format (e.g. {"resources": [...]})
        if "resources" in data and isinstance(data["resources"], list):
            return cls._extract_from_list(data["resources"])

        return resources

    @classmethod
    def _extract_from_list(cls, items: List[Any]) -> List[Dict[str, Any]]:
        resources = []
        for i, item in enumerate(items):
            if isinstance(item, dict):
                resources.append({
                    "Id": item.get("Id", item.get("name", f"resource_{i+1}")),
                    "Type": item.get("Type", item.get("type", "AWS::Generic::Resource")),
                    "Properties": item.get("Properties", item.get("properties", {})),
                    "Quantity": item.get("Quantity", item.get("quantity", 1))
                })
        return resources

    @classmethod
    def _extract_heuristic(cls, text: str) -> List[Dict[str, Any]]:
        """Extracts common AWS resource mentions from natural language or unstructured text."""
        resources = []
        lines = text.split("\n")
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean:
                continue

            # Check for common resource patterns
            if "nat gateway" in line_clean.lower() or "natgateway" in line_clean.lower():
                qty = 2 if "2" in line_clean or "two" in line_clean or "multi" in line_clean.lower() else 1
                resources.append({"Id": f"NatGateway_{i}", "Type": "AWS::EC2::NatGateway", "Properties": {}, "Quantity": qty})
            
            elif "opensearch" in line_clean.lower() or "elasticsearch" in line_clean.lower():
                resources.append({
                    "Id": f"OpenSearchCluster_{i}",
                    "Type": "AWS::OpenSearchService::Domain",
                    "Properties": {
                        "ClusterConfig": {
                            "InstanceType": "m6g.large.search",
                            "InstanceCount": 2,
                            "DedicatedMasterEnabled": True
                        }
                    },
                    "Quantity": 1
                })
                
            elif "rds" in line_clean.lower() or "postgres" in line_clean.lower() or "mysql" in line_clean.lower() or "database" in line_clean.lower():
                resources.append({
                    "Id": f"DatabaseInstance_{i}",
                    "Type": "AWS::RDS::DBInstance",
                    "Properties": {
                        "DBInstanceClass": "db.m6g.large" if "large" in line_clean.lower() else "db.m6g.xlarge",
                        "MultiAZ": "multi" in line_clean.lower() or "replica" in line_clean.lower(),
                        "AllocatedStorage": 100
                    },
                    "Quantity": 1
                })
                
            elif "ec2" in line_clean.lower() or "instance" in line_clean.lower():
                match = re.search(r'([a-z0-9]+\.[a-z0-9]+)', line_clean)
                inst_type = match.group(1) if match else "c6i.2xlarge"
                resources.append({"Id": f"EC2Instance_{i}", "Type": "AWS::EC2::Instance", "Properties": {"InstanceType": inst_type}, "Quantity": 1})

        return resources

    @staticmethod
    def _terraform_to_cfn_type(tf_type: str) -> str:
        mapping = {
            "aws_instance": "AWS::EC2::Instance",
            "aws_nat_gateway": "AWS::EC2::NatGateway",
            "aws_db_instance": "AWS::RDS::DBInstance",
            "aws_opensearch_domain": "AWS::OpenSearchService::Domain",
            "aws_lb": "AWS::ElasticLoadBalancingV2::LoadBalancer",
            "aws_lambda_function": "AWS::Lambda::Function",
            "aws_dynamodb_table": "AWS::DynamoDB::Table",
            "aws_s3_bucket": "AWS::S3::Bucket",
        }
        return mapping.get(tf_type, f"AWS::{tf_type}")
