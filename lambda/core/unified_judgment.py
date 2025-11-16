"""
Phase 1: Unified Judgment Lambda

Receives events from all trigger patterns, checks circuit breaker,
and delegates to AI analysis engine.
Based on DESIGN_DOC_FINAL.md Section 4.1
"""

import json
from datetime import datetime
from typing import Dict, Any

from lambda.utils.circuit_breaker import CircuitBreaker
from lambda.utils.aws_clients import get_table
from lambda.utils.constants import DYNAMODB_TABLES


def lambda_handler(event, context):
    """
    Lambda handler for unified judgment

    Triggered by: EventBridge custom events from:
    - news_fetch_lambda
    - price_monitor_lambda
    - calendar_checker_lambda
    """

    print("=== Unified Judgment Lambda ===")
    print(f"Event: {json.dumps(event)}")

    # Parse event
    detail = event.get('detail', {})
    trigger_type = detail.get('trigger_type')

    if not trigger_type:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing trigger_type'})
        }

    # Initialize circuit breaker
    circuit_breaker = CircuitBreaker()

    # Check circuit breaker
    check_result = circuit_breaker.check(trigger_type)

    if not check_result['allowed']:
        print(f"❌ Circuit breaker blocked: {check_result['reason']}")

        # Send notification
        send_notification(f"Circuit breaker: {check_result['reason']}")

        return {
            'statusCode': 429,  # Too Many Requests
            'body': json.dumps({
                'message': 'Circuit breaker blocked',
                'reason': check_result['reason']
            })
        }

    print(f"✓ Circuit breaker passed")

    # Log trigger
    circuit_breaker.log_trigger(trigger_type, detail)

    # Delegate to AI analysis
    analysis_result = invoke_ai_analysis(detail)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Judgment complete',
            'trigger_type': trigger_type,
            'analysis_result': analysis_result
        })
    }


def invoke_ai_analysis(detail: Dict[str, Any]) -> Dict:
    """
    Invoke AI analysis lambda

    In production, this would invoke another Lambda function.
    For template, we return a placeholder.
    """

    # TODO: Implement actual Lambda invocation
    # import boto3
    # lambda_client = boto3.client('lambda')
    # response = lambda_client.invoke(
    #     FunctionName='ai-trading-ai-analysis',
    #     InvocationType='Event',
    #     Payload=json.dumps(detail)
    # )

    print(f"Delegating to AI analysis: {detail.get('trigger_type')}")

    return {
        'delegated': True,
        'timestamp': datetime.utcnow().isoformat()
    }


def send_notification(message: str):
    """Send SNS notification"""

    try:
        from lambda.utils.aws_clients import AWSClients

        sns = AWSClients.get_sns()
        topic_arn = os.environ.get('SNS_TOPIC_ARN')

        if topic_arn:
            sns.publish(
                TopicArn=topic_arn,
                Subject='AI Trading System Alert',
                Message=message
            )

    except Exception as e:
        print(f"Error sending notification: {e}")
