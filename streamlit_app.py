import streamlit as st
import json
from datetime import datetime
import math
import random

if "assessments" not in st.session_state:
    st.session_state.assessments = []

st.set_page_config(page_title="Biotech Readiness Engine", layout="wide")

st.title("🧬 Bioinformatics Readiness & Statistical Engine")
st.caption("Week 4: Readiness Assessment, Nextflow Generator, Cost Estimator & Differential Expression Analysis")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 Readiness Assessment", 
    "📊 Statistical Analysis & PCA",
    "⚡ Pipeline Generator", 
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

        st.markdown("#### 2. Omics Modalities & Data Volume")
        data_types = st.multiselect(
            "Primary Workloads",
            ["Preventive Genomics WGS", "cfDNA / Fragmentomics", "ChIP-seq / Epigenetics", "Bulk RNA-seq", "scRNA-seq", "Oncology Panels"],
            default=["Preventive Genomics WGS", "cfDNA / Fragmentomics"]
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

        submitted = st.form_submit_button("Run Assessment Engine 🔥")

    if submitted:
        bottlenecks = []
        recommendations = []

        omics_score = 3
        if "cfDNA / Fragmentomics" in data_types or "ChIP-seq / Epigenetics" in data_types:
            omics_score += 1
            if team_size < 3:
                bottlenecks.append("High-noise omics require automated biological QC filtering.")
                recommendations.append("Implement biological QC layers before variant calling.")

        if "Preventive Genomics WGS" in data_types:
            omics_score = min(5, omics_score + 1)
            if monthly_gb > 1000 and not has_cold_archive:
                bottlenecks.append("High WGS data growth requires automated cold archiving.")
                recommendations.append("Set S3 Glacier Deep Archive lifecycle rules after 30 days.")

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

        st.success("Assessment Computed! Check the other tabs for pipeline code and analytics.")

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
# TAB 2: STATISTICAL ANALYSIS & PCA (WEEK 4 FEATURE)
# ---------------------------------------------------------
with tab2:
    st.markdown("### 📊 Differential Expression & High-Dimensional Clustering")
    st.caption("Interactive biological signal extraction engine for transcriptomics and panel profiling.")

    analysis_mode = st.radio("Select Analysis Module", ["Differential Expression (Volcano Plot)", "Sample Clustering (PCA Map)"], horizontal=True)

    st.markdown("---")

    if analysis_mode == "Differential Expression (Volcano Plot)":
        st.markdown("#### 🌋 Interactive Differential Expression Analysis")
        st.caption("Adjust significance thresholds to filter differentially expressed genes (DEGs).")

        col_param1, col_param2 = st.columns(2)
        with col_param1:
            p_threshold = st.slider("Significance Threshold (-log10 p-value)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)
        with col_param2:
            fc_threshold = st.slider("Fold-Change Cutoff (|log2FC|)", min_value=0.5, max_value=4.0, value=1.5, step=0.25)

        # Generate Synthetic DEG Dataset inside Wasm
        random.seed(42)
        genes = ["TP53", "EGFR", "BRCA1", "MYC", "KRAS", "VEGFA", "IL6", "TNF", "AKT1", "CDK4", "ESR1", "PTEN", "MET", "CDK6", "ERBB2"]
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

        # Calculate DEG counts
        up_count = sum(1 for d in deg_data if d["Status"] == "Upregulated")
        down_count = sum(1 for d in deg_data if d["Status"] == "Downregulated")
        ns_count = len(deg_data) - (up_count + down_count)

        s1, s2, s3 = st.columns(3)
        s1.metric("Upregulated Genes", up_count)
        s2.metric("Downregulated Genes", down_count)
        s3.metric("Non-Significant", ns_count)

        st.scatter_chart(
            deg_data,
            x="log2FC",
            y="-log10(p)",
            color="Status",
            size=None
        )

        st.markdown("##### 🧬 Top Significant Gene Hits")
        sig_genes = [d for d in deg_data if d["Status"] != "Not Significant"]
        if sig_genes:
            st.dataframe(sig_genes, use_container_width=True)
        else:
            st.info("No genes meet the current significance and fold-change thresholds.")

    else:
        st.markdown("#### 🎯 Principal Component Analysis (PCA)")
        st.caption("Assess cohort batch effects and sample separation along principal axes.")

        num_samples = st.slider("Number of Samples in Cohort", min_value=10, max_value=60, value=30, step=5)
        
        # Generate Synthetic PCA Cluster Data
        random.seed(123)
        pca_points = []
        groups = ["Control (Healthy)", "Treated (Drug A)", "Responder Cohort"]

        for i in range(num_samples):
            group = groups[i % len(groups)]
            if group == "Control (Healthy)":
                pc1 = round(random.gauss(-3.0, 1.2), 2)
                pc2 = round(random.gauss(-1.0, 1.0), 2)
            elif group == "Treated (Drug A)":
                pc1 = round(random.gauss(2.5, 1.0), 2)
                pc2 = round(random.gauss(2.0, 1.1), 2)
            else:
                pc1 = round(random.gauss(1.0, 0.9), 2)
                pc2 = round(random.gauss(-3.0, 1.2), 2)

            pca_points.append({"Sample_ID": f"SAMP_{i+1:02d}", "PC1 (42.5%)": pc1, "PC2 (18.3%)": pc2, "Group": group})

        st.scatter_chart(
            pca_points,
            x="PC1 (42.5%)",
            y="PC2 (18.3%)",
            color="Group"
        )

        st.info("💡 **Interpretation:** Clear separation along PC1 indicates treatment-induced variance, while PC2 captures baseline cohort heterogeneity.")

# ---------------------------------------------------------
# TAB 3: PIPELINE GENERATOR
# ---------------------------------------------------------
with tab3:
    st.markdown("### ⚡ Nextflow DSL2 Workflow & Container Generator")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        target_modality = st.selectbox(
            "Select Pipeline Template",
            ["Bulk RNA-seq (STAR / Salmon)", "Preventive Genomics (WGS / GATK4)", "cfDNA / Liquid Biopsy"]
        )
    with p_col2:
        executor_type = st.selectbox("Compute Engine", ["AWS Batch", "Google Cloud Batch", "Slurm HPC"])

    st.markdown("---")

    if "RNA-seq" in target_modality:
        main_nf = """nextflow.enable.dsl=2

params.reads = "$projectDir/data/*_{1,2}.fastq.gz"
params.outdir = "$projectDir/results"

process FASTQC {
    tag "$sample_id"
    container 'biocontainers/fastqc:v0.11.9_cv8'

    input:
    tuple val(sample_id), path(reads)

    output:
    path "*.zip", emit: fastqc_files

    script:
    \"\"\"
    fastqc ${reads}
    \"\"\"
}

process SALMON_QUANT {
    tag "$sample_id"
    container 'biocontainers/salmon:v1.10.1_cv1'

    input:
    tuple val(sample_id), path(reads)

    output:
    path "${sample_id}_quant", emit: quant_results

    script:
    \"\"\"
    salmon quant -i $params.transcriptome -l A -1 ${reads[0]} -2 ${reads[1]} -o ${sample_id}_quant
    \"\"\"
}

workflow {
    read_pairs_ch = Channel.fromFilePairs(params.reads)
    FASTQC(read_pairs_ch)
    SALMON_QUANT(read_pairs_ch)
}"""
    else:
        main_nf = """nextflow.enable.dsl=2

params.reads = "$projectDir/data/*_{1,2}.fastq.gz"
params.genome = "$projectDir/ref/hg38.fasta"
params.outdir = "$projectDir/results"

process BWA_ALIGN {
    tag "$sample_id"
    container 'biocontainers/bwa:v0.7.17_cv1'

    input:
    tuple val(sample_id), path(reads)

    output:
    tuple val(sample_id), path("${sample_id}.bam")

    script:
    \"\"\"
    bwa mem -t 8 $params.genome ${reads[0]} ${reads[1]} | samtools sort -o ${sample_id}.bam
    \"\"\"
}

workflow {
    read_pairs_ch = Channel.fromFilePairs(params.reads)
    BWA_ALIGN(read_pairs_ch)
}"""

    dockerfile_code = """FROM ubuntu:22.04

LABEL maintainer="Jordana Consulting"
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \\
    build-essential \\
    wget \\
    curl \\
    samtools \\
    fastqc \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/bioinformatics
CMD ["/bin/bash"]"""

    samplesheet_code = """sample,fastq_1,fastq_2,single_end
sample_01,s3://my-bucket/fastqs/sample_01_R1.fastq.gz,s3://my-bucket/fastqs/sample_02_R2.fastq.gz,false
sample_02,s3://my-bucket/fastqs/sample_02_R1.fastq.gz,s3://my-bucket/fastqs/sample_02_R2.fastq.gz,false"""

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
# TAB 4: COST ESTIMATOR
# ---------------------------------------------------------
with tab4:
    st.markdown("### 💰 Cloud Storage & Compute Cost Estimator")
    calc_c1, calc_c2 = st.columns(2)
    with calc_c1:
        calc_gb = st.slider("Monthly Raw Data Ingestion (GB)", min_value=100, max_value=20000, value=2000, step=100)
        retention_months = st.slider("Hot Storage Retention (Months)", min_value=1, max_value=12, value=3)
        compute_hours_per_sample = st.number_input("Est. Compute Hours / 100GB", value=4.0, step=0.5)

    with calc_c2:
        num_samples = calc_gb / 100
        total_hot_gb = calc_gb * retention_months
        total_cold_gb = max(0, (calc_gb * 12) - total_hot_gb)

        monthly_hot = total_hot_gb * 0.023
        monthly_cold = total_cold_gb * 0.00099
        monthly_compute = num_samples * compute_hours_per_sample * 8 * 0.04

        st.metric("Hot Storage Spend", f"${monthly_hot:,.2f} / mo")
        st.metric("Cold Storage Spend", f"${monthly_cold:,.2f} / mo")
        st.metric("Estimated Pipeline Compute (Spot)", f"${monthly_compute:,.2f} / mo")

        st.subheader(f"Total Projected Monthly Cloud Spend: **${(monthly_hot + monthly_cold + monthly_compute):,.2f}**")

# ---------------------------------------------------------
# TAB 5: SESSION LOGS
# ---------------------------------------------------------
with tab5:
    st.markdown("### 📊 Historical Session Logs")
    if st.session_state.assessments:
        st.table(st.session_state.assessments)
    else:
        st.info("No assessments completed in this browser session yet.")
