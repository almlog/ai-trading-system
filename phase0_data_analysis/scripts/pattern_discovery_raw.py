#!/usr/bin/env python3
"""
Phase 2: AI-Powered Pattern Discovery (B案 - Raw Data)

Uses Claude API to discover patterns from RAW data (no feature engineering).
Goal: Let AI find features humans might miss.
Based on DESIGN_DOC_FINAL.md Section 5.11
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

# Load environment variables
load_dotenv(project_root / ".env")


class RawPatternDiscoveryEngine:
    """AI-powered pattern discovery using raw data (B案)"""

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file")

        self.client = Anthropic(api_key=api_key)

    def prepare_raw_data(
        self,
        news_df: pd.DataFrame,
        prices_df: pd.DataFrame,
        max_samples: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Prepare raw data WITHOUT feature engineering

        Args:
            news_df: News data
            prices_df: Price data
            max_samples: Maximum samples

        Returns:
            List of raw data dictionaries
        """
        print("Preparing RAW data (no feature engineering)...")

        raw_data = []

        for idx, row in news_df.head(max_samples).iterrows():
            try:
                # NO feature extraction - just raw data
                news_text = f"{row.get('headline', '')} {row.get('content', '')}"

                # Get price change (simple)
                price_change = self._get_price_change(
                    prices_df,
                    row['symbol'],
                    row['date']
                )

                raw_item = {
                    'news_text': news_text,
                    'symbol': row['symbol'],
                    'timestamp': str(row['date']),
                    'price_change_pct': price_change['change_pct'],
                    'direction': price_change['direction']
                }

                raw_data.append(raw_item)

                if (idx + 1) % 50 == 0:
                    print(f"  Processed {idx + 1} samples...")

            except Exception as e:
                print(f"  Warning: Failed to process row {idx}: {e}")
                continue

        print(f"✓ Prepared {len(raw_data)} raw samples\n")
        return raw_data

    def _get_price_change(
        self,
        prices_df: pd.DataFrame,
        symbol: str,
        date: str
    ) -> Dict[str, Any]:
        """Get price change after news (simplified)"""

        try:
            target_date = pd.to_datetime(date)

            symbol_data = prices_df[prices_df['symbol'] == symbol].copy()
            symbol_data['date'] = pd.to_datetime(symbol_data['date'])

            current = symbol_data[symbol_data['date'] == target_date]
            next_day = symbol_data[symbol_data['date'] > target_date].head(1)

            if current.empty or next_day.empty:
                return {'change_pct': 0.0, 'direction': 'Hold'}

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
                'change_pct': round(change_pct, 2),
                'direction': direction
            }

        except Exception as e:
            return {'change_pct': 0.0, 'direction': 'Hold'}

    def discover_patterns_raw(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Use Claude to discover patterns from RAW data

        Returns:
            {
                "patterns": [
                    {
                        "pattern_id": str,
                        "discovered_feature": str,
                        "correlation": str,
                        "sample_size": int,
                        "hypothesis": str
                    }
                ]
            }
        """

        print("Requesting raw pattern discovery from Claude API...")

        prompt = self._build_raw_discovery_prompt(raw_data)

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

            result_text = response.content[0].text

            # Extract JSON
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            json_str = result_text[json_start:json_end]

            patterns = json.loads(json_str)

            print(f"✓ Discovered {len(patterns.get('patterns', []))} raw patterns\n")
            return patterns

        except Exception as e:
            print(f"ERROR: Raw pattern discovery failed: {e}")
            return {"patterns": []}

    def _build_raw_discovery_prompt(self, raw_data: List[Dict[str, Any]]) -> str:
        """Build prompt for raw data discovery (from DESIGN_DOC Section 5.11)"""

        data_json = json.dumps(raw_data[:100], indent=2)

        prompt = f"""あなたは金融データサイエンティストです。

【データ】
以下は過去1年分の「ニュース記事（生テキスト）」と「その後の株価変動」です。

{data_json}

【重要な指示】
私（人間）は、あなたに「特徴量」を与えていません。
あなた自身が、生のテキストと数値から「隠れたパターン」を発見してください。

例えば：
- 「特定の言い回し」（例："guidance was raised" vs "raised guidance"）
- 「文章の長さ」や「数字の出現頻度」
- 「発表時刻」や「曜日」との相関
- その他、人間が気づかない特徴

【求める出力】
以下のJSON形式で、発見したパターンを報告してください。

{{
  "patterns": [
    {{
      "pattern_id": "unique_pattern_id",
      "discovered_feature": "ニュースの最初の段落に'however'が含まれる",
      "correlation": "この特徴がある場合、67%の確率で1時間後に-1.5%下落",
      "sample_size": 15,
      "hypothesis": "最初に好材料を述べ、'however'で反転する記事は市場がネガティブと解釈しやすい"
    }}
  ]
}}

【制約】
- 統計的に有意なパターンのみ（最低10件以上の事例）
- 人間が想定しない「新しい視点」を重視
- 必ずJSONのみを返してください"""

        return prompt


def main():
    """Main execution for Phase 2"""

    print("=== Phase 2: Raw Pattern Discovery (B案) ===\n")

    # Check data files
    data_dir = Path(__file__).parent.parent / "data"

    news_file = data_dir / "news.csv"
    prices_file = data_dir / "stock_prices.csv"

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
    engine = RawPatternDiscoveryEngine()

    # Prepare RAW data
    raw_data = engine.prepare_raw_data(news_df, prices_df, max_samples=200)

    # Discover patterns
    patterns = engine.discover_patterns_raw(raw_data)

    # Save results
    output_dir = Path(__file__).parent.parent / "outputs"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "patterns_v2_raw.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, indent=2, ensure_ascii=False)

    print(f"✓ Raw patterns saved to: {output_file}")
    print("\n=== Raw Pattern Discovery Complete ===")
    print(f"Discovered {len(patterns.get('patterns', []))} raw patterns")
    print("\nNext steps:")
    print("  1. Review patterns: cat phase0_data_analysis/outputs/patterns_v2_raw.json")
    print("  2. Compare with A案: make phase2-compare")


if __name__ == "__main__":
    main()
