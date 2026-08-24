"""
FastAPI Backend for Jordana Consulting Interactive Demos
Serves validation, extraction, and booking endpoints
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
import json
import csv
from io import StringIO, BytesIO
import boto3
from datetime import datetime
import os
import logging

# Initialize FastAPI app
app = FastAPI(
    title="Jordana Consulting API",
    description="Field-Ready Cloud Infrastructure & Data Pipeline Services",
    version="1.0.0"
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AWS Bedrock client (for AI extraction)
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))

# ============================================================================
# Pydantic Models - FHIR Schemas
# ============================================================================

class PatientSchema(BaseModel):
    """FHIR Patient Resource Schema"""
    resourceType: str = "Patient"
    id: str
    identifier: List[Dict[str, str]]
    name: List[Dict[str, str]]
    telecom: Optional[List[Dict[str, str]]]
    gender: str
    birthDate: str
    address: Optional[List[Dict[str, str]]]
    
    @validator('resourceType')
    def validate_resource_type(cls, v):
        if v != "Patient":
            raise ValueError('resourceType must be "Patient"')
        return v
    
    @validator('gender')
    def validate_gender(cls, v):
        if v not in ['male', 'female', 'other', 'unknown']:
            raise ValueError('gender must be one of: male, female, other, unknown')
        return v


class ObservationSchema(BaseModel):
    """FHIR Observation Resource Schema"""
    resourceType: str = "Observation"
    id: str
    status: str
    category: List[Dict[str, str]]
    code: Dict[str, Any]
    subject: Dict[str, str]
    effectiveDateTime: str
    value: Optional[Dict[str, Any]]
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['registered', 'preliminary', 'final', 'amended', 'cancelled', 'entered-in-error', 'unknown']
        if v not in valid_statuses:
            raise ValueError(f'status must be one of: {", ".join(valid_statuses)}')
        return v


class SpecimenSchema(BaseModel):
    """FHIR Specimen Resource Schema"""
    resourceType: str = "Specimen"
    id: str
    identifier: List[Dict[str, str]]
    type: Dict[str, Any]
    subject: Dict[str, str]
    collectionDateTime: str
    processing: Optional[List[Dict[str, Any]]]
    container: Optional[List[Dict[str, Any]]]
    
    @validator('resourceType')
    def validate_resource_type(cls, v):
        if v != "Specimen":
            raise ValueError('resourceType must be "Specimen"')
        return v


# ============================================================================
# Booking & Contact Models
# ============================================================================

class BookingRequest(BaseModel):
    """Architecture Review Booking Request"""
    first_name: str
    last_name: str
    email: EmailStr
    company: str
    industry: str
    challenge: str
    
    class Config:
        schema_extra = {
            "example": {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane@example.com",
                "company": "MedTech Inc",
                "industry": "Healthcare",
                "challenge": "Need FHIR-compliant validation for patient records"
            }
        }


class ValidationResponse(BaseModel):
    """Response for data validation requests"""
    valid: bool
    schema_type: str
    errors: List[Dict[str, str]] = []
    warnings: List[str] = []
    processed_records: int
    timestamp: str


class ExtractionResponse(BaseModel):
    """Response for AI text extraction"""
    success: bool
    extracted_data: Dict[str, Any]
    confidence_score: float
    source_text_length: int
    processing_time_ms: int
    metadata: Dict[str, str]


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Jordana Consulting API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Data Validation Endpoints
# ============================================================================

@app.post("/api/validate", response_model=ValidationResponse)
async def validate_data(file: UploadFile = File(...), schema: str = "Patient") -> ValidationResponse:
    """
    Validate uploaded CSV/JSON against FHIR schema
    
    Args:
        file: CSV or JSON file to validate
        schema: FHIR schema type (Patient, Observation, Specimen)
    
    Returns:
        ValidationResponse with validation results
    """
    try:
        # Read file content
        content = await file.read()
        
        # Determine file type and parse
        if file.filename.endswith('.json'):
            data = json.loads(content.decode('utf-8'))
            records = data if isinstance(data, list) else [data]
        elif file.filename.endswith('.csv'):
            text = content.decode('utf-8')
            reader = csv.DictReader(StringIO(text))
            records = list(reader)
        else:
            raise ValueError("File must be CSV or JSON")
        
        # Select schema validator
        schema_map = {
            "Patient": PatientSchema,
            "Observation": ObservationSchema,
            "Specimen": SpecimenSchema
        }
        
        if schema not in schema_map:
            raise ValueError(f"Unknown schema: {schema}. Must be one of: {', '.join(schema_map.keys())}")
        
        SchemaClass = schema_map[schema]
        
        # Validate records
        errors = []
        valid_count = 0
        
        for idx, record in enumerate(records):
            try:
                SchemaClass(**record)
                valid_count += 1
            except Exception as e:
                errors.append({
                    "record_index": idx,
                    "error": str(e)
                })
        
        response = ValidationResponse(
            valid=len(errors) == 0,
            schema_type=schema,
            errors=errors[:100],  # Limit to 100 errors
            warnings=[] if valid_count == len(records) else [f"{len(errors)} records failed validation"],
            processed_records=len(records),
            timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(f"Validation completed: {valid_count}/{len(records)} records valid")
        return response
        
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# AI Text Extraction Endpoints
# ============================================================================

@app.post("/api/extract", response_model=ExtractionResponse)
async def extract_text(request: Dict[str, str]):
    """
    Extract structured data from unstructured clinical text using AWS Bedrock Claude 3
    
    Args:
        text: Clinical or unstructured text
    
    Returns:
        ExtractionResponse with extracted data
    """
    try:
        text = request.get("text", "")
        
        if not text or len(text.strip()) == 0:
            raise ValueError("Text input cannot be empty")
        
        # Create prompt for Claude 3
        prompt = f"""Extract clinical data from the following text and return as valid JSON.
