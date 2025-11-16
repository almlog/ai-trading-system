#!/usr/bin/env python3
"""
Phase 0: Feature Extraction for News Analysis

Extracts features from news data:
- Sentiment score (VADER/TextBlob)
- Keywords (TF-IDF)
- Topic classification (AI-based)
- Announcement timing

Based on DESIGN_DOC_FINAL.md Section 5.2
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
import numpy as np
from datetime import datetime
import json

# NLP libraries
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class NewsFeatureExtractor:
    """Extract features from financial news"""

    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.tfidf = TfidfVectorizer(max_features=50, stop_words='english')

        # Download required NLTK data
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')

        try:
            nltk.data.find('punkt')
        except LookupError:
            nltk.download('punkt')

    def extract_sentiment(self, text: str) -> Dict[str, float]:
        """
        Extract sentiment score from text

        Returns:
            {
                'sentiment_score': float (-1.0 to +1.0),
                'sentiment_label': str ('Positive', 'Negative', 'Neutral')
            }
        """
        # VADER sentiment
        vader_scores = self.vader.polarity_scores(text)
        compound = vader_scores['compound']

        # TextBlob sentiment (backup)
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity

        # Average of both
        sentiment_score = (compound + textblob_polarity) / 2

        # Label
        if sentiment_score > 0.2:
            label = "Positive"
        elif sentiment_score < -0.2:
            label = "Negative"
        else:
            label = "Neutral"

        return {
            'sentiment_score': round(sentiment_score, 3),
            'sentiment_label': label,
            'vader_compound': round(compound, 3),
            'textblob_polarity': round(textblob_polarity, 3)
        }

    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """
        Extract top keywords from text using TF-IDF
        """
        # Financial domain keywords (hardcoded)
        financial_keywords = [
            'beat', 'miss', 'expectations', 'earnings', 'revenue',
            'guidance', 'raised', 'lowered', 'upgrade', 'downgrade',
            'acquisition', 'merger', 'partnership', 'lawsuit', 'regulation',
            'product', 'launch', 'delay', 'recall', 'innovation'
        ]

        text_lower = text.lower()
        found_keywords = [kw for kw in financial_keywords if kw in text_lower]

        return found_keywords[:top_n]

    def classify_topic(self, text: str) -> str:
        """
        Classify news topic using keyword matching

        Categories:
        - Earnings
        - M&A (Mergers & Acquisitions)
        - Product
        - Legal
        - Other
        """
        text_lower = text.lower()

        if any(kw in text_lower for kw in ['earnings', 'revenue', 'profit', 'eps', 'beat', 'miss']):
            return "Earnings"
        elif any(kw in text_lower for kw in ['acquisition', 'merger', 'acquire', 'buyout']):
            return "M&A"
        elif any(kw in text_lower for kw in ['product', 'launch', 'release', 'innovation']):
            return "Product"
        elif any(kw in text_lower for kw in ['lawsuit', 'regulation', 'investigation', 'legal']):
            return "Legal"
        else:
            return "Other"

    def get_announcement_time(self, timestamp: str) -> str:
        """
        Classify announcement timing

        Returns:
        - 'pre_market': 4:00-9:30 AM ET
        - 'market_hours': 9:30 AM - 4:00 PM ET
        - 'after_market': 4:00-8:00 PM ET
        """
        try:
            dt = pd.to_datetime(timestamp)
            hour = dt.hour

            if 4 <= hour < 9.5:
                return "pre_market"
            elif 9.5 <= hour < 16:
                return "market_hours"
            elif 16 <= hour < 20:
                return "after_market"
            else:
                return "other"
        except:
            return "unknown"

    def extract_all_features(self, news_row: pd.Series) -> Dict[str, Any]:
        """
        Extract all features from a news row

        Args:
            news_row: pandas Series with columns: headline, content, timestamp

        Returns:
            Dictionary of extracted features
        """
        text = str(news_row.get('headline', '')) + " " + str(news_row.get('content', ''))

        sentiment = self.extract_sentiment(text)
        keywords = self.extract_keywords(text)
        topic = self.classify_topic(text)
        timing = self.get_announcement_time(news_row.get('timestamp', ''))

        return {
            'sentiment_score': sentiment['sentiment_score'],
            'sentiment_label': sentiment['sentiment_label'],
            'keywords': keywords,
            'topic': topic,
            'announcement_time': timing
        }


def extract_stock_features(prices_df: pd.DataFrame, symbol: str, date: str) -> Dict[str, float]:
    """
    Extract stock price features

    Args:
        prices_df: DataFrame with OHLCV data
        symbol: Stock symbol
        date: Target date

    Returns:
        {
            'pre_announcement_trend': float,  # 5-day trend %
            'volatility_5d': float,           # 5-day std dev
            'volume_spike': float             # Volume ratio vs previous day
        }
    """
    try:
        target_date = pd.to_datetime(date)

        # Filter for symbol
        symbol_data = prices_df[prices_df['symbol'] == symbol].copy()
        symbol_data['date'] = pd.to_datetime(symbol_data['date'])
        symbol_data = symbol_data.sort_values('date')

        # Get 5 days before target date
        mask = symbol_data['date'] < target_date
        recent = symbol_data[mask].tail(5)

        if len(recent) < 5:
            return {
                'pre_announcement_trend': 0.0,
                'volatility_5d': 0.0,
                'volume_spike': 1.0
            }

        # Calculate features
        first_close = recent.iloc[0]['close']
        last_close = recent.iloc[-1]['close']
        trend = ((last_close - first_close) / first_close) * 100

        volatility = recent['close'].std()

        last_volume = recent.iloc[-1]['volume']
        prev_volume = recent.iloc[-2]['volume']
        volume_ratio = last_volume / prev_volume if prev_volume > 0 else 1.0

        return {
            'pre_announcement_trend': round(trend, 2),
            'volatility_5d': round(volatility, 2),
            'volume_spike': round(volume_ratio, 2)
        }

    except Exception as e:
        print(f"Error extracting stock features: {e}")
        return {
            'pre_announcement_trend': 0.0,
            'volatility_5d': 0.0,
            'volume_spike': 1.0
        }


if __name__ == "__main__":
    print("Feature Extraction Module")
    print("Import this module in your analysis scripts")
