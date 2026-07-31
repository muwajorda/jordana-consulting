import streamlit as st
import json
from datetime import datetime
import math
import random

# Initialize session states
if "assessments" not in st.session_state:
    st.session_state.assessments = []

if "active_workloads" not in st.session_state:
    st.session_state.active_workloads = ["scRNA-seq (Single Cell)", "Oncology Panels (Somatic Mutect2)"]

st.set_page_config(page_title="Biotech Readiness Engine", layout="wide")

st.title("🧬 Bioinformatics Readiness & Dynamic Pipeline Engine")
st.caption("Auto-adapts Nextflow DSL2 templates, structured metadata samplesheets & DAG execution graphs")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 Readiness Assessment", 
    "⚡ Pipeline Generator & DAG Graph", 
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

        st.session_state.active_workloads = data_types

        omics_score = 3
        if "scRNA-seq (Single Cell)" in data_types or "cfDNA / Fragmentomics" in data_types:
            omics_score += 1
            if team_size < 3:
                bottlenecks.append("High cell-count / single-cell runs require high-memory compute nodes.")
                recommendations.append("Configure AWS Batch / GCP Batch memory autoscaling for Cell Ranger.")

        if "Oncology Panels (Somatic Mutect2)" in data_types:
            omics_score = min(5, omics_score + 1)
            recommendations.append("Incorporate Tumor-Matched Normal pipelines for accurate somatic calling.")

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

        st.success("✅ Assessment Computed! Check 'Pipeline Generator & DAG Graph' tab for updated samplesheets and visual workflow graph.")

        m1, m2, m3 = st.columns(3)
        m1.metric("Omics Readiness", f"{min(5, omics_score)} / 5")
        m2.metric("Infra Readiness", f"{min(5, infra_score)} / 5")
        m3.metric("Team Maturity", f"{team_score} / 5")

# ---------------------------------------------------------
# TAB 2: PIPELINE GENERATOR & ENHANCED SAMPLESHEET
# ---------------------------------------------------------
with tab2:
    st.markdown("### ⚡ Nextflow DSL2 Workflow & Metadata-Enriched Samplesheet")
    st.caption("Templates and structured samplesheets dynamically update based on pipeline selection.")

    p_col1, p_col2 = st.columns(2)
    with p_col1:
        available_templates = st.session_state.active_workloads if st.session_state.active_workloads else [
            "scRNA-seq (Single Cell)", 
            "Oncology Panels (Somatic Mutect2)", 
            "TCGA / GDC Public Data Ingestion"
        ]
        
        target_modality = st.selectbox(
            "Select Pipeline Template",
            options=available_templates,
            index=0
        )
    with p_col2:
        executor_type = st.selectbox("Compute Engine", ["AWS Batch", "Google Cloud Batch", "Slurm HPC"])

    st.markdown("---")

    # Generate Modality-Specific Nextflow Code, SVG DAG, and Structured Samplesheet
    if "scRNA-seq" in target_modality:
        svg_dag = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 160" style="background:#0f172a; border-radius:8px; padding:10px; width:100%;">
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
            </marker>
          </defs>
          <rect x="20" y="50" width="130" height="50" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
          <text x="85" y="80" fill="#f8fafc" font-size="12" font-family="monospace" text-anchor="middle">FASTQ Input</text>
          
          <line x1="150" y1="75" x2="220" y2="75" stroke="#10b981" stroke-width="2" marker-end="url(#arrow)" />
          
          <rect x="225" y="50" width="160" height="50" rx="8" fill="#1e293b" stroke="#10b981" stroke-width="2"/>
          <text x="305" y="72" fill="#f8fafc" font-size="12" font-family="monospace" text-anchor="middle">CELLRANGER_COUNT</text>
          <text x="305" y="88" fill="#94a3b8" font-size="10" font-family="sans-serif" text-anchor="middle">Alignment & Demux</text>
          
          <line x1="385" y1="75" x2="455" y2="75" stroke="#10b981" stroke-width="2" marker-end="url(#arrow)" />
          
          <rect x="460" y="20" width="150" height="45" rx="8" fill="#1e293b" stroke="#a855f7" stroke-width="2"/>
          <text x="535" y="47" fill="#f8fafc" font-size="11" font-family="monospace" text-anchor="middle">SEURAT_QC</text>

          <rect x="460" y="85" width="150" height="45" rx="8" fill="#1e293b" stroke="#a855f7" stroke-width="2"/>
          <text x="535" y="112" fill="#f8fafc" font-size="11" font-family="monospace" text-anchor="middle">SCANPY_UMAP</text>
          
          <line x1="610" y1="42" x2="670" y2="75" stroke="#10b981" stroke-width="2" marker-end="url(#arrow)" />
          <line x1="610" y1="108" x2="670" y2="75" stroke="#10b981" stroke-width="2" marker-end="url(#arrow)" />

          <rect x="675" y="50" width="100" height="50" rx="8" fill="#065f46" stroke="#34d399" stroke-width="2"/>
          <text x="725" y="80" fill="#f8fafc" font-size="12" font-family="monospace" text-anchor="middle">h5ad / rds</text>
        </svg>
        """
        main_nf = """nextflow.enable.dsl=2

