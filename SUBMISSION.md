# AWS Builder Center Submission: CostCircuitBreaker

> **Event:** Weekend Challenge: Give your Agent a Tool  
> **Challenge Window:** October 23, 2026 – October 26, 2026  
> **Author:** Muhammad Yaseen

---

## 1. Project Title & Tagline

* **Project Title:** `CostCircuitBreaker: Autonomous FinOps Safety Tool for AI DevOps Agents`
* **Headline / Pitch:** *"I gave my DevOps agent an AWS Pricing Circuit Breaker, because it tried to deploy a $2,480/month cluster for a hobby project."*
* **Tags:** `#strands-agents` `#amazon-bedrock` `#aws-lambda` `#agents` `#tools` `#finops` `#python`

---

## 2. The Agent You Started With and What It Could Already Do

I started with an AI Cloud DevOps agent built with **Amazon Bedrock** (using Amazon Nova Micro) and the **Strands Agents SDK**.

The base agent was capable of taking natural language architectural requirements (e.g. *"Deploy a scalable vector search service with a PostgreSQL database and background worker queue"*) and generating syntactically valid AWS CloudFormation and Terraform templates.

### The Fatal Flaw (The "Before" Problem):
While the agent generated valid infrastructure code, **it had zero financial awareness or concept of dollar bills**. When given a simple prompt for an e-commerce or worker workload, it naively provisioned multi-node OpenSearch clusters, Multi-AZ RDS Postgres `db.m6g.xlarge` instances, 2 managed NAT Gateways, and 10,000 Provisioned IOPS. 

Without human intervention, the agent blindly approved and attempted to deploy architectures costing **over $1,000 to $2,400 per month** for hobby and prototype workloads!

---

## 3. The One New Tool Added and Why It Was Picked

To solve this critical blind spot, I gave my agent one focused, deterministic tool:

### **`evaluate_aws_cost_circuit_breaker(architecture_spec, budget_limit=50.0)`**

### Why I Picked It:
Cloud architects and developers are terrified of autonomous agents running up runaway AWS bills. Instead of letting an LLM guess whether an architecture is "affordable" (which LLMs frequently hallucinate), this tool enforces a **deterministic financial safety gate**:

1. **Deterministic Pricing Engine:** Calculates exact monthly run rates for compute, databases, NAT Gateways, provisioned IOPS, load balancers, and idle IPv4 addresses using official US-East-1 AWS list rates.
2. **Circuit Breaker Policy:**
   - If projected monthly cost $\le$ budget (e.g. $50/mo) $\rightarrow$ `PASS` (Deployment permitted).
   - If projected monthly cost > budget $\rightarrow$ `CIRCUIT_TRIPPED` (Deployment hard-blocked).
3. **Serverless Rearchitect Synthesizer:** When the circuit trips, the tool automatically translates the expensive monolithic components into modern, pay-per-use AWS Serverless equivalents (AWS Lambda + Amazon DynamoDB + S3 + API Gateway + VPC Gateway Endpoints), reducing monthly spend by up to **98%** while meeting the same functional goals.

---

## 4. AWS Services Used

* **Amazon Bedrock (Amazon Nova):** Powers the agent's core reasoning, prompt interpretation, and architectural understanding.
* **Strands Agents SDK (1.62.0):** AWS's open-source model-driven agent framework used to initialize the agent, manage memory, and register the `@tool` decorator.
* **AWS Lambda:** Hosts the deterministic CostCircuitBreaker execution engine and provides an isolated sandbox for template evaluation.
* **AWS Pricing Reference Catalog (us-east-1):** Supplies deterministic hourly and monthly pricing rates for EC2, RDS, NAT Gateways, EBS, and OpenSearch.

---

## 5. Before vs After: Verifiable Proof & Numbers

We evaluated the agent across **5 realistic cloud architecture benchmarks**:

* **Interception Rate:** **100.0%** (4 out of 4 runaway cloud deployments were intercepted and blocked before touching the AWS account).
* **False Positive Rate:** **0.0%** (1 out of 1 optimal serverless workload was passed cleanly without false alarms).
* **Total Cloud Spend Without Tool (Base Agent):** **$2,532.26 / month**
* **Total Cloud Spend With Tool (CostCircuitBreaker):** **$51.00 / month**
* **Net Monthly Savings:** **$2,481.26 / month (98.0% overall spend reduction)**.

---

## 6. Demo Video Script (< 3 Minutes)

*Use this exact script when recording your 2 to 3 minute demo video for YouTube/Loom:*

### [0:00 - 0:30] Introduction & The Fatal Flaw
> *"Hi everyone! For the AWS Builder Center Weekend Challenge, I asked a simple question: What happens when an autonomous AI DevOps agent writes your cloud infrastructure?*
> 
> *I built a DevOps agent using Amazon Bedrock and the Strands Agents SDK. It writes valid CloudFormation templates. But here was the fatal flaw: LLMs have no idea what things cost.*
> 
> *When I asked it to build a simple e-commerce backend with search, it blindly provisioned a Multi-AZ OpenSearch cluster, an expensive RDS database, and 2 NAT Gateways. Total cost? Over $670 a month on a $50 hobby budget! If this ran autonomously, my AWS account would be drained."*

### [0:30 - 1:15] Introducing The Tool: `evaluate_aws_cost_circuit_breaker`
> *"So this weekend, I gave my agent one new tool: `evaluate_aws_cost_circuit_breaker`.*
> 
> *Built with the Strands Agents SDK and running on AWS Lambda, this tool intercepts any proposed CloudFormation or Terraform template BEFORE it ever deploys.*
> 
> *It parses the resource primitives, calculates exact AWS list prices, and checks against the project's hard monthly budget constraint. If the architecture exceeds the budget, it immediately trips the circuit and halts deployment."*

### [1:15 - 2:00] Live Demonstration: Tool OFF vs Tool ON
*(Show the interactive dashboard / terminal)*
> *"Let's see the Before and After live.*
> 
> *First, Tool OFF: The base agent runs Scenario 1. It says 'Approved for deployment!' But look at the screen: It just attempted to deploy a $671/month runaway architecture. Total disaster.*
> 
> *Now, let's flip the tool switch ON. We send the exact same prompt with a $50 budget.*
> 
> *Watch what happens: The tool immediately TRIPS THE CIRCUIT. 'BLOCKED: $671/mo exceeds $50 budget!'*
> 
> *And it doesn't just stop there. The tool feeds back an optimized Serverless alternative into the Strands agent: replacing NAT Gateways with free VPC Gateway Endpoints, replacing OpenSearch with Bedrock Knowledge Bases, and replacing RDS with DynamoDB on-demand.*
> 
> *The new verified monthly cost? Just $10.50 a month! That is a 98.4% cost reduction, fully automated and safe."*

### [2:00 - 2:40] Benchmark Results & Reusable Pattern
> *"Across our 5 automated test scenarios, the CostCircuitBreaker achieved a 100% interception rate, stopping over $2,480 in runaway cloud spend without a single false positive.*
> 
> *Best of all, this tool is packaged as a reusable Strands `@tool` decorator. Any developer can plug it into their Bedrock agent with just three lines of Python.*
> 
> *The model reasons, but the deterministic tool decides. Thank you for watching!"*
