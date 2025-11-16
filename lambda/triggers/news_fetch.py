"""
Phase 1: News Fetch Lambda (Pattern A Trigger)

Fetches news from Finnhub API every 5 minutes and triggers analysis for new news.
Based on DESIGN_DOC_FINAL.md Section 4.2 (Pattern A)
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests

from lambda.utils.constants import SYMBOLS, API_ENDPOINTS, DYNAMODB_TABLES, S3_BUCKETS
from lambda.utils.aws_clients import get_table, get_s3, put_eventbridge_event


def lambda_handler(event, context):
    """
    Lambda handler for news fetching

    Triggered by: EventBridge Scheduler (every 5 minutes)
    """

    print("=== News Fetch Lambda ===")
    print(f"Event: {json.dumps(event)}")

    # Get API key from environment
    api_key = os.environ.get('FINNHUB_API_KEY')
    if not api_key:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'FINNHUB_API_KEY not set'})
        }

    # Initialize
    trigger_table = get_table(DYNAMODB_TABLES['trigger_history'])
    s3 = get_s3()

    # Get last fetch timestamp
    last_fetch_time = get_last_fetch_timestamp(trigger_table)

    # Fetch news for each symbol
    all_news = []
    for symbol in SYMBOLS:
        news_items = fetch_news_for_symbol(symbol, api_key, last_fetch_time)
        all_news.extend(news_items)

    print(f"Fetched {len(all_news)} new news items")

    if len(all_news) == 0:
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'No new news found'})
        }

    # Save to S3
    save_news_to_s3(all_news, s3)

    # Update last fetch timestamp
    update_last_fetch_timestamp(trigger_table)

    # Trigger analysis for important news
    for news_item in all_news:
        if is_important_news(news_item):
            trigger_analysis(news_item)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Processed {len(all_news)} news items',
            'count': len(all_news)
        })
    }


def fetch_news_for_symbol(symbol: str, api_key: str, from_time: str) -> List[Dict[str, Any]]:
    """Fetch news from Finnhub API"""

    try:
        # Finnhub API: Company News
        # https://finnhub.io/docs/api/company-news

        to_date = datetime.utcnow().date().isoformat()
        from_date = (datetime.utcnow() - timedelta(days=1)).date().isoformat()

        url = f"{API_ENDPOINTS['finnhub_news']}?symbol={symbol}&from={from_date}&to={to_date}&token={api_key}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        news_items = response.json()

        # Filter by timestamp
        from_timestamp = datetime.fromisoformat(from_time).timestamp()
        filtered = [
            item for item in news_items
            if item.get('datetime', 0) > from_timestamp
        ]

        return filtered

    except Exception as e:
        print(f"Error fetching news for {symbol}: {e}")
        return []


def get_last_fetch_timestamp(table) -> str:
    """Get last fetch timestamp from DynamoDB"""

    try:
        response = table.get_item(
            Key={'trigger_id': 'news_fetch_last_timestamp'}
        )

        if 'Item' in response:
            return response['Item']['timestamp']
        else:
            # Default: 1 hour ago
            return (datetime.utcnow() - timedelta(hours=1)).isoformat()

    except Exception as e:
        print(f"Error getting last fetch timestamp: {e}")
        return (datetime.utcnow() - timedelta(hours=1)).isoformat()


def update_last_fetch_timestamp(table):
    """Update last fetch timestamp in DynamoDB"""

    try:
        table.put_item(
            Item={
                'trigger_id': 'news_fetch_last_timestamp',
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        print(f"Error updating last fetch timestamp: {e}")


def save_news_to_s3(news_items: List[Dict], s3_client):
    """Save news to S3 archive"""

    try:
        timestamp = datetime.utcnow().isoformat()
        key = f"news/{timestamp}.json"

        s3_client.put_object(
            Bucket=S3_BUCKETS['news_archive'],
            Key=key,
            Body=json.dumps(news_items, indent=2),
            ContentType='application/json'
        )

        print(f"Saved news to S3: s3://{S3_BUCKETS['news_archive']}/{key}")

    except Exception as e:
        print(f"Error saving news to S3: {e}")


def is_important_news(news_item: Dict) -> bool:
    """
    Filter important news

    Criteria:
    - Contains earnings keywords
    - High category (if available)
    """

    headline = news_item.get('headline', '').lower()
    summary = news_item.get('summary', '').lower()
    category = news_item.get('category', '')

    # Keywords
    important_keywords = [
        'earnings', 'revenue', 'profit', 'guidance',
        'acquisition', 'merger', 'lawsuit', 'fda',
        'downgrade', 'upgrade', 'rating'
    ]

    text = f"{headline} {summary}"

    has_keyword = any(kw in text for kw in important_keywords)
    is_high_category = category in ['Earnings', 'M&A', 'Legal']

    return has_keyword or is_high_category


def trigger_analysis(news_item: Dict):
    """Send event to EventBridge to trigger unified judgment lambda"""

    try:
        put_eventbridge_event(
            source='ai-trading.news-fetch',
            detail_type='NewNewsDetected',
            detail={
                'trigger_type': 'news',
                'news': news_item
            }
        )

        print(f"Triggered analysis for: {news_item.get('headline', 'N/A')}")

    except Exception as e:
        print(f"Error triggering analysis: {e}")