Extract the following fields if present: patient_name, diagnosis, treatment, lab_values, medications, observations.

Text:
{text}

Return ONLY valid JSON, no other text."""
        
        # Call Bedrock API (mocked here - replace with real call when AWS credentials available)
        start_time = datetime.utcnow()
        
        # Mock extraction for demo (replace with actual Bedrock call when configured)
        extracted_data = {
            "patient_name": "John Doe",
            "diagnosis": ["Hypertension", "Type 2 Diabetes"],
            "treatment": "Antihypertensive + Metformin",
            "lab_values": {
                "blood_pressure": "140/90 mmHg",
                "glucose": "145 mg/dL",
                "hemoglobin_a1c": "7.2%"
            },
            "medications": ["Lisinopril", "Metformin"],
            "observations": "Patient responding well to current treatment regimen"
        }
        
        # Real Bedrock call (uncomment when configured):
        # try:
        #     response = bedrock_runtime.invoke_model(
        #         modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        #         body=json.dumps({
        #             "anthropic_version": "bedrock-2023-06-01",
        #             "max_tokens": 1024,
        #             "messages": [
        #                 {
        #                     "role": "user",
        #                     "content": prompt
        #                 }
        #             ]
        #         })
        #     )
        #     result = json.loads(response['body'].read())
        #     extracted_data = json.loads(result['content'][0]['text'])
        # except Exception as e:
        #     logger.error(f"Bedrock API error: {str(e)}")
        #     # Fall back to mock response
        #     pass
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return ExtractionResponse(
            success=True,
            extracted_data=extracted_data,
            confidence_score=0.95,
            source_text_length=len(text),
            processing_time_ms=int(processing_time),
            metadata={
                "model": "Claude 3",
                "source": "AWS Bedrock",
                "extracted_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Extraction error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Booking Endpoint
# ============================================================================

@app.post("/api/booking")
async def create_booking(booking: BookingRequest):
    """
    Create an architecture review booking request
    
    Args:
        booking: BookingRequest with contact and challenge details
    
    Returns:
        Confirmation with booking details
    """
    try:
        # In production, save to database (DynamoDB, PostgreSQL, etc.)
        booking_data = {
            "id": f"booking_{datetime.utcnow().timestamp()}",
            "first_name": booking.first_name,
            "last_name": booking.last_name,
            "email": booking.email,
            "company": booking.company,
            "industry": booking.industry,
            "challenge": booking.challenge,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending_review"
        }
        
        # TODO: Save to database
        # TODO: Send confirmation email
        
        logger.info(f"Booking created: {booking_data['id']} from {booking.email}")
        
        return {
            "success": True,
            "message": "Architecture review request submitted successfully",
            "booking_id": booking_data["id"],
            "next_steps": "We will contact you within 24 hours to schedule your personalized review.",
            "confirmation_email": booking.email,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Booking error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Terraform Template Endpoints
# ============================================================================

@app.get("/api/terraform/templates")
async def list_terraform_templates():
    """List available Terraform templates"""
    return {
        "templates": [
            {
                "name": "AWS VPC + Security Groups",
                "file": "main.tf",
                "lines": 250,
                "description": "Complete VPC setup with public/private subnets and security groups"
            },
            {
                "name": "RDS Aurora PostgreSQL",
                "file": "database.tf",
                "lines": 120,
                "description": "Multi-AZ Aurora PostgreSQL cluster with automatic failover"
            },
            {
                "name": "S3 Data Lake + IAM",
                "file": "storage.tf",
                "lines": 180,
                "description": "Encrypted S3 buckets with versioning and lifecycle policies"
            },
            {
                "name": "Lambda Validation Service",
                "file": "lambda.tf",
                "lines": 95,
                "description": "Serverless Pydantic validation Lambda function"
            }
        ]
    }


@app.get("/api/terraform/template/{template_name}")
async def get_terraform_template(template_name: str):
    """Get specific Terraform template content"""
    templates = {
        "main.tf": """# AWS VPC Configuration
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "jordana-vpc"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet-${count.index + 1}"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "private-subnet-${count.index + 1}"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "jordana-igw"
  }
}

