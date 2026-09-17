StockFlow — Supply Chain Visibility Platform
Project Plan
1. Overview

What this is: A multi-location supply chain visibility platform tracking inventory and order flow across warehouses, with real-time low-stock alerting and full operational visibility for warehouse operators.

Business problem solved: Retailers and distributors operating across multiple warehouses lack unified, real-time visibility into inventory levels and order status. This leads to stockouts, delayed fulfillment, and poor operational decision-making. StockFlow gives operators a single, real-time view across all locations.

Why this project: No native AWS service solves this — every architecture decision is genuinely defensible. The domain (orders, inventory, warehouses) is universally understandable to any interviewer without needing context-setting, so conversation time goes to architecture depth, not explaining the premise.

Primary goals of building this:

Fill the "beyond 3-tier" AWS service breadth gap (EKS/Kubernetes hands-on)
Produce a genuine, defensible portfolio project with real trade-off decisions
Generate authentic debugging/troubleshooting stories through deliberate break-and-fix cycles
Cover all 8 core AWS services (EKS, EC2, VPC, IAM, S3, RDS, Route53, EBS) plus the Well-Architected Framework's 5 pillars
2. Architecture Decisions (Locked In)
Tiers & Data Flow
Presentation: Containerized React frontend pods on EKS, private subnet
Application: EKS worker nodes (EC2 under the hood), private subnet
Database: RDS Postgres, private subnet

Traffic flow: Browser → ALB (public subnet) → AWS Load Balancer Controller (syncs target groups from Ingress/Service) → pod on private-subnet node → RDS via security group rule (port 5432, source = node SG only)

Outbound access — no NAT Gateway: VPC Gateway Endpoint (S3) + Interface Endpoints (ECR api/dkr, Secrets Manager, CloudWatch Logs, EKS API). Nodes have zero path to the public internet, since the app has no external third-party dependency. Chosen over NAT Gateway for stronger security posture and lower cost.

Scaling: HPA scales pod replicas on CPU/memory → if no room, pods go Pending → Cluster Autoscaler provisions new nodes via ASG.

Data Model

warehouses table

warehouse_id — Primary key (tenant_id)
name, region — Basic metadata

inventory_items table

item_id — Primary key
warehouse_id — Tenant isolation (FK)
sku — Stock-keeping unit identifier
quantity_on_hand — Current stock level
reorder_threshold — Triggers low-stock alert
last_updated — Timestamp

orders table

order_id — Primary key
warehouse_id — Tenant isolation (FK)
customer_ref — Order origin reference
status — pending / fulfilled / shipped / cancelled
created_at, updated_at — Timestamps
Alert Logic

Rule-based, not ML: flag inventory_items where quantity_on_hand < reorder_threshold. Stretch version: estimate days-until-stockout using recent order velocity for that SKU, rather than a static threshold alone.

Multi-Tenancy Model

Pool model — shared database, shared schema, warehouse_id column with row-level filtering enforced at the application/ORM layer. Postgres Row-Level Security (RLS) as a defense-in-depth stretch goal.

3. Technology Stack
Backend: Python, FastAPI — chosen for native async support, automatic OpenAPI/Swagger docs, and built-in request validation via Pydantic
Database: RDS Postgres
Caching: ElastiCache (Redis) — cache-aside pattern for inventory reads
Frontend: React — clean, modern dashboard UI, not a bare-bones interface
Container orchestration: EKS
IaC: Terraform
CI/CD: GitHub Actions
Container registry: ECR
Observability: CloudWatch Container Insights, CloudWatch Logs, CloudWatch Alarms
Security: IRSA, Secrets Manager, Security Groups, encryption at rest/in transit, CloudTrail
Networking: VPC Endpoints (no NAT Gateway), ALB Ingress, Route53 custom domain
Cost optimization: S3 lifecycle policy → Glacier for fulfilled-order attachments older than 90 days
4. Build Stages
Backend API — REST endpoints: POST /orders, GET /orders/{warehouse_id}, PATCH /orders/{order_id}/status, GET /inventory/{warehouse_id}, GET /inventory/{warehouse_id}/alerts, GET /health
Database Layer — RDS Postgres, 3 tables above, Row-Level Security stretch goal
Caching Layer — ElastiCache Redis, short TTL for inventory reads
Containerize Backend — Dockerfile, multi-stage build
Frontend Dashboard — React app, containerized alongside the backend; orders table + inventory levels + low-stock alerts, with real thought given to layout and visual clarity
Kubernetes Cluster & Networking (Terraform) — VPC (public/private subnets), EKS cluster + node group, IAM OIDC provider, VPC Endpoints
Kubernetes Deploy — ECR push, Deployment/Service/Ingress/ConfigMap/Secret/HPA manifests
Security & Compliance — IRSA, Security Groups, encryption, CloudTrail, Route53 domain
Observability — CloudWatch Container Insights, Logs, Alarms tied to HPA
Cost Optimization — S3 lifecycle → Glacier policy
CI/CD Pipeline — GitHub Actions: lint/test → build → push to ECR → deploy to EKS, OIDC federation for AWS credentials
Break & Debug Cycle — deliberately break 5 things (wrong port, revoked IRSA permission, blocked security group, low memory limit/OOMKill, broken CI YAML), debug without AI help first, log each as "broke X → symptom Y → root cause Z → fixed by W"
Boto3 Companion Scripts — run against StockFlow's own live AWS resources
Interview Narrative — 90-second summary, trade-off answers, debugging stories, full request-flow trace, Well-Architected Framework mapping
5. UI Design Goals

The dashboard should look like a genuine product, not a bare data table — this matters for demoing the project in interviews.

Warehouse selector — switch between warehouses/tenants cleanly (dropdown or tab-based)
Inventory view — clear table or card layout showing SKU, quantity on hand, and reorder threshold, with low-stock items visually flagged (color/badge), not just listed identically to healthy stock
Orders view — status-based grouping or filtering (pending/fulfilled/shipped/cancelled), not one flat unsorted list
Alerts panel — a dedicated, prominent section surfacing items below reorder threshold — this is the dashboard's actual value proposition, so it shouldn't be buried
Clean, modern visual style — sensible spacing, a coherent color palette, readable typography
Responsive layout — should hold up reasonably on a laptop screen at minimum

This isn't meant to be a design showcase — it's meant to look competently built, since a rough UI can undercut an otherwise strong architecture story in a live demo.

6. Build Methodology
Design decisions are made here (Stage 0), before any code generation
Claude Code generates implementation for each stage
Every generated file is read and understood before being applied
Once each stage works, deliberately break something in it and debug without AI assistance first (Stage 12)
Final deliverable: a working, documented, publicly-hosted GitHub repo with a clear README
7. Success Criteria
All 8 core AWS services genuinely used and explainable
Well-Architected Framework's 5 pillars each have a concrete example in this project
At least 3 real debugging stories from the break/debug cycle
Boto3 scripts run successfully against real project resources
Can explain the full request-flow trace end to end from memory
Can defend every major trade-off without notes
Dashboard looks like a genuine, demo-ready product — not a raw data table