params.samplesheet = "$projectDir/samplesheet.csv"
params.transcriptome = "$projectDir/ref/refdata-gex-GRCh38-2020-A"
params.outdir = "$projectDir/results"

process CELLRANGER_COUNT {
    tag "$sample_id"
    container 'cumulus/cellranger:7.1.0'

    input:
    tuple val(sample_id), val(fastq_1), val(fastq_2)

    output:
    path "${sample_id}_out", emit: count_matrix

    script:
    \"\"\"
    cellranger count --id=${sample_id}_out --transcriptome=${params.transcriptome} --fastqs=${fastq_1}
    \"\"\"
}

workflow {
    samples_ch = Channel
        .fromPath(params.samplesheet)
        .splitCsv(header:true)
        .map { row -> tuple(row.sample_id, row.fastq_1, row.fastq_2) }

    CELLRANGER_COUNT(samples_ch)
}"""
        dockerfile_code = """FROM ubuntu:22.04
LABEL maintainer="Jordana Consulting - Single Cell Engine"
RUN apt-get update && apt-get install -y wget curl python3 python3-pip
RUN pip3 install scanpy seurat-disk scrublet
WORKDIR /opt/singlecell
CMD ["/bin/bash"]"""

        samplesheet_code = """sample_id,omics_modality,experiment_type,data_type,file_type,fastq_1,fastq_2
PBMC_10k_Ctrl,Single-Cell Transcriptomics,10x Chromium 3' v3,Raw Gene Expression,FASTQ (GZIP),s3://my-bucket/sc_fastqs/pbmc_10k_R1.fastq.gz,s3://my-bucket/sc_fastqs/pbmc_10k_R2.fastq.gz
TCell_Tumor_01,Single-Cell Transcriptomics,10x Chromium 5' VDJ,Immune Profiling,FASTQ (GZIP),s3://my-bucket/sc_fastqs/tcell_R1.fastq.gz,s3://my-bucket/sc_fastqs/tcell_R2.fastq.gz"""

    elif "Oncology Panels" in target_modality:
        svg_dag = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 160" style="background:#0f172a; border-radius:8px; padding:10px; width:100%;">
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8" />
            </marker>
          </defs>
          <rect x="20" y="20" width="130" height="45" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
          <text x="85" y="47" fill="#f8fafc" font-size="11" font-family="monospace" text-anchor="middle">Tumor FASTQ</text>
          
          <rect x="20" y="85" width="130" height="45" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
          <text x="85" y="112" fill="#f8fafc" font-size="11" font-family="monospace" text-anchor="middle">Normal FASTQ</text>
          
          <line x1="150" y1="42" x2="210" y2="75" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)" />
          <line x1="150" y1="108" x2="210" y2="75" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)" />

          <rect x="215" y="50" width="150" height="50" rx="8" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
          <text x="290" y="80" fill="#f8fafc" font-size="12" font-family="monospace" text-anchor="middle">BWA_MEM_ALIGN</text>
          
          <line x1="365" y1="75" x2="435" y2="75" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)" />

          <rect x="440" y="50" width="160" height="50" rx="8" fill="#1e293b" stroke="#ef4444" stroke-width="2"/>
          <text x="520" y="80" fill="#f8fafc" font-size="12" font-family="monospace" text-anchor="middle">GATK_MUTECT2</text>
          
          <line x1="600" y1="75" x2="670" y2="75" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow)" />

          <rect x="675" y="50" width="100" height="50" rx="8" fill="#7f1d1d" stroke="#f87171" stroke-width="2"/>
          <text x="725" y="80" fill="#f8fafc" font-size="12" font-family="monospace" text-anchor="middle">Somatic VCF</text>
        </svg>
        """
        main_nf = """nextflow.enable.dsl=2

params.samplesheet = "$projectDir/samplesheet.csv"
params.genome = "$projectDir/ref/hg38.fasta"

process MUTECT2_SOMATIC {
    tag "$sample_id"
    container 'broadinstitute/gatk:4.4.0.0'

    input:
    tuple val(sample_id), val(tumor_bam), val(normal_bam)

    output:
    path "${sample_id}.vcf.gz", emit: vcf

    script:
    \"\"\"
    gatk Mutect2 -R ${params.genome} -I ${tumor_bam} -tumor ${sample_id}_T -I ${normal_bam} -normal ${sample_id}_N -O ${sample_id}.vcf.gz
    \"\"\"
}

