/**
 * CostCircuitBreaker Interactive Dashboard Logic
 */

const SCENARIOS = {
  "1": {
    id: "SCENARIO_1",
    name: "E-Commerce Search & DB",
    prompt: "Deploy a scalable e-commerce product catalog with full-text search and transactional PostgreSQL database.",
    defaultBudget: 50,
    unbudgetedCost: 671.24,
    optimizedCost: 10.50,
    resources: [
      { Id: "ProductSearchDomain", Type: "AWS::OpenSearchService::Domain", Quantity: 1, MonthlyEst: "$250.00" },
      { Id: "OrdersDatabase", Type: "AWS::RDS::DBInstance (db.m6g.xlarge Multi-AZ)", Quantity: 1, MonthlyEst: "$355.54" },
      { Id: "EgressNatGateways", Type: "AWS::EC2::NatGateway", Quantity: 2, MonthlyEst: "$65.70" }
    ],
    replacements: [
      { legacy: "OpenSearch 2-Node Cluster ($250.00/mo)", newService: "Amazon Bedrock Knowledge Bases / OpenSearch Serverless ($8.50/mo)", rationale: "Pay-per-search serverless indexing; scales down to zero idle compute." },
      { legacy: "Multi-AZ RDS Postgres db.m6g.xlarge ($355.54/mo)", newService: "Amazon DynamoDB (On-Demand) / Aurora Serverless v2 ($2.00/mo)", rationale: "On-demand autoscaling with zero always-on base instances." },
      { legacy: "2x AWS NAT Gateways ($65.70/mo)", newService: "AWS VPC Gateway Endpoints ($0.00/mo)", rationale: "Direct S3/DynamoDB endpoints eliminate expensive NAT Gateway hourly and data charges." }
    ],
    cfnSnippet: `AWSTemplateFormatVersion: '2010-09-09'
Description: 'Cost-Optimized E-Commerce Architecture (Budget Compliant)'
Resources:
  HttpApiGateway:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      Name: ECommerceApi
      ProtocolType: HTTP

  CatalogFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: ProductCatalogService
      Runtime: python3.12
      Handler: catalog.handler
      MemorySize: 512

  DynamoOrderTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: Orders
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: orderId
          AttributeType: S
      KeySchema:
        - AttributeName: orderId
          KeyType: HASH`
  },
  "2": {
    id: "SCENARIO_2",
    name: "High-Compute Worker Fleet",
    prompt: "Deploy a fleet of background queue processors with an Application Load Balancer to handle video rendering jobs.",
    defaultBudget: 40,
    unbudgetedCost: 1041.23,
    optimizedCost: 10.50,
    resources: [
      { Id: "WorkerComputeFleet", Type: "AWS::EC2::Instance (4x c6i.2xlarge)", Quantity: 4, MonthlyEst: "$992.80" },
      { Id: "PublicIngressALB", Type: "AWS::ElasticLoadBalancingV2::LoadBalancer", Quantity: 1, MonthlyEst: "$16.43" },
      { Id: "EbsStorage", Type: "AWS::EC2::Volume (4x 100GB gp3)", Quantity: 4, MonthlyEst: "$32.00" }
    ],
    replacements: [
      { legacy: "4x c6i.2xlarge Dedicated EC2 Instances ($992.80/mo)", newService: "AWS Lambda Event-Driven Execution ($6.00/mo)", rationale: "Serverless execution executes strictly per task, saving 99% during idle periods." },
      { legacy: "Application Load Balancer ($16.43/mo)", newService: "Amazon API Gateway HTTP API ($1.00/mo)", rationale: "Eliminates baseline hourly charges for lightweight queue dispatching." },
      { legacy: "Always-on 400GB EBS Volumes ($32.00/mo)", newService: "Amazon S3 Ephemeral Staging ($1.50/mo)", rationale: "Payloads stored in cheap object storage with lifecycle expiration." }
    ],
    cfnSnippet: `AWSTemplateFormatVersion: '2010-09-09'
Description: 'Cost-Optimized Worker Queue (Budget Compliant)'
Resources:
  JobQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: VideoRenderQueue

  ProcessorFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: VideoProcessor
      Runtime: python3.12
      Handler: render.handler
      MemorySize: 2048
      Timeout: 120`
  },
  "3": {
    id: "SCENARIO_3",
    name: "Documentation Site with Accidental NAT",
    prompt: "Deploy a documentation website with S3 and CloudFront, but agent added private VPC NAT Gateways for internal CI/CD.",
    defaultBudget: 15,
    unbudgetedCost: 66.90,
    optimizedCost: 10.50,
    resources: [
      { Id: "StaticAssetsBucket", Type: "AWS::S3::Bucket", Quantity: 1, MonthlyEst: "$1.20" },
      { Id: "UnnecessaryNatGateways", Type: "AWS::EC2::NatGateway", Quantity: 2, MonthlyEst: "$65.70" }
    ],
    replacements: [
      { legacy: "2x Unnecessary NAT Gateways ($65.70/mo)", newService: "Direct CloudFront Origin Access Control ($0.00/mo)", rationale: "Public static websites need zero NAT Gateways; OAC secures the S3 origin directly." }
    ],
    cfnSnippet: `AWSTemplateFormatVersion: '2010-09-09'
Description: 'Zero-NAT Static Site (Budget Compliant)'
Resources:
  DocsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: company-docs-site

  CdnDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Enabled: true
        DefaultRootObject: index.html`
  },
  "4": {
    id: "SCENARIO_4",
    name: "Provisioned IOPS & Idle Elastic IPs",
    prompt: "Deploy a caching node with 10,000 IOPS dedicated volume and a pool of reserved public IP addresses.",
    defaultBudget: 60,
    unbudgetedCost: 743.89,
    optimizedCost: 10.50,
    resources: [
      { Id: "OverprovisionedDisk", Type: "AWS::EC2::Volume (io2 10k IOPS)", Quantity: 1, MonthlyEst: "$662.50" },
      { Id: "ReservedPublicIpv4Pool", Type: "AWS::EC2::EIP (5x Idle)", Quantity: 5, MonthlyEst: "$18.25" },
      { Id: "CacheHostInstance", Type: "AWS::EC2::Instance (t3.large)", Quantity: 1, MonthlyEst: "$63.14" }
    ],
    replacements: [
      { legacy: "Dedicated io2 10,000 IOPS ($662.50/mo)", newService: "Standard gp3 EBS (3,000 Free Baseline IOPS) ($8.00/mo)", rationale: "Standard gp3 delivers sub-millisecond latencies for 99% lower cost." },
      { legacy: "5x Idle Unattached Elastic IPs ($18.25/mo)", newService: "Released Idle IPv4 Pool ($0.00/mo)", rationale: "AWS charges $0.005/hr per idle public IPv4 address; unused addresses released." }
    ],
    cfnSnippet: `AWSTemplateFormatVersion: '2010-09-09'
Description: 'Optimized Storage & Address Allocation'
Resources:
  StandardDisk:
    Type: AWS::EC2::Volume
    Properties:
      VolumeType: gp3
      Size: 100
      Iops: 3000`
  },
  "5": {
    id: "SCENARIO_5",
    name: "Optimal Serverless App",
    prompt: "Deploy a lightweight REST microservice with on-demand persistence and HTTP gateway.",
    defaultBudget: 50,
    unbudgetedCost: 9.00,
    optimizedCost: 9.00,
    resources: [
      { Id: "PublicHttpEndpoint", Type: "AWS::ApiGateway::HttpApi", Quantity: 1, MonthlyEst: "$1.00" },
      { Id: "OrderProcessorFunctions", Type: "AWS::Lambda::Function", Quantity: 2, MonthlyEst: "$5.00" },
      { Id: "OrdersStateStore", Type: "AWS::DynamoDB::Table (Pay-per-request)", Quantity: 1, MonthlyEst: "$3.00" }
    ],
    replacements: [],
    cfnSnippet: `AWSTemplateFormatVersion: '2010-09-09'
Description: 'Native Serverless Architecture (Verified Optimal)'
Resources:
  Api:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      ProtocolType: HTTP
  Handler:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.12`
  }
};

