"""
streamlit_integration_patch.py

Small helper to show how the Streamlit app can post a run request to the onboarding webhook / API Gateway.
This file is a small example and should be integrated into streamlit_app.py where you want to trigger runs.
"""
import os
import requests

ONBOARDING_WEBHOOK = os.environ.get('ONBOARDING_WEBHOOK')


def post_run_request(payload):
    """Post a run request to the onboarding webhook. Returns response JSON or raises.
    payload example: {'email':..., 'samplesheet_s3': 's3://bucket/key', 'pipeline': 'rnaseq'}
    """
    if not ONBOARDING_WEBHOOK:
        print('ONBOARDING_WEBHOOK not configured - dry run')
        return {'status': 'dry-run', 'payload': payload}

    resp = requests.post(ONBOARDING_WEBHOOK, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()
