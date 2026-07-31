import streamlit as st
import pandas as pd
import json
from datetime import datetime
import math
import random

# Initialize session states
if "assessments" not in st.session_state:
    st.session_state.assessments = []

if "active_workloads" not in st.session_state:
    st.session_state.active_workloads = ["scRNA-seq (Single Cell)", "Oncology Panels (Somatic Mutect2)"]

st.set_page_config(page_title="Biotech Readiness & Workflow Engine", layout="wide")

st.title("🧬 Enterprise Bioinformatics Infrastructure & Workflow Engine")
st.caption("Production-grade Nextflow DSL2 / Snakemake orchestrators, Cloud resource breakdown & Interactive data ingester")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 Readiness Assessment", 
    "⚡ Pipeline Engine & Samplesheet Ingester", 
    "📊 Statistical Analysis & Live DEG",
    "☁️ Cloud Resources & Runtime Sizing", 
    "📅 Week 5 & 6 Roadmap & Logs"
])

# ---------------------------------------------------------
# TAB 1: READINESS ASSESSMENT
# ---------------------------------------------------------
with tab1:
    with st.form("assessment_form"):
        st.markdown("#### 1. Company Profile & Scope")
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name", value="AstraOmics Bio")
            contact_email = st.text_input("Contact Email", value="founder@astraomics.com")
            cloud_provider = st.selectbox("Cloud Provider", ["AWS (Amazon Web Services)", "GCP (Google Cloud Platform)", "Hybrid / On-Prem"])
        with col2:
            team_size = st.number_input("Bioinformatics Headcount", min_value=0, max_value=50, value=3)
            stage = st.selectbox("Company Stage", ["Seed", "Series A", "Series B+", "Academic / Non-Profit"])
            primary_engine = st.selectbox("Workflow Orchestrator", ["Nextflow (nf-core)", "Snakemake", "Cromwell / WDL"])

        st.markdown("#### 2. Omics Modalities & Workloads")
        data_types = st.multiselect(
            "Primary Workloads",
            [
                "scRNA-seq (Single Cell)", 
                "Oncology Panels (Somatic Mutect2)", 
                "Bulk RNA-seq (nf-core/rnaseq)", 
                "Preventive Genomics WGS", 
                "cfDNA / Fragmentomics"
            ],
            default=["scRNA-seq (Single Cell)", "Oncology Panels (Somatic Mutect2)"]
        )
        monthly_gb = st.number_input("Monthly Data Ingestion (GB)", value=1200, step=100)

        st.markdown("#### 3. Infrastructure Checklist")
        col3, col4 = st.columns(2)
        with col3:
            uses_containers = st.checkbox("Uses Containers (Docker / Singularity)", value=True)
            has_cold_archive = st.checkbox("Cold Storage Tiering Configured", value=False)
        with col4:
            uses_spot_instances = st.checkbox("Utilizes Spot / Preemptible Instances", value=True)
            has_ci_cd = st.checkbox("CI/CD Integration", value=False)

        submitted = st.form_submit_button("Run Assessment & Compute Infrastructure Sizing 🔥")

    if submitted:
        st.session_state.active_workloads = data_types
        omics_score = 4 if len(data_types) > 1 else 2
        infra_score = 4 if uses_containers and uses_spot_instances else 2
        team_score = min(5, max(1, team_size * 2))

        st.session_state.assessments.append({
            "Company": company_name,
            "Stage": stage,
            "Cloud": cloud_provider.split(" ")[0],
            "Engine": primary_engine,
            "Omics Score": f"{omics_score}/5",
            "Infra Score": f"{infra_score}/5",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

        st.success("✅ Assessment Computed! Review generated pipelines, cloud sizing, and samplesheet parser.")

# ---------------------------------------------------------
# TAB 2: PIPELINE ENGINE & SAMPLESHEET INGESTER
# ---------------------------------------------------------
with tab2:
    st.markdown("### ⚡ Production Pipeline Templates & Data Ingestion")
    
    col_upload, col_select = st.columns([1, 1])
    with col_upload:
        st.markdown("##### 📥 Upload Your Custom Samplesheet CSV")
        uploaded_ss = st.file_uploader("Upload CSV containing sample metadata", type=["csv", "tsv", "txt"])
    
    with col_select:
        st.markdown("##### ⚙️ Engine Parameters")
        chosen_engine = st.selectbox("Pipeline Framework", ["Nextflow DSL2", "Snakemake"])
        target_modality = st.selectbox("Workflow Target", ["Bulk RNA-seq", "Somatic Oncology (Mutect2)", "scRNA-seq (10x Chromium)"])

    st.markdown("---")

    default_ss = """sample_id,omics_modality,experiment_type,data_type,file_type,fastq_1,fastq_2
SAMPLE_01_CTRL,Bulk RNA-seq,Illumina NovaSeq PE150,Raw Transcriptomics,FASTQ GZIP,s3://my-bio-bucket/fastqs/S01_R1.fq.gz,s3://my-bio-bucket/fastqs/S01_R2.fq.gz
SAMPLE_02_TRT,Bulk RNA-seq,Illumina NovaSeq PE150,Raw Transcriptomics,FASTQ GZIP,s3://my-bio-bucket/fastqs/S02_R1.fq.gz,s3://my-bio-bucket/fastqs/S02_R2.fq.gz
PATIENT_01_T,Somatic Panel,Hybrid Capture WES,Targeted DNA,Aligned BAM,s3://my-bio-bucket/bams/P01_Tumor.bam,s3://my-bio-bucket/bams/P01_Normal.bam"""

    if uploaded_ss is not None:
        try:
            sep = "," if uploaded_ss.name.endswith(".csv") else "\t"
            df_ss = pd.read_csv(uploaded_ss, sep=sep)
            st.success(f"✅ Successfully ingested `{uploaded_ss.name}` ({len(df_ss)} samples registered)")
            st.dataframe(df_ss, use_container_width=True)
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.info("💡 Showing default dynamic sample sheet format below. Upload your own CSV above or download the example template.")
        st.code(default_ss, language="csv")
        
        # FEATURE 1: Downloadable synthetic samplesheet button
        st.download_button(
            label="📥 Download Template samplesheet.csv",
            data=default_ss,
            file_name="example_samplesheet.csv",
            mime="text/csv"
        )

    st.markdown("#### 📜 Production Pipeline Code")

    if chosen_engine == "Nextflow DSL2":
        nf_code = """/*
 * Nextflow DSL2 Production Pipeline: Alignment & Variant/Expression Quantification
 */
nextflow.enable.dsl=2

params.samplesheet = "$projectDir/samplesheet.csv"
params.genome_fasta = "s3://ngi-igenomes/igenomes/Homo_sapiens/NCBI/GRCh38/Sequence/WholeGenomeFasta/genome.fa"
params.star_index   = "s3://ngi-igenomes/igenomes/Homo_sapiens/NCBI/GRCh38/Sequence/STARIndex/"
params.outdir       = "s3://my-company-data-lake/results/"

process FASTQC {
    tag "$sample_id"
    container 'quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0'
    cpus 2
    memory '8 GB'

    input:
    tuple val(sample_id), path(fastq_1), path(fastq_2)

    output:
    path "*_fastqc.zip", emit: qc_reports

    script:
    \"\"\"
    fastqc -t ${task.cpus} ${fastq_1} ${fastq_2}
    \"\"\"
}

process STAR_ALIGN {
    tag "$sample_id"
    container 'quay.io/biocontainers/star:2.7.10a--h9ee0642_0'
    cpus 16
    memory '32 GB'
    publishDir "${params.outdir}/alignments", mode: 'copy'

    input:
    tuple val(sample_id), path(fastq_1), path(fastq_2)

    output:
    tuple val(sample_id), path("${sample_id}.Aligned.sortedByCoord.out.bam"), emit: bam

    script:
    \"\"\"
    STAR --genomeDir ${params.star_index} \\
         --readFilesIn ${fastq_1} ${fastq_2} \\
         --readFilesCommand zcat \\
         --runThreadN ${task.cpus} \\
         --outSAMtype BAM SortedByCoordinate \\
         --outFileNamePrefix ${sample_id}.
    \"\"\"
}

workflow {
    samples_ch = Channel
        .fromPath(params.samplesheet)
        .splitCsv(header: true)
        .map { row -> tuple(row.sample_id, file(row.fastq_1), file(row.fastq_2)) }

    FASTQC(samples_ch)
    STAR_ALIGN(samples_ch)
}"""
        st.code(nf_code, language="groovy")

        # FEATURE 3: Pipeline Configuration Exporter
        with st.expander("⚙️ View nextflow.config / AWS Execution Profile"):
            config_code = """
process {
    executor = 'awsbatch'
    queue    = 'arn:aws:batch:us-east-1:123456789012:job-queue/omics-high-memory'
    
    // Auto-retry on OOM (Out Of Memory) exit codes
    errorStrategy = { task.exitStatus in [137,140] ? 'retry' : 'finish' }
    maxRetries    = 2
    memory        = { 16.GB * task.attempt }
    
    withName: 'STAR_ALIGN' {
        cpus   = 16
        memory = 64.GB
    }
    withName: 'GATK_MUTECT2' {
        cpus   = 32
        memory = 128.GB
    }
}

aws {
    region = 'us-east-1'
    batch {
        cliPath = '/home/ec2-user/miniconda/bin/aws'
    }
}
"""
            st.code(config_code, language="groovy")

    else:
        snake_code = """# Production Snakemake Workflow
SAMPLES = ["SAMPLE_01_CTRL", "SAMPLE_02_TRT"]

rule all:
    input:
        expand("results/alignments/{sample}.bam", sample=SAMPLES),
        expand("results/qc/{sample}_fastqc.html", sample=SAMPLES)

rule fastqc:
    input:
        r1="data/{sample}_R1.fastq.gz",
        r2="data/{sample}_R2.fastq.gz"
    output:
        html="results/qc/{sample}_fastqc.html"
    threads: 2
    resources:
        mem_mb=8000
    container:
        "docker://biocontainers/fastqc:v0.11.9_cv8"
    shell:
        "fastqc -t {threads} -o results/qc/ {input.r1} {input.r2}"

rule star_align:
    input:
        r1="data/{sample}_R1.fastq.gz",
        r2="data/{sample}_R2.fastq.gz",
        index="refs/star_index"
    output:
        bam="results/alignments/{sample}.bam"
    threads: 16
    resources:
        mem_mb=32000
    container:
        "docker://biocontainers/star:2.7.10a"
    shell:
        \"\"\"
        STAR --genomeDir {input.index} \\
             --readFilesIn {input.r1} {input.r2} \\
             --readFilesCommand zcat \\
             --runThreadN {threads} \\
             --outSAMtype BAM SortedByCoordinate \\
             --outFileNamePrefix results/alignments/{wildcards.sample}.
        \"\"\"
"""
        st.code(snake_code, language="python")

# ---------------------------------------------------------
# TAB 3: STATISTICAL ANALYSIS & CSV DEG UPLOADER
# ---------------------------------------------------------
with tab3:
    st.markdown("### 📊 Interactive Volcano Plot & Expression Analysis")
    st.caption("Upload raw gene expression / differential expression CSVs or test with interactive synthetic data.")

    deg_file = st.file_uploader("Upload DEG Results CSV (Columns needed: Gene, log2FC, pvalue)", type=["csv", "tsv", "txt"], key="deg_upload")

    if deg_file is not None:
        try:
            df_deg = pd.read_csv(deg_file)
            st.success("✅ Custom DEG file loaded successfully!")
        except Exception as e:
            st.error(f"Error parsing custom expression file: {e}")
            df_deg = None
    else:
        random.seed(42)
        genes = ["TP53", "EGFR", "BRCA1", "MYC", "KRAS", "VEGFA", "IL6", "TNF", "AKT1", "CDK4", "ESR1", "PTEN", "MET", "BRAF", "PIK3CA"]
        rows = []
        for i in range(120):
            g = genes[i % len(genes)] if i < len(genes) else f"GENE_{i+1}"
            l2fc = round(random.uniform(-4.5, 4.5), 2)
            pval = max(0.00001, random.choices([random.uniform(0.00001, 0.001), random.uniform(0.01, 0.5)], weights=[0.25, 0.75])[0])
            rows.append({"Gene": g, "log2FC": l2fc, "pvalue": pval})
        df_deg = pd.DataFrame(rows)

    if df_deg is not None:
        p_cutoff = st.slider("Significance Cutoff (-log10 p-value)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)
        fc_cutoff = st.slider("Fold-Change Cutoff (|log2FC|)", min_value=0.5, max_value=4.0, value=1.5, step=0.25)

        df_deg["-log10(pvalue)"] = df_deg["pvalue"].apply(lambda p: round(-math.log10(max(p, 1e-10)), 2))
        
        def assign_status(row):
            if row["log2FC"] >= fc_cutoff and row["-log10(pvalue)"] >= p_cutoff:
                return "Upregulated"
            elif row["log2FC"] <= -fc_cutoff and row["-log10(pvalue)"] >= p_cutoff:
                return "Downregulated"
            return "Not Significant"

        df_deg["Status"] = df_deg.apply(assign_status, axis=1)

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Genes", len(df_deg))
        c2.metric("Upregulated", len(df_deg[df_deg["Status"] == "Upregulated"]))
        c3.metric("Downregulated", len(df_deg[df_deg["Status"] == "Downregulated"]))

        st.scatter_chart(df_deg, x="log2FC", y="-log10(pvalue)", color="Status")

        # FEATURE 4: Interactive DEG Gene Search & Filter
        selected_gene = st.text_input("🔍 Search / Filter Specific Gene (e.g. TP53, BRCA1)", value="")
        if selected_gene:
            filtered_df = df_deg[df_deg["Gene"].str.contains(selected_gene, case=False, na=False)]
            st.markdown(f"**Search Results for `{selected_gene}`:**")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            with st.expander("🔍 View All Table Data"):
                st.dataframe(df_deg.head(20), use_container_width=True)

# ---------------------------------------------------------
# TAB 4: CLOUD RESOURCES & RUNTIME SIZING
# ---------------------------------------------------------
with tab4:
    st.markdown("### ☁️ AWS Architecture Connections & Workflow Sizing")
    
    st.markdown("#### 🛠 AWS Cloud Infrastructure Architecture")
    st.info("""
    **Connection & Resource Lifecycle:**
    1. **IAM Role / Access Key:** Nextflow/Snakemake head node authenticates to AWS Batch & Amazon S3.
    2. **S3 Staging Bucket:** FastQ reads & genomic reference files (GRCh38) stage in `s3://company-omics-lake/`.
    3. **AWS Batch Compute Environment:** Spawns EC2 instances (`c5.4xlarge`, `r5.4xlarge`, `r5.8xlarge`) on-demand inside isolated VPC subnets.
    4. **Container Registry:** Pulls biocontainers directly from Amazon ECR / Quay.io.
    5. **AWS CloudWatch:** Captures live stdout/stderr execution logs and memory utilization metrics.
    """)

    st.markdown("#### ⏱ Runtime & Resource Sizing Breakdown per Workflow Stage")
    
    runtime_data = [
        {
            "Pipeline Stage": "1. Quality Control (FastQC / MultiQC)",
            "AWS EC2 Instance": "c5.2xlarge",
            "vCPUs": 8,
            "RAM (GB)": 16,
            "Est. Execution Time (30x WGS / 50M PE Reads)": "20 - 35 mins",
            "Estimated AWS Cost / Sample": "$0.08"
        },
        {
            "Pipeline Stage": "2. Alignment (STAR / BWA-MEM2)",
            "AWS EC2 Instance": "r5.4xlarge",
            "vCPUs": 16,
            "RAM (GB)": 64,
            "Est. Execution Time (30x WGS / 50M PE Reads)": "1.5 - 3.0 hours",
            "Estimated AWS Cost / Sample": "$1.45"
        },
        {
            "Pipeline Stage": "3. Variant Calling / Quantification (Mutect2 / Cell Ranger)",
            "AWS EC2 Instance": "r5.8xlarge",
            "vCPUs": 32,
            "RAM (GB)": 128,
            "Est. Execution Time (30x WGS / 50M PE Reads)": "3.0 - 6.0 hours",
            "Estimated AWS Cost / Sample": "$3.80"
        },
        {
            "Pipeline Stage": "4. Downstream Stats & MultiQC Summary",
            "AWS EC2 Instance": "t3.medium",
            "vCPUs": 2,
            "RAM (GB)": 4,
            "Est. Execution Time (30x WGS / 50M PE Reads)": "10 - 15 mins",
            "Estimated AWS Cost / Sample": "$0.02"
        }
    ]
    
    st.table(pd.DataFrame(runtime_data))

    # FEATURE 2: Dynamic Cohort Cost & Resource Calculator
    st.markdown("#### 💵 Dynamic Cohort Cost Estimator")
    sample_count = st.number_input("Target Sample Cohort Size", min_value=1, max_value=1000, value=25, step=5)

    cost_per_sample = 5.35
    total_cost = sample_count * cost_per_sample
    total_node_hours = sample_count * 7  # Average ~7 hours of processing time per sample

    m1, m2, m3 = st.columns(3)
    m1.metric("Est. Total AWS Cost (Spot)", f"${total_cost:,.2f} USD")
    m2.metric("Total Compute Allocation", f"{total_node_hours:,} vCPU Hours")
    m3.metric("Cost / Sample", f"${cost_per_sample:.2f} USD")

# ---------------------------------------------------------
# TAB 5: WEEK 5 & 6 ROADMAP & HISTORICAL LOGS
# ---------------------------------------------------------
with tab5:
    st.markdown("### 📅 Week 5 & 6 Engineering Roadmap & Client Deliverables")
    
    st.markdown("#### 🔵 Week 5: Pipeline Optimization, Cloud Sizing & Interactive Analysis")
    st.markdown("""
    * **Production Pipeline Syntax Validation:** Verified Nextflow DSL2 and Snakemake orchestrators against standard nf-core and somatic profiling specifications.
    * **Dynamic Sample Sheet & Ingestion Engine:** Implemented user CSV/TSV sample sheet uploading to parse custom file paths (`fastq_1`, `fastq_2`, BAM URIs) on the fly.
    * **Cloud Resource Architecture Sizing:** Mapped AWS EC2 instance tiers (`c5.2xlarge`, `r5.4xlarge`, `r5.8xlarge`), memory limits (16GB to 128GB), and execution runtimes from alignment to final variant calling.
    * **Interactive Differential Expression:** Integrated live volcano plot rendering with adjustable fold-change and significance cutoff sliders.
    """)

    st.markdown("#### 🟢 Week 6: Automated Reporting, Container Registry & Client Handover")
    st.markdown("""
    * **Automated MultiQC & Execution Tracking:** Configured Nextflow and Snakemake execution logging (`-with-report`, `-with-trace`, `-with-dag`) to export comprehensive HTML performance summaries.
    * **Container Registry & Amazon ECR Packaging:** Multi-architecture Docker/Apptainer images packaged and pushed to Amazon ECR / Quay.io with tool pinning.
    * **Executive Report & Output Artifacts:** Automated summary reporting tables and exportable CSV artifacts for clinical analysis.
    * **Client Handover & Technical Walkthrough:** Finalized platform documentation, GitHub Pages browser deployment runbooks, and team handover sessions.
    """)

    st.markdown("---")
    st.markdown("#### 📜 Historical Client Assessments")
    if st.session_state.assessments:
        st.table(st.session_state.assessments)
    else:
        st.info("No assessments logged in this session yet.")
