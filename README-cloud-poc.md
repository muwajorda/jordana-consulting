# Cloud POC README

This document describes how to use the cloud POC scaffold added to the branch `cloud-poc-nfcore-rnaseq`.

Defaults chosen for this scaffold:
- AWS Region: us-east-1
- PDF engine: reportlab (pure Python)
- Nextflow executor: AWS Batch (profile `awsbatch` in nextflow/nextflow.config)

Quick local test (no AWS required)
1. Install Python deps: `pip install -r dev/requirements.txt`
2. Ensure Nextflow is installed on your machine (Nextflow is a Java JVM tool): https://www.nextflow.io/
3. From repository root, run a dry local Nextflow run (use the example samplesheet):
   nextflow run nextflow/main.nf --samplesheet samples/example_samplesheet.csv --outdir ./local_results -profile local
   (This will attempt to call nf-core/rnaseq; for an offline dry-run you can use `-stub` or `-resume` as needed.)

Cloud deployment notes (read carefully before provisioning)
1. Open `infra/turnkey_production_stack.yaml` and replace placeholders for bucket names and subnets. The template will create S3 buckets, an SQS queue, and AWS Batch scaffolding.
2. Upload the CloudFormation template via the AWS Console or CLI into us-east-1.
3. After stack creation, update environment variables for the Lambda and webhook with the created Resource ARNs / URLs.

Security & compliance
- This scaffold intentionally contains NO secrets in source control. You must configure the Stripe signing secret, AWS credentials, and any dbGaP/GDC tokens as encrypted environment variables (e.g., via AWS Secrets Manager or Systems Manager Parameter Store).
- Controlled-access datasets (TCGA raw FASTQs via GDC controlled access) require dbGaP authorization and separate provisioning steps. The scaffold does not bypass any access controls.

Limitations
- The AWS Batch resource in the CloudFormation is a simplified example and lacks VPC/subnet/AMI/instance type tuning. Do not use it as-is in production.
- The webhook and lambda functions operate in DRY_RUN mode by default. Flip DRY_RUN to false only after you validate IAM roles and permissions.

Next steps
- Provide AWS account-specific values (subnets, VPC, bucket name prefixes) so we can enrich the CloudFormation template.
- If you want, I can open a PR now with these files and a checklist of values you must provide before creating resources.
