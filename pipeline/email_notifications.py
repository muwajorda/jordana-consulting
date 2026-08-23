"""
email_notifications.py

SES-based email sender for delivering report links. This is a minimal helper and
intended to be invoked from the pipeline post-processing step.
"""
import os
import boto3

SES_REGION = os.environ.get('AWS_REGION', 'us-east-1')
SES_SENDER = os.environ.get('SES_SENDER', 'no-reply@example.com')
DRY_RUN = os.environ.get('DRY_RUN', 'true').lower() == 'true'

ses = boto3.client('ses', region_name=SES_REGION) if not DRY_RUN else None


def send_report_email(recipient, subject, html_body, text_body=None):
    if DRY_RUN:
        print('DRY_RUN: send email to', recipient)
        return {'status': 'dry-run'}

    if not text_body:
        text_body = 'Please view the attached report.'

    resp = ses.send_email(
        Source=SES_SENDER,
        Destination={'ToAddresses': [recipient]},
        Message={
            'Subject': {'Data': subject},
            'Body': {
                'Html': {'Data': html_body},
                'Text': {'Data': text_body}
            }
        }
    )
    return resp
