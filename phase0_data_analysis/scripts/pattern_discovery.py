#!/usr/bin/env python3
"""
Phase 0: AI-Powered Pattern Discovery (A案)

Uses Claude API to discover "golden patterns" from historical data.
Based on DESIGN_DOC_FINAL.md Section 5.3
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
from dotenv import load_dotenv
from anthropic import Anthropic

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from phase0_data_analysis.scripts.feature_extraction import NewsFeatureExtractor, extract_stock_features

# Load environment variables
load_dotenv(project_root / ".env")


class PatternDiscoveryEngine:
    """AI-powered pattern discovery using Claude"""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file")

        self.client = Anthropic(api_key=api_key)
        self.feature_extractor = NewsFeatureExtractor()

    def prepare_training_data(
        self,
        news_df: pd.DataFrame,
        prices_df: pd.DataFrame,
        max_samples: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Prepare training data with features

        Args:
            news_df: News data with columns: date, headline, content, symbol
            prices_df: Price data with columns: date, symbol, open, high, low, close, volume
            max_samples: Maximum number of samples to use

        Returns:
            List of feature dictionaries
        """
        print("Extracting features from historical data...")

        training_data = []

        for idx, row in news_df.head(max_samples).iterrows():
            try:
                # Extract news features
                news_features = self.feature_extractor.extract_all_features(row)

                # Extract stock features
                stock_features = extract_stock_features(
                    prices_df,
                    row['symbol'],
                    row['date']
                )

                # Calculate price movement after news (1 hour, 1 day)
                # (Simplified - in real implementation, need precise timing)
                price_change = self._calculate_price_change(
                    prices_df,
                    row['symbol'],
                    row['date']
                )

                combined = {
                    **news_features,
                    **stock_features,
                    **price_change,
                    'symbol': row['symbol'],
                    'date': str(row['date'])
                }

                training_data.append(combined)

                if (idx + 1) % 100 == 0:
                    print(f"  Processed {idx + 1} samples...")

            except Exception as e:
                print(f"  Warning: Failed to process row {idx}: {e}")
                continue

        print(f"✓ Prepared {len(training_data)} training samples\n")
        return training_data

    def _calculate_price_change(
        self,
        prices_df: pd.DataFrame,
        symbol: str,
        date: str
    ) -> Dict[str, float]:
        """Calculate price change after news announcement"""
        try:
            target_date = pd.to_datetime(date)

            symbol_data = prices_df[prices_df['symbol'] == symbol].copy()
            symbol_data['date'] = pd.to_datetime(symbol_data['date'])

            # Get current and next day price
            current = symbol_data[symbol_data['date'] == target_date]
            next_day = symbol_data[symbol_data['date'] > target_date].head(1)

            if current.empty or next_day.empty:
                return {'price_change_pct': 0.0, 'direction': 'Hold'}

            current_close = current.iloc[0]['close']
            next_close = next_day.iloc[0]['close']

            change_pct = ((next_close - current_close) / current_close) * 100

            if change_pct > 1.0:
                direction = "Up"
            elif change_pct < -1.0:
                direction = "Down"
            else:
                direction = "Hold"

            return {
                'price_change_pct': round(change_pct, 2),
                'direction': direction
            }

        except Exception as e:
            return {'price_change_pct': 0.0, 'direction': 'Hold'}

    def discover_patterns(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Use Claude API to discover patterns

        Returns:
            {
                "patterns": [
                    {
                        "pattern_id": "...",
                        "name": "...",
                        "conditions": [...],
                        "prediction": {...},
                        "sample_size": int,
                        "hypothesis": "..."
                    }
                ]
            }
        """
        print("Requesting pattern discovery from Claude API...")

        # Prepare prompt (from DESIGN_DOC_FINAL.md Section 5.3)
        prompt = self._build_discovery_prompt(training_data)

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8000,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse JSON response
            result_text = response.content[0].text

            # Extract JSON from response
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            json_str = result_text[json_start:json_end]

            patterns = json.loads(json_str)

            print(f"✓ Discovered {len(patterns.get('patterns', []))} patterns\n")
            return patterns

        except Exception as e:
            print(f"ERROR: Pattern discovery failed: {e}")
            return {"patterns": []}

    def _build_discovery_prompt(self, training_data: List[Dict[str, Any]]) -> str:
        """Build prompt for Claude API"""

        # Convert training data to JSON
        data_json = json.dumps(training_data[:100], indent=2)  # Limit to 100 samples

        prompt = f"""あなたは金融データサイエンティストです。

【データ】
以下は過去1年分の「ニュースの特徴量」と「その後の株価変動」のペアです。

{data_json}

【あなたのタスク】
「どのような特徴のニュース」が「どのような市場状況」で発表されると、
「株価がどう動くか」の相関パターンを発見してください。

【求める出力】
以下のJSON形式で、5-10個のパターンを報告してください。

{{
  "patterns": [
    {{
      "pattern_id": "earnings_beat_selloff",
      "name": "好決算後の利益確定売り",
      "conditions": [
        "sentiment_score > 0.5",
        "pre_announcement_trend > 5.0",
        "topic == 'Earnings'"
      ],
      "prediction": {{
        "direction": "Down",
        "magnitude": "-2% within 1 hour",
        "confidence": 0.72
      }},
      "sample_size": 23,
      "hypothesis": "材料出尽くし。短期筋の利益確定"
    }}
  ]
}}

【制約】
- 統計的に有意なパターンのみ（最低10件以上の事例）
- 各パターンには「なぜそうなるか」の仮説を必ず付ける
- confidence は 0.0-1.0 の範囲
- 必ずJSONのみを返してください（説明文は不要）"""

        return prompt


def main():
    """Main execution"""

    print("=== Phase 0: Pattern Discovery (A案) ===\n")

    # Check data files
    data_dir = Path(__file__).parent.parent / "data"

    print("NOTE: This is a template script.")
    print("You need to:")
    print("  1. Download Kaggle datasets: make phase0-download-data")
    print("  2. Update file paths below to match your actual data files")
    print("  3. Ensure data has required columns\n")

    # Placeholder - update these paths
    news_file = data_dir / "news.csv"  # Update with actual filename
    prices_file = data_dir / "stock_prices.csv"  # Update with actual filename

    if not news_file.exists() or not prices_file.exists():
        print("ERROR: Data files not found!")
        print(f"  News: {news_file}")
        print(f"  Prices: {prices_file}")
        print("\nRun: make phase0-download-data")
        sys.exit(1)

    # Load data
    print("Loading datasets...")
    news_df = pd.read_csv(news_file)
    prices_df = pd.read_csv(prices_file)
    print(f"  News: {len(news_df)} rows")
    print(f"  Prices: {len(prices_df)} rows\n")

    # Initialize engine
    engine = PatternDiscoveryEngine()

    # Prepare training data
    training_data = engine.prepare_training_data(news_df, prices_df, max_samples=200)

    # Discover patterns
    patterns = engine.discover_patterns(training_data)

    # Save results
    output_dir = Path(__file__).parent.parent / "outputs"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "patterns_v1.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, indent=2, ensure_ascii=False)

    print(f"✓ Patterns saved to: {output_file}")
    print("\n=== Pattern Discovery Complete ===")
    print(f"Discovered {len(patterns.get('patterns', []))} patterns")
    print("\nNext steps:")
    print("  1. Review patterns: cat phase0_data_analysis/outputs/patterns_v1.json")
    print("  2. Validate patterns: make phase0-validate")
    print("  3. Proceed to Phase 1: Lambda deployment")


if __name__ == "__main__":
    main()
