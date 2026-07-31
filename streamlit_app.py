import streamlit as st
import json
from datetime import datetime
import math
import random

# Initialize session states
if "assessments" not in st.session_state:
    st.session_state.assessments = []

if "recommended_pipeline" not in st.session_state:
    st.session_state.recommended_pipeline = "scRNA-seq (Cell Ranger / Seurat)"

if "active_workloads" not in st.session_state:
    st.session_state.active_workloads = ["scRNA-seq", "Oncology Panels"]

st.set_page_config(page_title="Biotech Readiness Engine", layout="wide")

st.title("🧬 Bioinformatics Readiness & Dynamic Pipeline Engine")
st.caption("Auto-adapts Nextflow DSL2 templates based on your Readiness Assessment selections")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 Readiness Assessment", 
    "⚡ Pipeline Generator", 
    "📊 Statistical Analysis & PCA",
    "💰 Cost Estimator", 
    "📋 Session History"
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
                "TCGA / GDC Public Data Ingestion", 
                "Preventive Genomics WGS", 
                "cfDNA / Fragmentomics", 
                "Bulk RNA-seq"
            ],
            default=["scRNA-seq (Single Cell)", "Oncology Panels (Somatic Mutect2)"]
        )
        monthly_gb = st.number_input("Monthly Data Ingestion (GB)", value=1200, step=100)

        st.markdown("#### 3. Infrastructure Checklist")
        col3, col4 = st.columns(2)
        with col3:
            uses_containers = st.checkbox("Uses Containers (Docker / Apptainer)", value=True)
            has_cold_archive = st.checkbox("Cold Storage Tiering Configured", value=False)
        with col4:
            uses_spot_instances = st.checkbox("Utilizes Spot / Preemptible Instances", value=True)
            has_ci_cd = st.checkbox("CI/CD Integration", value=False)

        submitted = st.form_submit_button("Run Assessment & Link Pipelines 🔥")

    if submitted:
        bottlenecks = []
        recommendations = []

        # Update global session state for Tab 2
        st.session_state.active_workloads = data_types
        if data_types:
            st.session_state.recommended_pipeline = data_types[0]

        omics_score = 3
        if "scRNA-seq (Single Cell)" in data_types or "cfDNA / Fragmentomics" in data_types:
            omics_score += 1
            if team_size < 3:
                bottlenecks.append("High cell-count / single-cell runs require high-memory compute nodes.")
                recommendations.append("Configure AWS Batch / GCP Batch memory autoscaling for Cell Ranger.")

        if "Oncology Panels (Somatic Mutect2)" in data_types:
            omics_score = min(5, omics_score + 1)
            recommendations.append("Incorporate Tumor-Matched Normal pipelines for accurate somatic calling.")

        if "TCGA / GDC Public Data Ingestion" in data_types:
            recommendations.append("Automate Genomic Data Commons (GDC) API download processes via Nextflow.")

        infra_score = 3 if uses_containers else 1
        if uses_spot_instances:
            infra_score = min(5, infra_score + 1)

        team_score = min(5, max(1, team_size * 2))

        st.session_state.assessments.append({
            "Company": company_name,
            "Stage": stage,
            "Cloud": cloud_provider.split(" ")[0],
            "Omics Score": f"{min(5, omics_score)}/5",
            "Infra Score": f"{min(5, infra_score)}/5",
            "Team Score": f"{team_score}/5",
            "Monthly GB": monthly_gb,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

        st.success("✅ Assessment Computed! Navigating to 'Pipeline Generator' will now display your selected pipelines.")

        m1, m2, m3 = st.columns(3)
        m1.metric("Omics Readiness", f"{min(5, omics_score)} / 5")
        m2.metric("Infra Readiness", f"{min(5, infra_score)} / 5")
        m3.metric("Team Maturity", f"{team_score} / 5")

        col_b, col_r = st.columns(2)
        with col_b:
            if bottlenecks:
                st.markdown("##### 🚨 Identified Bottlenecks")
                for b in bottlenecks:
                    st.warning(f"- {b}")
        with col_r:
            if recommendations:
                st.markdown("##### 🚀 Recommended Actions")
                for r in recommendations:
                    st.info(f"- {r}")

# ---------------------------------------------------------
# TAB 2: PIPELINE GENERATOR (DYNAMICALLY POPULATED)
# ---------------------------------------------------------
with tab2:
    st.markdown("### ⚡ Nextflow DSL2 Workflow & Container Generator")
    st.caption("Templates dynamically match your selections from the Readiness Assessment.")

    p_col1, p_col2 = st.columns(2)
    with p_col1:
        # Dynamically build pipeline list based on assessment selections
        available_templates = st.session_state.active_workloads if st.session_state.active_workloads else [
            "scRNA-seq (Single Cell)", 
            "Oncology Panels (Somatic Mutect2)", 
            "TCGA / GDC Public Data Ingestion", 
            "Bulk RNA-seq"
        ]
        
        target_modality = st.selectbox(
            "Select Pipeline Template",
            options=available_templates,
            index=0
        )
    with p_col2:
        executor_type = st.selectbox("Compute Engine", ["AWS Batch", "Google Cloud Batch", "Slurm HPC"])

    st.markdown("---")

    # Dynamic Code Generation
    if "scRNA-seq" in target_modality:
        main_nf = """nextflow.enable.dsl=2

params.fastqs = "$projectDir/fastqs"
params.transcriptome = "$projectDir/ref/refdata-gex-GRCh38-2020-A"
params.outdir = "$projectDir/results"

process CELLRANGER_COUNT {
    tag "$sample_id"
    container 'cumulus/cellranger:7.1.0'
    memory '64 GB'
    cpus 16

    input:
    tuple val(sample_id), path(fastq_dir)

    output:
    path "${sample_id}_cellranger", emit: count_matrix

    script:
    \"\"\"
    cellranger count --id=${sample_id}_cellranger \\
                     --transcriptome=${params.transcriptome} \\
                     --fastqs=${fastq_dir} \\
                     --sample=${sample_id}
    \"\"\"
}

workflow {
    samples_ch = Channel.fromPath(params.fastqs, type: 'dir')
    CELLRANGER_COUNT(samples_ch)
}"""
        dockerfile_code = """FROM ubuntu:22.04
LABEL maintainer="Jordana Consulting - scRNA Engine"

RUN apt-get update && apt-get install -y wget curl python3 python3-pip
RUN pip3 install scanpy seurat-disk scrublet

WORKDIR /opt/singlecell
CMD ["/bin/bash"]"""

        samplesheet_code = """sample,fastq_dir
PBMC_10k_Control,s3://my-bucket/sc_fastqs/pbmc_10k/
TCell_Tumor_Infiltrate,s3://my-bucket/sc_fastqs/tcell_tumor/"""

    elif "Oncology Panels" in target_modality:
        main_nf = """nextflow.enable.dsl=2

params.tumor_bam = "$projectDir/bams/tumor.bam"
params.normal_bam = "$projectDir/bams/normal.bam"
params.genome = "$projectDir/ref/hg38.fasta"
params.outdir = "$projectDir/results"

process MUTECT2_SOMATIC {
    tag "Oncology_Panel_Variant_Calling"
    container 'broadinstitute/gatk:4.4.0.0'

    input:
    path tumor
    path normal

    output:
    path "somatic_variants.vcf.gz", emit: vcf

    script:
    \"\"\"
    gatk Mutect2 \\
        -R ${params.genome} \\
        -I ${tumor} -tumor Tumor_Sample \\
        -I ${normal} -normal Normal_Sample \\
        -O somatic_variants.vcf.gz
    \"\"\"
}

workflow {
    MUTECT2_SOMATIC(file(params.tumor_bam), file(params.normal_bam))
}"""
        dockerfile_code = """FROM broadinstitute/gatk:4.4.0.0
LABEL maintainer="Jordana Consulting - Somatic Oncology"

RUN apt-get update && apt-get install -y bcftools samtools python3-pandas"""

        samplesheet_code = """tumor_sample,normal_sample,tumor_bam,normal_bam
TUMOR_PANEL_01,NORMAL_PANEL_01,s3://my-bucket/oncology/T01.bam,s3://my-bucket/oncology/N01.bam"""

    elif "TCGA" in target_modality:
        main_nf = """nextflow.enable.dsl=2

params.gdc_manifest = "$projectDir/tcga_manifest.txt"
params.outdir = "$projectDir/tcga_data"

process GDC_DOWNLOAD {
    tag "TCGA_Data_Ingestion"
    container 'biocontainers/gdc-client:v1.6.1_cv1'

    input:
    path manifest

    output:
    path "gdc_downloaded/*", emit: tcga_files

    script:
    \"\"\"
    gdc-client download -m ${manifest} -d gdc_downloaded/
    \"\"\"
}

workflow {
    GDC_DOWNLOAD(file(params.gdc_manifest))
}"""
        dockerfile_code = """FROM ubuntu:22.04
RUN apt-get update && apt-get install -y curl unzip
RUN curl -O https://gdc.cancer.gov/files/public/file/gdc-client_v1.6.1_Ubuntu_x64.zip \\
    && unzip gdc-client_v1.6.1_Ubuntu_x64.zip -d /usr/local/bin/"""

        samplesheet_code = """file_id,filename,data_category,data_type
a1b2c3d4-e5f6-7890-1234-56789abcdef0,TCGA-BRCA.htseq.counts.gz,Transcriptome Profiling,Gene Expression Quantification"""

    else:
        main_nf = """nextflow.enable.dsl=2
// Default Genomics Alignment Pipeline
process BWA_ALIGN {
    container 'biocontainers/bwa:v0.7.17_cv1'
    script:
    \"\"\"
    bwa mem -t 8 ref.fa read1.fq read2.fq > aligned.sam
    \"\"\"
}"""
        dockerfile_code = "FROM biocontainers/bwa:v0.7.17_cv1"
        samplesheet_code = "sample,fastq_1,fastq_2\nS1,s3://b/1.fq,s3://b/2.fq"

    code_tab1, code_tab2, code_tab3 = st.tabs(["📄 main.nf", "🐳 Dockerfile", "📋 samplesheet.csv"])

    with code_tab1:
        st.code(main_nf, language="groovy")
        st.download_button("Download main.nf", data=main_nf, file_name="main.nf", mime="text/plain")

    with code_tab2:
        st.code(dockerfile_code, language="dockerfile")
        st.download_button("Download Dockerfile", data=dockerfile_code, file_name="Dockerfile", mime="text/plain")

    with code_tab3:
        st.code(samplesheet_code, language="csv")
        st.download_button("Download samplesheet.csv", data=samplesheet_code, file_name="samplesheet.csv", mime="text/csv")

# ---------------------------------------------------------
# TAB 3: STATISTICAL ANALYSIS & PCA
# ---------------------------------------------------------
with tab3:
    st.markdown("### 📊 Differential Expression & High-Dimensional Clustering")
    analysis_mode = st.radio("Select Analysis Module", ["Differential Expression (Volcano Plot)", "Sample Clustering (PCA Map)"], horizontal=True)

    if analysis_mode == "Differential Expression (Volcano Plot)":
        p_threshold = st.slider("Significance Threshold (-log10 p-value)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)
        fc_threshold = st.slider("Fold-Change Cutoff (|log2FC|)", min_value=0.5, max_value=4.0, value=1.5, step=0.25)

        random.seed(42)
        genes = ["TP53", "EGFR", "BRCA1", "MYC", "KRAS", "VEGFA", "IL6", "TNF", "AKT1", "CDK4", "ESR1", "PTEN"]
        deg_data = []

        for i in range(100):
            gene_name = genes[i % len(genes)] if i < len(genes) else f"GENE_{i+1}"
            log2_fc = round(random.uniform(-4.0, 4.0), 2)
            p_val = max(0.00001, random.choices([random.uniform(0.00001, 0.001), random.uniform(0.01, 0.5)], weights=[0.3, 0.7])[0])
            neg_log10_p = round(-math.log10(p_val), 2)

            is_up = log2_fc >= fc_threshold and neg_log10_p >= p_threshold
            is_down = log2_fc <= -fc_threshold and neg_log10_p >= p_threshold

            status = "Upregulated" if is_up else "Downregulated" if is_down else "Not Significant"
            deg_data.append({"Gene": gene_name, "log2FC": log2_fc, "-log10(p)": neg_log10_p, "Status": status})

        st.scatter_chart(deg_data, x="log2FC", y="-log10(p)", color="Status")

    else:
        num_samples = st.slider("Number of Samples in Cohort", min_value=10, max_value=60, value=30, step=5)
        random.seed(123)
        pca_points = []
        groups = ["Control (Healthy)", "Treated (Drug A)", "Responder Cohort"]

        for i in range(num_samples):
            group = groups[i % len(groups)]
            pc1 = round(random.gauss(-3.0 if group == "Control (Healthy)" else 2.5, 1.2), 2)
            pc2 = round(random.gauss(-1.0 if group == "Control (Healthy)" else 2.0, 1.1), 2)
            pca_points.append({"Sample_ID": f"SAMP_{i+1:02d}", "PC1": pc1, "PC2": pc2, "Group": group})

        st.scatter_chart(pca_points, x="PC1", y="PC2", color="Group")

# ---------------------------------------------------------
# TAB 4: COST ESTIMATOR
# ---------------------------------------------------------
with tab4:
    st.markdown("### 💰 Cloud Storage & Compute Cost Estimator")
    calc_gb = st.slider("Monthly Raw Data Ingestion (GB)", min_value=100, max_value=20000, value=2000, step=100)
    retention_months = st.slider("Hot Storage Retention (Months)", min_value=1, max_value=12, value=3)

    num_samples = calc_gb / 100
    monthly_hot = (calc_gb * retention_months) * 0.023
    monthly_compute = num_samples * 4.0 * 8 * 0.04

    st.metric("Hot Storage Spend", f"${monthly_hot:,.2f} / mo")
    st.metric("Estimated Pipeline Compute", f"${monthly_compute:,.2f} / mo")

# ---------------------------------------------------------
# TAB 5: SESSION LOGS
# ---------------------------------------------------------
with tab5:
    st.markdown("### 📊 Historical Session Logs")
    if st.session_state.assessments:
        st.table(st.session_state.assessments)
    else:
        st.info("No assessments completed yet.")