// DOM Elements
const scenarioSelect = document.getElementById("scenarioSelect");
const budgetSlider = document.getElementById("budgetSlider");
const budgetValue = document.getElementById("budgetValue");
const toolToggle = document.getElementById("toolToggle");
const promptText = document.getElementById("promptText");
const candidateJson = document.getElementById("candidateJson");
const executionBadge = document.getElementById("executionBadge");
const verdictCard = document.getElementById("verdictCard");
const candidateCost = document.getElementById("candidateCost");
const finalCost = document.getElementById("finalCost");
const savingsVal = document.getElementById("savingsVal");
const replacementsContainer = document.getElementById("replacementsContainer");
const templateCode = document.getElementById("templateCode");
const copyBtn = document.getElementById("copyBtn");

function updateDashboard() {
  const scKey = scenarioSelect.value;
  const sc = SCENARIOS[scKey];
  const budget = parseFloat(budgetSlider.value);
  const isToolOn = toolToggle.checked;

  budgetValue.textContent = `$${budget.toFixed(2)} / month`;
  promptText.textContent = `"${sc.prompt}"`;
  candidateJson.textContent = JSON.stringify(sc.resources, null, 2);
  templateCode.textContent = sc.cfnSnippet;

  const candidateSpend = sc.unbudgetedCost;
  candidateCost.textContent = `$${candidateSpend.toFixed(2)}/mo`;

  if (!isToolOn) {
    // TOOL IS OFF: Base Agent Blind Run
    executionBadge.textContent = "TOOL OFF (BLIND)";
    executionBadge.className = "badge badge-danger";

    const overage = Math.max(0, candidateSpend - budget);
    const overagePct = ((overage / budget) * 100).toFixed(0);

    verdictCard.className = "verdict-banner banner-blocked";
    verdictCard.innerHTML = `
      <span class="badge" style="background: rgba(239, 68, 68, 0.2); color: #F87171; width: fit-content;">⚠️ RUNAWAY BILL SHOCK</span>
      <h3 class="banner-title text-red">Deployment Blindly Approved!</h3>
      <p class="banner-desc">The unaugmented base agent has zero cost awareness. It marked this unbudgeted stack as ready for AWS deployment.</p>
      <p style="margin-top: 8px; font-weight: 700; color: #FCA5A5;">Exceeds budget by $${overage.toFixed(2)}/mo (${overagePct}% cost overrun)!</p>
    `;

    finalCost.textContent = `$${candidateSpend.toFixed(2)}/mo`;
    finalCost.className = "cost-val text-red";
    savingsVal.textContent = "$0.00 (0%)";
    savingsVal.className = "cost-val text-muted";

    replacementsContainer.innerHTML = `
      <div class="replacement-item" style="border-left-color: #EF4444;">
        <p style="color: #FCA5A5;">No architectural replacements generated. Agent lacks evaluate_aws_cost_circuit_breaker tool.</p>
      </div>
    `;
  } else {
    // TOOL IS ON: Protected Agent
    if (candidateSpend > budget) {
      // Circuit Tripped
      executionBadge.textContent = "CIRCUIT TRIPPED & RESOLVED";
      executionBadge.className = "badge badge-aws";

      const savings = candidateSpend - sc.optimizedCost;
      const pctSavings = ((savings / candidateSpend) * 100).toFixed(1);

      verdictCard.className = "verdict-banner banner-passed";
      verdictCard.innerHTML = `
        <span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #34D399; width: fit-content;">🛡️ CIRCUIT TRIPPED & RE-ARCHITECTED</span>
        <h3 class="banner-title text-green">Runaway Deployment Intercepted!</h3>
        <p class="banner-desc">The <code>evaluate_aws_cost_circuit_breaker</code> tool blocked deployment ($${candidateSpend.toFixed(2)} > $${budget.toFixed(2)}). Synthesized Serverless alternative within budget.</p>
      `;

      finalCost.textContent = `$${sc.optimizedCost.toFixed(2)}/mo`;
      finalCost.className = "cost-val text-green";
      savingsVal.textContent = `$${savings.toFixed(2)} (${pctSavings}%)`;
      savingsVal.className = "cost-val text-blue";

      // Render replacements
      replacementsContainer.innerHTML = sc.replacements.map(rep => `
        <div class="replacement-item">
          <div class="rep-header">
            <span class="rep-legacy">${rep.legacy}</span>
            <span class="rep-new">${rep.newService}</span>
          </div>
          <p class="rep-rationale">${rep.rationale}</p>
        </div>
      `).join("");
    } else {
      // Clean Pass (Within Budget)
      executionBadge.textContent = "BUDGET VERIFIED";
      executionBadge.className = "badge badge-challenge";

      verdictCard.className = "verdict-banner banner-passed";
      verdictCard.innerHTML = `
        <span class="badge" style="background: rgba(56, 189, 248, 0.2); color: #38BDF8; width: fit-content;">🟢 BUDGET VERIFIED</span>
        <h3 class="banner-title text-blue">Clean Serverless Architecture Approved</h3>
        <p class="banner-desc">Projected cost of $${candidateSpend.toFixed(2)}/mo is below the $${budget.toFixed(2)}/mo budget ceiling. Zero false alarms.</p>
      `;

      finalCost.textContent = `$${candidateSpend.toFixed(2)}/mo`;
      finalCost.className = "cost-val text-green";
      savingsVal.textContent = "$0.00 (Optimal)";
      savingsVal.className = "cost-val text-muted";

      replacementsContainer.innerHTML = `
        <div class="replacement-item" style="border-left-color: #38BDF8;">
          <p style="color: #93C5FD;">Workload is already optimal. No replacements required.</p>
        </div>
      `;
    }
  }
}

// Event Listeners
scenarioSelect.addEventListener("change", (e) => {
  budgetSlider.value = SCENARIOS[e.target.value].defaultBudget;
  updateDashboard();
});
budgetSlider.addEventListener("input", updateDashboard);
toolToggle.addEventListener("change", updateDashboard);

copyBtn.addEventListener("click", () => {
  navigator.clipboard.writeText(templateCode.textContent).then(() => {
    copyBtn.textContent = "Copied!";
    setTimeout(() => { copyBtn.textContent = "Copy Snippet"; }, 2000);
  });
});

// Initial Render
updateDashboard();
