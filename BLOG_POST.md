# I gave my DevOps agent an AWS Pricing Circuit Breaker, because it tried to deploy a $2,480/mo cluster for a hobby project

![CostCircuitBreaker Cover Image](https://raw.githubusercontent.com/mindofyaseen/CostCircuitBreaker/main/docs/screenshots/cover_image.jpg)

> **AWS Builder Center Weekend Challenge:** Give your Agent a Tool  
> **Tags:** `#strands-agents` `#amazon-bedrock` `#aws-lambda` `#agents` `#tools` `#finops` `#python`  
> **GitHub Repository:** [https://github.com/mindofyaseen/CostCircuitBreaker](https://github.com/mindofyaseen/CostCircuitBreaker)  
> **Demo & Screenshots:** [https://github.com/mindofyaseen/CostCircuitBreaker#visual-dashboard-walkthrough](https://github.com/mindofyaseen/CostCircuitBreaker#visual-dashboard-walkthrough)

---

## The Day My Autonomous Agent Tried to Bankrupt Me

Like many cloud builders, I have been experimenting with autonomous AI agents that don’t just write code, but actually plan, architect, and deploy infrastructure directly to AWS. 

With **Amazon Bedrock** and AWS’s open-source **Strands Agents SDK**, building a Cloud DevOps agent is surprisingly intuitive. You give the agent a system prompt, connect it to your foundation model, and ask:

> *"Deploy a scalable backend for my new prototype: I need a web API, full-text product search, and a PostgreSQL database."*

The model reasons through the problem, generates valid AWS CloudFormation, and proudly responds:  
**`"Architecture generated and marked ready for deployment!"`**

I inspected the synthesized template. Technically, it was flawless. 
Financially, it was an absolute disaster.

Here is what the foundation model had happily provisioned for a hobby prototype:
* A 2-node **Amazon OpenSearch Service** cluster with dedicated master instances (~**$480.00 / month**)
* A Multi-AZ **Amazon RDS PostgreSQL** `db.m6g.xlarge` instance (~**$383.00 / month**)
* 2x Managed **AWS NAT Gateways** (~**$65.70 / month** idle baseline)
* 10,000 Provisioned IOPS on an **`io2` EBS Volume** (~**$650.00 / month**)

Total projected monthly burn? **Over $1,570 a month** for a prototype with zero users.

### The Fatal Blind Spot
LLMs don’t pay AWS bills. They don’t have credit cards, and they have no innate understanding of dollar amounts. If you ask an LLM to build a "resilient and scalable" architecture, it will pick the biggest, most redundant, enterprise-grade clusters in the catalog. 

Asking the LLM *"Is this affordable?"* doesn't work either—models frequently hallucinate pricing estimates, confuse hourly with monthly rates, or forget data transfer and idle resource fees.

For this Weekend Challenge, I decided to fix this dangerous capability gap once and for all.

---

## The One New Tool: `evaluate_aws_cost_circuit_breaker`

Instead of relying on model guesswork, I gave my Strands agent one focused, deterministic tool:

```python
@tool
def evaluate_aws_cost_circuit_breaker(architecture_spec: str, budget_limit: float = 50.0) -> str:
    """
    Deterministic FinOps Circuit Breaker for Autonomous Cloud Agents.
    Evaluates proposed AWS CloudFormation/Terraform against monthly budget.
    Trips the circuit and halts deployment if projected spend > budget.
    """
```

### The Design Philosophy:
> **The Model reasons. The Deterministic Tool decides.**

The agent is strictly forbidden from approving any infrastructure deployment on its own. Before any CloudFormation stack or Terraform plan can be executed, the agent **MUST** pass the template through `evaluate_aws_cost_circuit_breaker`.

### What the Tool Does Under the Hood:
1. **IaC Template Parsing:** Extracts resource primitives, instance families, storage tiers, Multi-AZ flags, and unattached Elastic IPs.
2. **Deterministic Pricing Engine:** Calculates exact monthly run rates based on official US-East-1 AWS list pricing (730-hour baseline).
3. **Hard Circuit Breaker Gate:**
   - **`PASS`**: If projected monthly cost $\le$ project budget (e.g. $50.00/mo) $\rightarrow$ Stack deployment is permitted.
   - **`CIRCUIT_TRIPPED`**: If projected monthly cost > budget $\rightarrow$ **Execution is immediately halted**. The tool returns a line-item audit highlighting the biggest cost offenders.
4. **Serverless Rearchitect Synthesizer:** When a circuit trips, the tool automatically re-architects the monolithic resources into modern AWS Serverless primitives meeting the same functional goal:
   - Replaces NAT Gateways with **AWS VPC Gateway Endpoints** ($0.00 charge for S3 & DynamoDB traffic).
   - Replaces provisioned OpenSearch with **Amazon Bedrock Knowledge Bases / OpenSearch Serverless** (pay-per-query).
   - Replaces provisioned Multi-AZ RDS with **Amazon DynamoDB (On-Demand)** or **Aurora Serverless v2**.
   - Replaces dedicated EC2 worker instances with **AWS Lambda + Amazon SQS**.

---

## The Live "Before vs After" Contrast

### 1. Tool OFF: Fatal Unbudgeted Bill Shock (Base Agent)
When the tool is disabled, the base agent blindly generates expensive clusters with zero budget awareness:

![Tool OFF: Fatal Unbudgeted Bill Shock](https://raw.githubusercontent.com/mindofyaseen/CostCircuitBreaker/main/docs/screenshots/screenshot_2_tool_off_bill_shock.png)

### 2. Tool ON: Runaway Deployment Intercepted & Re-Architected to Serverless
With `evaluate_aws_cost_circuit_breaker` active, the agent immediately catches the overage, halts deployment, and synthesizes a $10.50/mo serverless alternative:

![Tool ON: Intercepted & Re-architected](https://raw.githubusercontent.com/mindofyaseen/CostCircuitBreaker/main/docs/screenshots/screenshot_1_tool_on_intercepted.png)

### 3. Full 5-Scenario Automated Benchmark Matrix
![5-Scenario Benchmark Matrix](https://raw.githubusercontent.com/mindofyaseen/CostCircuitBreaker/main/docs/screenshots/screenshot_3_benchmark_matrix.png)

| Scenario | Monthly Budget | Base Agent Spend (Tool OFF) | Protected Agent Spend (Tool ON) | Dollars Saved | Final Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. E-Commerce Search & DB** | $50.00 | $671.24 / mo | **$10.50 / mo** | **$660.74 (98.4%)** | 🔴 Intercepted & Rewritten |
| **2. High-Compute Worker Fleet** | $40.00 | $1,041.23 / mo | **$10.50 / mo** | **$1,030.73 (99.0%)** | 🔴 Intercepted & Rewritten |
| **3. Doc Site with Accidental NAT** | $15.00 | $66.90 / mo | **$10.50 / mo** | **$56.40 (84.3%)** | 🔴 Intercepted & Rewritten |
| **4. Provisioned IOPS & Idle IPs** | $60.00 | $743.89 / mo | **$10.50 / mo** | **$733.39 (98.6%)** | 🔴 Intercepted & Rewritten |
| **5. Optimal Serverless Microservice** | $50.00 | $9.00 / mo | **$9.00 / mo** | **$0.00 (Optimal)** | 🟢 Passed (0% False Alarm) |
| **TOTALS** | — | **$2,532.26 / mo** | **$51.00 / mo** | **$2,481.26 / mo** | **100% Interception** |

### The Numbers:
* **Interception Accuracy:** **100.0%** (4 out of 4 runaway deployments halted before touching AWS).
* **False Positive Rate:** **0.0%** (The already-optimal Serverless microservice passed cleanly).
* **Total Cloud Waste Prevented:** **$2,481.26 / month (98.0% overall spend reduction)**!

---

## Closed-Loop Execution in Action

Here is what happens during a live agent run:

### Step 1: Initial Prompt
> **User:** *"Deploy a video rendering queue with an Application Load Balancer."*

The base model proposes: 4x `c6i.2xlarge` instances + ALB + 400GB gp3 storage.

### Step 2: Tool Call Interception
The agent calls `evaluate_aws_cost_circuit_breaker(template, budget_limit=40.0)`:

```json
{
  "status": "CIRCUIT_TRIPPED",
  "action": "HALT_DEPLOYMENT_AND_REWRITE",
  "verdict": "BLOCKED: Projected spend of $1,041.23/mo violates monthly budget of $40.00/mo (2503% overage).",
  "major_cost_offenders": [
    {
      "resource_id": "WorkerComputeFleet",
      "resource_type": "AWS::EC2::Instance",
      "monthly_cost_usd": 992.80
    }
  ]
}
```

### Step 3: Closed-Loop Re-architecture
The Strands agent reads the tool's structured feedback, generates the recommended **AWS Lambda + SQS** template, and feeds it back into the tool for a second verification.

The tool returns **`status: PASS`** at **$10.50 / month**. The stack is safely deployed.

---

## Reusable Pattern: Plug It Into Any Strands Agent

Because this is built with the **Strands Agents SDK**, you can add this exact safety gate to your own Bedrock agent in just 4 lines of Python:

```python
from strands import Agent, tool
from core.circuit_breaker import CostCircuitBreaker

# 1. Define the tool
@tool
def evaluate_aws_cost_circuit_breaker(architecture_spec: str, budget_limit: float = 50.0) -> str:
    """Evaluates proposed AWS templates against hard budget ceilings."""
    return CostCircuitBreaker.evaluate(architecture_spec, budget_limit=budget_limit).model_dump_json()

# 2. Attach to your Strands Agent
agent = Agent(
    model="amazon.nova-micro-v1:0",
    tools=[evaluate_aws_cost_circuit_breaker],
    system_prompt="You are an autonomous Cloud Architect. You MUST invoke evaluate_aws_cost_circuit_breaker before executing any deployment."
)
```

---

## How to Try It

Everything is open source and reproducible:

1. **Clone the Repo:**
   ```bash
   git clone https://github.com/mindofyaseen/CostCircuitBreaker.git
   cd CostCircuitBreaker
   pip install -r requirements.txt
   ```

2. **Run the Automated Benchmarks:**
   ```bash
   python benchmarks/run_benchmarks.py
   ```

3. **Launch the Live Streamlit Dashboard:**
   ```bash
   streamlit run web_ui/app.py
   ```
   *(Or open `web_ui/index.html` in your browser for the zero-dependency web playground).*

---

## Conclusion

As autonomous AI agents take over more operational tasks, the most important tool we can give them isn't more access—it's **guardrails**. 

Giving my agent an AWS Pricing Circuit Breaker transformed it from a dangerous liability that would accidentally burn $2,000 overnight into a trustworthy cloud engineer that guarantees cost efficiency by design.

*What tool have you given your agent this weekend? Let me know in the comments!*
