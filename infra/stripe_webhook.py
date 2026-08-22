"""
stripe_webhook.py

Minimal Flask webhook to accept Stripe payment events and push an onboarding message to SQS.
This is a scaffold: do NOT deploy without configuring environment variables and verifying IAM permissions.
"""
from flask import Flask, request, jsonify
import os
import hmac
import hashlib
import boto3
import json

app = Flask(__name__)

# Environment variables expected:
# STRIPE_SIGNING_SECRET - stripe webhook signing secret
# RUN_QUEUE_URL - SQS queue URL for onboarding/run messages
# DRY_RUN=true will log but not send to SQS

STRIPE_SIGNING_SECRET = os.environ.get('STRIPE_SIGNING_SECRET')
RUN_QUEUE_URL = os.environ.get('RUN_QUEUE_URL')
DRY_RUN = os.environ.get('DRY_RUN', 'true').lower() == 'true'

sqs = boto3.client('sqs') if not DRY_RUN else None

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature', '')

    # Basic HMAC check if signing secret provided. This is a simplified example.
    if STRIPE_SIGNING_SECRET:
        expected = hmac.new(STRIPE_SIGNING_SECRET.encode(), payload, hashlib.sha256).hexdigest()
        # NOTE: Real Stripe signatures use a timestamped scheme - use stripe library in production.
        if expected not in sig_header:
            return jsonify({'error': 'signature-mismatch'}), 400

    event = json.loads(payload.decode('utf-8'))

    # Example: on successful checkout.session.completed, create an onboarding message
    typ = event.get('type')
    if typ == 'checkout.session.completed':
        data = event.get('data', {}).get('object', {})
        customer_email = data.get('customer_details', {}).get('email')
        plan = data.get('metadata', {}).get('plan', 'default')

        message = {
            'action': 'onboard_customer',
            'email': customer_email,
            'plan': plan,
        }

        if DRY_RUN:
            app.logger.info('DRY_RUN: would send message to SQS: %s', message)
        else:
            sqs.send_message(QueueUrl=RUN_QUEUE_URL, MessageBody=json.dumps(message))

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=9850)
