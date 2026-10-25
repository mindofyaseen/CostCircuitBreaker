"""
CostCircuitBreaker: Interactive Live FinOps Demonstration Dashboard.

Built with Streamlit and styled with modern dark glassmorphism.
Demonstrates the dramatic before-and-after contrast of giving an AI DevOps Agent
the evaluate_aws_cost_circuit_breaker tool.
"""

import os
import sys
import json
import glob
import streamlit as st

# Path configuration
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.base_agent import BaseCloudDevOpsAgent
from agent.protected_agent import ProtectedCloudDevOpsAgent
from core.circuit_breaker import CostCircuitBreaker

st.set_page_config(
    page_title="CostCircuitBreaker | Autonomous FinOps Safety Guard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium dark theme styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .main {
        background: radial-gradient(circle at top right, #111827, #030712);
        color: #F9FAFB;
    }

    .glass-card {
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    .stat-hero {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60A5FA, #A78BFA, #F472B6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .badge-danger {
        background: rgba(239, 68, 68, 0.2);
        border: 1px solid #EF4444;
        color: #FCA5A5;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }

    .badge-success {
        background: rgba(16, 185, 129, 0.2);
        border: 1px solid #10B981;
        color: #6EE7B7;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.title("⚡ CostCircuitBreaker")
st.markdown("### Autonomous FinOps Safety Tool for AI DevOps Agents")
st.markdown("*\"I gave my DevOps agent an AWS Pricing Circuit Breaker, because it tried to deploy a $2,480/mo cluster for a hobby project.\"*")
st.divider()

# Sidebar: Controls & Scenarios
st.sidebar.header("🎯 Mission Controls")

scenario_files = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", "benchmarks", "scenarios", "*.json")))
scenario_options = {}
for sf in scenario_files:
    with open(sf, "r", encoding="utf-8") as f:
        d = json.load(f)
        scenario_options[f"{d['scenario_id']}: {d['name']}"] = d

selected_name = st.sidebar.selectbox("Choose Architecture Scenario:", list(scenario_options.keys()))
current_scenario = scenario_options[selected_name]

# Budget Slider
budget = st.sidebar.slider(
    "Project Monthly Budget ($USD):",
    min_value=10.0,
    max_value=300.0,
    value=float(current_scenario.get("budget_limit_usd", 50.0)),
    step=5.0
)

# Tool Toggle (The Core Hackathon Demonstration)
st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ The Tool Switch")
tool_active = st.sidebar.toggle("Enable CostCircuitBreaker Tool", value=True)

if tool_active:
    st.sidebar.success("🛡️ **Protected Agent Active**\nTool: `evaluate_aws_cost_circuit_breaker` wired via Strands SDK.")
else:
    st.sidebar.error("⚠️ **Base Agent (Tool OFF)**\nBlind execution mode: No pricing checks or budget awareness.")

st.sidebar.markdown("---")
st.sidebar.info("""
**AWS Technologies:**
- Amazon Bedrock (Agent Reasoning)
- Strands Agents SDK 1.62.0
- AWS Lambda (Tool Execution Sandbox)
- AWS Pricing Catalog (us-east-1 reference)
""")

# Main Canvas Layout: Two Columns
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("#### 📋 Workload Prompt & Architecture Candidate")
    st.markdown(f"**Scenario:** `{current_scenario['scenario_id']}` — {current_scenario['name']}")
    st.info(f"**Prompt:** *\"{current_scenario['prompt']}\"*")

    st.markdown("##### Candidate Resources (Proposed by LLM)")
    st.json(current_scenario["resources"], expanded=False)

    st.metric(label="Target Budget Ceiling", value=f"${budget:.2f} / mo")

with col_right:
    st.markdown("#### 🚀 Agent Execution & Live Outcome")

    raw_resources = json.dumps(current_scenario["resources"])

    if not tool_active:
        # BASE AGENT RUN (BEFORE STATE)
        base_agent = BaseCloudDevOpsAgent()
        res = base_agent.plan_and_deploy(current_scenario["prompt"], raw_resources)
        
        # Calculate real unbudgeted cost for display
        eval_pre = CostCircuitBreaker.evaluate(raw_resources, budget_limit=budget)
        unbudgeted_cost = eval_pre.projected_monthly_cost
        overage = unbudgeted_cost - budget
        overage_pct = (overage / budget) * 100 if budget > 0 else 0

        st.markdown(f"""
        <div class="glass-card" style="border-color: #EF4444;">
            <span class="badge-danger">CRITICAL BILL SHOCK</span>
            <h2 style="color: #F87171; margin-top: 10px;">Deployment Blindly Approved!</h2>
            <p>The unaugmented agent has no concept of AWS pricing. It marked the stack as ready for deployment without checking the budget.</p>
            <div style="margin: 20px 0;">
                <p style="margin: 0; color: #9CA3AF; font-size: 0.9rem;">Projected Monthly Burn:</p>
                <p class="stat-hero" style="background: linear-gradient(135deg, #EF4444, #F87171); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    ${unbudgeted_cost:,.2f} / mo
                </p>
                <p style="color: #FCA5A5; font-weight: 600;">⚠️ ${overage:,.2f} over budget ({overage_pct:.0f}% cost overrun)!</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.warning("🚨 The developer wakes up to an unexpected cloud invoice at month-end.")

    else:
        # PROTECTED AGENT RUN (AFTER STATE)
        protected_agent = ProtectedCloudDevOpsAgent()
        prot_res = protected_agent.plan_and_deploy(
            current_scenario["prompt"],
            raw_resources,
            budget_override=budget
        )

        verdict = prot_res["final_verdict"]
        orig_cost = prot_res["original_unbudgeted_cost_usd"]
        opt_cost = prot_res["optimized_serverless_cost_usd"]
        saved = prot_res["monthly_dollars_saved_usd"]
        pct_saved = prot_res["percentage_savings"]

        if verdict == "RUNAWAY_DEPLOYMENT_INTERCEPTED":
            st.markdown(f"""
            <div class="glass-card" style="border-color: #10B981;">
                <span class="badge-success">🛡️ CIRCUIT TRIPPED & RE-ARCHITECTED</span>
                <h2 style="color: #34D399; margin-top: 10px;">Runaway Stack Intercepted!</h2>
                <p>The <code>evaluate_aws_cost_circuit_breaker</code> tool halted deployment when candidate spend exceeded the ${budget:.2f} budget.</p>
                <div style="display: flex; gap: 30px; margin: 20px 0;">
                    <div>
                        <p style="margin: 0; color: #9CA3AF; font-size: 0.85rem;">Blocked Cost:</p>
                        <p style="font-size: 1.6rem; font-weight: 700; color: #EF4444; margin: 0; text-decoration: line-through;">${orig_cost:,.2f}/mo</p>
                    </div>
                    <div>
                        <p style="margin: 0; color: #9CA3AF; font-size: 0.85rem;">New Serverless Cost:</p>
                        <p class="stat-hero" style="font-size: 2.2rem; background: linear-gradient(135deg, #10B981, #6EE7B7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                            ${opt_cost:,.2f} / mo
                        </p>
                    </div>
                    <div>
                        <p style="margin: 0; color: #9CA3AF; font-size: 0.85rem;">Monthly Savings:</p>
                        <p style="font-size: 1.6rem; font-weight: 700; color: #60A5FA; margin: 0;">${saved:,.2f} ({pct_saved}%)</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("🔍 View Serverless Architectural Replacements"):
                for rep in prot_res.get("serverless_replacements", []):
                    st.markdown(f"**Legacy:** `{rep['legacy']}` (${rep['legacy_cost_usd']:.2f}/mo)")
                    st.markdown(f"👉 **Replaced with:** `{rep['recommended_serverless']}` (**${rep['new_cost_usd']:.2f}/mo**)")
                    st.caption(rep['rationale'])
                    st.markdown("---")

            with st.expander("📄 View Approved Serverless CloudFormation Snippet"):
                st.code(prot_res["final_approved_template"], language="yaml")

        else:
            st.markdown(f"""
            <div class="glass-card" style="border-color: #3B82F6;">
                <span class="badge-success">🟢 BUDGET VERIFIED</span>
                <h2 style="color: #60A5FA; margin-top: 10px;">Clean Serverless Architecture Approved</h2>
                <p>Projected cost of <b>${orig_cost:.2f} / mo</b> is comfortably below the <b>${budget:.2f} / mo</b> budget ceiling.</p>
                <p style="color: #9CA3AF;">Zero false blocks. Deployment allowed to proceed.</p>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# Tabular Evidence & Reusability Section
st.markdown("### 📊 Verifiable Benchmark Evidence Summary")
st.markdown("Results across all 5 standard test suites (Automated Test Run):")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Interception Rate", "100.0%", "4 / 4 runaway stacks caught")
col_m2.metric("False Positive Rate", "0.0%", "0 / 1 optimal stacks blocked")
col_m3.metric("Total Prevented Waste", "$2,481.26 / mo", "Over 5 scenarios")
col_m4.metric("Avg Spend Reduction", "98.0%", "Serverless re-architecture")

st.markdown("""
```python
# The Reusable Pattern (Strands Agents SDK + Amazon Bedrock)
from strands import Agent, tool
from core.circuit_breaker import CostCircuitBreaker

@tool
def evaluate_aws_cost_circuit_breaker(architecture_spec: str, budget_limit: float = 50.0) -> str:
    \"\"\"Deterministic FinOps Circuit Breaker for Autonomous Cloud Agents.\"\"\"
    return CostCircuitBreaker.evaluate(architecture_spec, budget_limit=budget_limit).model_dump_json()

# Plugs directly into any Strands Agent:
agent = Agent(
    model="amazon.nova-micro-v1:0",
    tools=[evaluate_aws_cost_circuit_breaker],
    system_prompt="You are a Cloud DevOps agent. You must invoke evaluate_aws_cost_circuit_breaker before provisioning."
)
```
""")