workflow {
    samples_ch = Channel
        .fromPath(params.samplesheet)
        .splitCsv(header:true)
        .map { row -> tuple(row.sample_id, row.tumor_bam, row.normal_bam) }

    MUTECT2_SOMATIC(samples_ch)
}"""
        dockerfile_code = """FROM broadinstitute/gatk:4.4.0.0
LABEL maintainer="Jordana Consulting - Somatic Oncology"
RUN apt-get update && apt-get install -y bcftools samtools python3-pandas"""

        samplesheet_code = """sample_id,omics_modality,experiment_type,data_type,file_type,tumor_bam,normal_bam
PATIENT_01,Cancer Genomics,Targeted Hybrid Capture Panel,Somatic Variant Calling,Aligned BAM,s3://my-bucket/oncology/P01_T.bam,s3://my-bucket/oncology/P01_N.bam
PATIENT_02,Cancer Genomics,Targeted Hybrid Capture Panel,Somatic Variant Calling,Aligned BAM,s3://my-bucket/oncology/P02_T.bam,s3://my-bucket/oncology/P02_N.bam"""

    else:
        svg_dag = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 160" style="background:#0f172a; border-radius:8px; padding:10px; width:100%;">
          <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#a855f7" />
            </marker>
          </defs>
          <rect x="50" y="50" width="150" height="50" rx="8" fill="#1e293b" stroke="#a855f7" stroke-width="2"/>
          <text x="125" y="80" fill="#f8fafc" font-size="12" font-family="monospace" text-anchor="middle">GDC Manifest</text>
          
          <line x1="200" y1="75" x2="300" y2="75" stroke="#a855f7" stroke-width="2" marker-end="url(#arrow)" />

          <rect x="305" y="50" width="180" height="50" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
          <text x="395" y="80" fill="#f8fafc" font-size="12" font-family="monospace" text-anchor="middle">GDC_CLIENT_DOWNLOAD</text>
          
          <line x1="485" y1="75" x2="585" y2="75" stroke="#a855f7" stroke-width="2" marker-end="url(#arrow)" />

          <rect x="590" y="50" width="150" height="50" rx="8" fill="#581c87" stroke="#c084fc" stroke-width="2"/>
          <text x="665" y="80" fill="#f8fafc" font-size="12" font-family="monospace" text-anchor="middle">TCGA Data Lake</text>
        </svg>
        """
        main_nf = """nextflow.enable.dsl=2

params.samplesheet = "$projectDir/samplesheet.csv"

process GDC_DOWNLOAD {
    container 'biocontainers/gdc-client:v1.6.1_cv1'

    input:
    tuple val(sample_id), val(file_id)

    output:
    path "gdc_downloaded/*", emit: tcga_files

    script:
    \"\"\"
    gdc-client download ${file_id} -d gdc_downloaded/
    \"\"\"
}

workflow {
    samples_ch = Channel
        .fromPath(params.samplesheet)
        .splitCsv(header:true)
        .map { row -> tuple(row.sample_id, row.file_id) }

    GDC_DOWNLOAD(samples_ch)
}"""
        dockerfile_code = """FROM ubuntu:22.04
RUN apt-get update && apt-get install -y curl unzip
RUN curl -O https://gdc.cancer.gov/files/public/file/gdc-client_v1.6.1_Ubuntu_x64.zip \\
    && unzip gdc-client_v1.6.1_Ubuntu_x64.zip -d /usr/local/bin/"""

        samplesheet_code = """sample_id,omics_modality,experiment_type,data_type,file_type,file_id
TCGA_BRCA_01,Cancer Transcriptomics,Bulk RNA-seq Illumina NovaSeq,HTSeq Gene Counts,GZIP CSV,a1b2c3d4-e5f6-7890-1234-56789abcdef0
TCGA_LUAD_02,Cancer Transcriptomics,Bulk RNA-seq Illumina NovaSeq,HTSeq Gene Counts,GZIP CSV,b2c3d4e5-f6a7-8901-2345-6789abcdef01"""

    st.markdown("#### 🗺 Visual Execution Graph (DAG)")
    st.components.v1.html(svg_dag, height=180)

    code_tab1, code_tab2, code_tab3 = st.tabs(["📋 samplesheet.csv", "📄 main.nf", "🐳 Dockerfile"])

    with code_tab1:
        st.markdown("##### Metadata-Enriched Pipeline Input CSV")
        st.code(samplesheet_code, language="csv")
        st.download_button("Download samplesheet.csv", data=samplesheet_code, file_name="samplesheet.csv", mime="text/csv")

    with code_tab2:
        st.code(main_nf, language="groovy")
        st.download_button("Download main.nf", data=main_nf, file_name="main.nf", mime="text/plain")

    with code_tab3:
        st.code(dockerfile_code, language="dockerfile")
        st.download_button("Download Dockerfile", data=dockerfile_code, file_name="Dockerfile", mime="text/plain")

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