# Security Group for Application
resource "aws_security_group" "app" {
  name   = "jordana-app-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "jordana-app-sg"
  }
}

# Security Group for Database
resource "aws_security_group" "db" {
  name   = "jordana-db-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "jordana-db-sg"
  }
}""",
        "database.tf": """# RDS Aurora PostgreSQL Cluster
resource "aws_rds_cluster" "main" {
  cluster_identifier              = "jordana-aurora-cluster"
  engine                          = "aurora-postgresql"
  engine_version                  = "14.6"
  database_name                   = var.db_name
  master_username                 = var.db_user
  master_password                 = var.db_password
  backup_retention_period         = 30
  preferred_backup_window         = "03:00-04:00"
  preferred_maintenance_window    = "mon:04:00-mon:05:00"
  multi_az                        = true
  storage_encrypted               = true
  kms_key_id                      = aws_kms_key.rds.arn
  skip_final_snapshot             = false
  final_snapshot_identifier       = "jordana-aurora-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
  enabled_cloudwatch_logs_exports = ["postgresql"]

  db_subnet_group_name            = aws_db_subnet_group.main.name
  vpc_security_group_ids          = [aws_security_group.db.id]

  tags = {
    Name = "jordana-aurora"
  }
}

# RDS Cluster Instances
resource "aws_rds_cluster_instance" "main" {
  count              = 2
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = "db.t4g.medium"
  engine              = aws_rds_cluster.main.engine
  engine_version      = aws_rds_cluster.main.engine_version
  publicly_accessible = false

  performance_insights_enabled    = true
  monitoring_interval             = 60
  monitoring_role_arn             = aws_iam_role.rds_monitoring.arn

  tags = {
    Name = "jordana-aurora-instance-${count.index + 1}"
  }
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "jordana-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "jordana-db-subnet-group"
  }
}

# KMS Key for RDS Encryption
resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name = "jordana-rds-key"
  }
}"""
    }
    
    content = templates.get(template_name, "Template not found")
    
    return {
        "template_name": template_name,
        "content": content,
        "lines": len(content.split('\n')),
        "language": "hcl"
    }


# ============================================================================
# Root endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "service": "Jordana Consulting API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "validation": "/api/validate",
            "extraction": "/api/extract",
            "booking": "/api/booking",
            "terraform": "/api/terraform/templates",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
