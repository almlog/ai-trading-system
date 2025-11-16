"""
Phase 1: AI Analysis Engine

Uses AWS Bedrock (Claude Haiku) to analyze news/market conditions
and make trading decisions based on discovered patterns.
Based on DESIGN_DOC_FINAL.md Section 5.6
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from lambda.utils.aws_clients import AWSClients, get_ssm_parameter
from lambda.utils.constants import SSM_PARAMS


def lambda_handler(event, context):
    """
    Lambda handler for AI analysis

    Triggered by: unified_judgment_lambda
    """

    print("=== AI Analysis Lambda ===")
    print(f"Event: {json.dumps(event)}")

    detail = event.get('detail', event)  # Support both EventBridge and direct invocation
    trigger_type = detail.get('trigger_type')

    if not trigger_type:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing trigger_type'})
        }

    # Load patterns from SSM
    patterns = load_patterns()
    if not patterns:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to load patterns'})
        }

    # Load realtime analysis prompt
    prompt_template = load_prompt()
    if not prompt_template:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to load prompt'})
        }

    # Analyze with Claude
    analysis_result = analyze_with_claude(detail, patterns, prompt_template)

    # Decide action
    if should_enter_position(analysis_result):
        # TODO: Invoke position_manager_lambda
        print(f"✓ RECOMMENDED ACTION: {analysis_result.get('action')}")
        print(f"  Pattern: {analysis_result.get('matched_pattern_id')}")
        print(f"  Confidence: {analysis_result.get('confidence')}")
    else:
        print(f"⊘ No action (confidence too low or criteria not met)")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Analysis complete',
            'result': analysis_result
        })
    }


def load_patterns() -> Optional[Dict]:
    """Load patterns from SSM Parameter Store"""

    try:
        patterns_json = get_ssm_parameter(SSM_PARAMS['patterns'])
        if patterns_json:
            return json.loads(patterns_json)
        return None
    except Exception as e:
        print(f"Error loading patterns: {e}")
        return None


def load_prompt() -> Optional[str]:
    """Load realtime analysis prompt from SSM"""

    try:
        return get_ssm_parameter(SSM_PARAMS['prompt_realtime_analysis'])
    except Exception as e:
        print(f"Error loading prompt: {e}")
        return None


def analyze_with_claude(
    detail: Dict,
    patterns: Dict,
    prompt_template: str
) -> Dict[str, Any]:
    """
    Analyze with AWS Bedrock Claude

    Args:
        detail: Event detail (news/volatility data)
        patterns: Discovered patterns from Phase 0
        prompt_template: Prompt template from SSM

    Returns:
        {
            "matched_pattern_id": str,
            "match_score": int (0-100),
            "action": str (Buy/Sell/Hold),
            "confidence": str (High/Medium/Low),
            "reasoning": str,
            "entry_price": float,
            "target_profit": float,
            "stop_loss": float
        }
    """

    try:
        # Build prompt
        prompt = build_realtime_prompt(detail, patterns, prompt_template)

        # Invoke Bedrock
        bedrock = AWSClients.get_bedrock()

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "temperature": 0.3,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps(request_body)
        )

        response_body = json.loads(response['body'].read())
        result_text = response_body['content'][0]['text']

        # Parse JSON from response
        json_start = result_text.find('{')
        json_end = result_text.rfind('}') + 1
        json_str = result_text[json_start:json_end]

        analysis = json.loads(json_str)

        print(f"Claude analysis: {analysis.get('action')} (confidence: {analysis.get('confidence')})")

        return analysis

    except Exception as e:
        print(f"Error analyzing with Claude: {e}")
        return {
            "matched_pattern_id": "error",
            "match_score": 0,
            "action": "Hold",
            "confidence": "Low",
            "reasoning": f"Analysis error: {str(e)}",
            "entry_price": 0,
            "target_profit": 0,
            "stop_loss": 0
        }


def build_realtime_prompt(
    detail: Dict,
    patterns: Dict,
    template: str
) -> str:
    """Build prompt with current data"""

    # Extract relevant data from detail
    symbol = detail.get('symbol', 'UNKNOWN')
    trigger_type = detail.get('trigger_type')

    # Get current market data (placeholder)
    # TODO: Fetch real market data
    current_price = detail.get('current_price', 0)
    pre_trend = 0.0
    volume_ratio = 1.0

    # Format prompt
    prompt = template.format(
        patterns_from_phase0=json.dumps(patterns, indent=2),
        headline=detail.get('news', {}).get('headline', 'N/A'),
        content=detail.get('news', {}).get('summary', 'N/A'),
        symbol=symbol,
        timestamp=datetime.utcnow().isoformat(),
        current_price=current_price,
        pre_trend=pre_trend,
        volume_ratio=volume_ratio
    )

    return prompt


def should_enter_position(analysis: Dict) -> bool:
    """
    Determine if should enter position

    Criteria (DESIGN_DOC_FINAL.md Section 5.7):
    - confidence == "High"
    - match_score >= 80
    - circuit_breaker_ok() (already checked)
    - no_existing_position_for_symbol() (TODO)
    """

    confidence = analysis.get('confidence')
    match_score = analysis.get('match_score', 0)
    action = analysis.get('action')

    if confidence != "High":
        return False

    if match_score < 80:
        return False

    if action == "Hold":
        return False

    # TODO: Check if position already exists for symbol

    return True
