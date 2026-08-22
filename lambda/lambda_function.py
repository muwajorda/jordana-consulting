"""
lambda_function.py

S3 Event Lambda stub that validates uploaded samplesheet/FASTQ and enqueues a run request to SQS.
Environment variables required by this stub:
- RUN_QUEUE_URL
- RESULTS_BUCKET
- DRY_RUN (optional)

This is a minimal, well-commented scaffold. Do not deploy without reviewing IAM role permissions and adding error handling for your environment.
"""
import os
import json
import boto3
import urllib.parse

RUN_QUEUE_URL = os.environ.get('RUN_QUEUE_URL')
RESULTS_BUCKET = os.environ.get('RESULTS_BUCKET')
DRY_RUN = os.environ.get('DRY_RUN', 'true').lower() == 'true'

sqs = boto3.client('sqs') if not DRY_RUN else None


def lambda_handler(event, context):
    """Handle S3 PUT events. Expect either a samplesheet.csv or FASTQ files.
    For a samplesheet upload we create a run request including the S3 path.
    """
    records = event.get('Records', [])
    responses = []

    for r in records:
        s3 = r.get('s3', {})
        bucket = s3.get('bucket', {}).get('name')
        key = urllib.parse.unquote_plus(s3.get('object', {}).get('key', ''))

        # Very basic validation by extension
        if key.endswith('.csv') or key.endswith('.tsv'):
            run_request = {
                'type': 'samplesheet',
                'bucket': bucket,
                'key': key
            }
        elif key.endswith('.fastq') or key.endswith('.fastq.gz') or key.endswith('.fq.gz'):
            run_request = {
                'type': 'fastq',
                'bucket': bucket,
                'key': key
            }
        else:
            run_request = {'type': 'other', 'bucket': bucket, 'key': key}

        if DRY_RUN:
            print('DRY_RUN: would enqueue', run_request)
            responses.append({'status': 'dry-run', 'request': run_request})
        else:
            res = sqs.send_message(QueueUrl=RUN_QUEUE_URL, MessageBody=json.dumps(run_request))
            responses.append({'status': 'enqueued', 'messageId': res.get('MessageId')})

    return {'statusCode': 200, 'body': json.dumps(responses)}
