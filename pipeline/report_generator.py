"""
report_generator.py

Minimal report generator that creates a one-page PDF using reportlab and optionally
uploads it to S3. This is intentionally small to serve as a starting point for the POC.
"""
import os
import argparse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import boto3


def make_pdf(output_path, metadata):
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    c.setFont('Helvetica-Bold', 16)
    c.drawString(40, height - 60, 'BioFlow Cloud - Executive Pipeline Report')

    c.setFont('Helvetica', 10)
    c.drawString(40, height - 90, f"Generated: {metadata.get('generated', 'unknown')}")
    c.drawString(40, height - 110, f"Samples processed: {metadata.get('samples', 'N/A')}")
    c.drawString(40, height - 130, f"Pipeline: nf-core/rnaseq")

    c.drawString(40, height - 170, 'Summary:')
    text = c.beginText(40, height - 190)
    text.setFont('Helvetica', 9)
    text.textLines(metadata.get('summary', 'No summary available.'))
    c.drawText(text)

    c.showPage()
    c.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', required=True, help='Path to pipeline results folder')
    parser.add_argument('--out', required=True, help='Output PDF path')
    parser.add_argument('--upload-s3', default=None, help='Optional S3 path to upload the PDF (s3://bucket/key)')
    args = parser.parse_args()

    # Minimal metadata extraction; extend as needed
    metadata = {
        'generated': os.environ.get('CI_TIMESTAMP') or 'manual',
        'samples': os.environ.get('SAMPLES_COUNT', '1'),
        'summary': 'Pipeline completed successfully (POC).'
    }

    make_pdf(args.out, metadata)

    if args.upload_s3:
        s3 = boto3.client('s3')
        uri = args.upload_s3.replace('s3://', '')
        bucket, key = uri.split('/', 1)
        s3.upload_file(args.out, bucket, key)
        print('Uploaded to s3://%s/%s' % (bucket, key))
