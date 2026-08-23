#!/usr/bin/env nextflow

/*
 * main.nf - wrapper that launches nf-core/rnaseq with a provided samplesheet.
 * This is a lightweight scaffold for the cloud POC. The actual nf-core pipeline
 * will run as 'nextflow run nf-core/rnaseq -profile ...'
 */

params.samplesheet = null
params.outdir = params.outdir ?: "results"
params.profile = params.profile ?: 'local'

process prepare_run {
    tag "prepare"
    input:
    path samplesheet if params.samplesheet

    output:
    path 'samplesheet.csv', emit: ss

    script:
    """
    cp ${samplesheet} samplesheet.csv
    """
}

workflow {
    if (params.samplesheet) {
        prepare_run(samplesheet: file(params.samplesheet))
    }

    main_run()
}

process main_run {
    tag "nfcore-rnaseq"
    input:
    path ss from prepare_run.out.ss

    output:
    path "${params.outdir}", emit: outdir

    script:
    """
    # Run nf-core/rnaseq. In production you may pin a version and set profiles.
    nextflow run nf-core/rnaseq -r 3.10.1 --input ${ss} --outdir ${params.outdir} -profile ${params.profile} 

    # After run completes, call the report generator to create an executive PDF.
    python3 ../pipeline/report_generator.py --results ${params.outdir} --out ${params.outdir}/executive_report.pdf || true
    """
}
