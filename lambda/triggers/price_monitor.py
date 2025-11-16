"""
Phase 1: Price Monitor Lambda (Pattern B Trigger)

Monitors stock price volatility every 1 minute.
Triggers analysis when price moves ±2% (or ±2.5% for AMZN/NVDA)
Based on DESIGN_DOC_FINAL.md Section 4.2 (Pattern B)
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import requests

from lambda.utils.constants import SYMBOLS, VOLATILITY_THRESHOLDS, API_ENDPOINTS
from lambda.utils.aws_clients import put_eventbridge_event


def lambda_handler(event, context):
    """
    Lambda handler for price monitoring

    Triggered by: EventBridge Scheduler (every 1 minute)
    """

    print("=== Price Monitor Lambda ===")

    # Get API key
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'ALPHA_VANTAGE_API_KEY not set'})
        }

    triggered_symbols = []

    # Check each symbol
    for symbol in SYMBOLS:
        volatility = check_volatility(symbol, api_key)

        if volatility and volatility['triggered']:
            trigger_analysis(symbol, volatility)
            triggered_symbols.append(symbol)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Monitored {len(SYMBOLS)} symbols',
            'triggered': triggered_symbols,
            'count': len(triggered_symbols)
        })
    }


def check_volatility(symbol: str, api_key: str) -> Optional[Dict]:
    """
    Check if symbol exceeded volatility threshold

    Returns:
        {
            'triggered': bool,
            'current_price': float,
            'change_pct': float,
            'threshold': float
        }
    """

    try:
        # Alpha Vantage: Global Quote
        # https://www.alphavantage.co/documentation/

        url = f"{API_ENDPOINTS['alpha_vantage_quote']}?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if 'Global Quote' not in data:
            print(f"No data for {symbol}")
            return None

        quote = data['Global Quote']

        current_price = float(quote.get('05. price', 0))
        change_pct = float(quote.get('10. change percent', '0').replace('%', ''))

        threshold = VOLATILITY_THRESHOLDS.get(symbol, 2.0)

        triggered = abs(change_pct) >= threshold

        return {
            'triggered': triggered,
            'current_price': current_price,
            'change_pct': change_pct,
            'threshold': threshold
        }

    except Exception as e:
        print(f"Error checking volatility for {symbol}: {e}")
        return None


def trigger_analysis(symbol: str, volatility: Dict):
    """Send event to EventBridge"""

    try:
        put_eventbridge_event(
            source='ai-trading.price-monitor',
            detail_type='VolatilityDetected',
            detail={
                'trigger_type': 'volatility',
                'symbol': symbol,
                'current_price': volatility['current_price'],
                'change_pct': volatility['change_pct'],
                'threshold': volatility['threshold']
            }
        )

        print(f"Triggered analysis for {symbol}: {volatility['change_pct']:.2f}% (threshold: {volatility['threshold']}%)")

    except Exception as e:
        print(f"Error triggering analysis: {e}")
