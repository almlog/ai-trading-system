#!/usr/bin/env python3
"""
Phase 2: Compare A案 vs B案 Patterns

Compares feature-engineered patterns (A) vs raw data patterns (B)
Based on DESIGN_DOC_FINAL.md Section 5.12
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def load_patterns(file_path: Path) -> Dict:
    """Load patterns from JSON file"""

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        return {"patterns": []}
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {file_path}: {e}")
        return {"patterns": []}


def analyze_patterns(patterns: Dict, label: str) -> Dict[str, Any]:
    """Analyze pattern characteristics"""

    pattern_list = patterns.get('patterns', [])

    if not pattern_list:
        return {
            "label": label,
            "count": 0,
            "avg_confidence": 0.0,
            "avg_sample_size": 0,
            "min_sample_size": 0,
            "max_sample_size": 0
        }

    # Calculate statistics
    confidences = []
    sample_sizes = []

    for p in pattern_list:
        # For A案 (feature-engineered)
        if 'prediction' in p and 'confidence' in p['prediction']:
            confidences.append(p['prediction']['confidence'])

        # For B案 (raw data) - different structure
        # Confidence is implicit in correlation description

        sample_sizes.append(p.get('sample_size', 0))

    return {
        "label": label,
        "count": len(pattern_list),
        "avg_confidence": sum(confidences) / len(confidences) if confidences else 0.0,
        "avg_sample_size": sum(sample_sizes) / len(sample_sizes) if sample_sizes else 0,
        "min_sample_size": min(sample_sizes) if sample_sizes else 0,
        "max_sample_size": max(sample_sizes) if sample_sizes else 0,
        "patterns": pattern_list
    }


def find_novel_patterns(a_patterns: Dict, b_patterns: Dict) -> List[Dict]:
    """
    Find patterns in B案 that are novel (not found in A案)

    Returns:
        List of novel pattern descriptions
    """

    a_list = a_patterns.get('patterns', [])
    b_list = b_patterns.get('patterns', [])

    # Extract pattern features from A案
    a_features = set()
    for p in a_list:
        # Get condition keywords
        conditions = p.get('conditions', [])
        for cond in conditions:
            # Extract feature names (simplified)
            if 'sentiment' in cond.lower():
                a_features.add('sentiment')
            if 'topic' in cond.lower():
                a_features.add('topic')
            if 'trend' in cond.lower():
                a_features.add('trend')
            if 'volume' in cond.lower():
                a_features.add('volume')

    # Check B案 for novel features
    novel = []
    for p in b_list:
        discovered = p.get('discovered_feature', '').lower()

        is_novel = True
        for a_feature in a_features:
            if a_feature in discovered:
                is_novel = False
                break

        if is_novel:
            novel.append({
                "pattern_id": p.get('pattern_id', 'unknown'),
                "discovered_feature": p.get('discovered_feature', 'N/A'),
                "hypothesis": p.get('hypothesis', 'N/A'),
                "sample_size": p.get('sample_size', 0)
            })

    return novel


def generate_comparison_report(a_stats: Dict, b_stats: Dict, novel: List[Dict]) -> str:
    """Generate comparison report in Markdown"""

    report = f"""# Phase 2: A案 vs B案 パターン比較レポート

**生成日時**: {Path(__file__).stat().st_mtime}

---

## 📊 統計サマリー

| 項目 | A案（特徴量） | B案（生データ） |
|------|--------------|----------------|
| 発見パターン数 | {a_stats['count']}個 | {b_stats['count']}個 |
| 平均サンプル数 | {a_stats['avg_sample_size']:.1f}件 | {b_stats['avg_sample_size']:.1f}件 |
| 最小サンプル数 | {a_stats['min_sample_size']}件 | {b_stats['min_sample_size']}件 |
| 最大サンプル数 | {a_stats['max_sample_size']}件 | {b_stats['max_sample_size']}件 |
| 平均信頼度 | {a_stats['avg_confidence']:.2f} | N/A (構造が異なる) |

---

## 🆕 B案で新たに発見されたパターン

B案でのみ発見された「人間が想定しなかった特徴」:

"""

    if novel:
        for idx, pattern in enumerate(novel, 1):
            report += f"""
### {idx}. {pattern['pattern_id']}

- **発見特徴**: {pattern['discovered_feature']}
- **仮説**: {pattern['hypothesis']}
- **サンプル数**: {pattern['sample_size']}件

"""
    else:
        report += "\n（新規パターンなし - A案とB案で同様の特徴を発見）\n"

    report += """
---

## 🎯 評価と推奨

"""

    # Evaluation logic
    if b_stats['count'] > a_stats['count'] and len(novel) > 0:
        report += """
### 評価: B案が優秀

- B案は人間が想定しない特徴を発見した
- パターン数もB案が多い
- **推奨**: Phase 3でB案を採用し、システムに統合

"""
    elif a_stats['count'] > b_stats['count'] and len(novel) == 0:
        report += """
### 評価: A案が依然優秀

- A案の特徴量エンジニアリングは有効
- B案は新規パターンを発見できなかった
- **推奨**: Phase 1のシステムを継続使用

"""
    else:
        report += """
### 評価: ハイブリッドが最適

- A案とB案はそれぞれ異なる強みを持つ
- **推奨**: 両方のパターンを統合し、信頼度が高い方を採用する仕組みを構築

"""

    report += """
---

## 📖 詳細パターンリスト

### A案パターン

"""

    for idx, pattern in enumerate(a_stats['patterns'][:5], 1):  # Show top 5
        report += f"""
**{idx}. {pattern.get('name', 'N/A')}**
- Pattern ID: `{pattern.get('pattern_id', 'N/A')}`
- サンプル数: {pattern.get('sample_size', 0)}件
- 条件: {', '.join(pattern.get('conditions', []))}

"""

    report += """
### B案パターン

"""

    for idx, pattern in enumerate(b_stats['patterns'][:5], 1):
        report += f"""
**{idx}. {pattern.get('pattern_id', 'N/A')}**
- 発見特徴: {pattern.get('discovered_feature', 'N/A')}
- サンプル数: {pattern.get('sample_size', 0)}件
- 相関: {pattern.get('correlation', 'N/A')}

"""

    report += "\n---\n\n**レポート終了**\n"

    return report


def main():
    """Main execution"""

    print("=== Phase 2: A案 vs B案 比較分析 ===\n")

    # Load patterns
    project_root = Path(__file__).parent.parent
    a_file = project_root / "phase0_data_analysis" / "outputs" / "patterns_v1.json"
    b_file = project_root / "phase0_data_analysis" / "outputs" / "patterns_v2_raw.json"

    print(f"Loading A案 patterns: {a_file}")
    a_patterns = load_patterns(a_file)

    print(f"Loading B案 patterns: {b_file}")
    b_patterns = load_patterns(b_file)

    if not a_patterns.get('patterns') or not b_patterns.get('patterns'):
        print("\nERROR: One or both pattern files are missing or empty!")
        print("  A案: Run 'make phase0-analyze'")
        print("  B案: Run 'make phase2-analyze-raw'")
        sys.exit(1)

    # Analyze
    print("\nAnalyzing patterns...")
    a_stats = analyze_patterns(a_patterns, "A案（特徴量）")
    b_stats = analyze_patterns(b_patterns, "B案（生データ）")

    # Find novel patterns
    print("Finding novel patterns...")
    novel = find_novel_patterns(a_patterns, b_patterns)

    # Generate report
    print("Generating comparison report...")
    report = generate_comparison_report(a_stats, b_stats, novel)

    # Save report
    output_dir = project_root / "claudedocs"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "phase2_ab_comparison_report.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✓ Comparison report saved to: {output_file}")
    print(f"\n=== Comparison Complete ===")
    print(f"A案: {a_stats['count']} patterns")
    print(f"B案: {b_stats['count']} patterns")
    print(f"Novel patterns in B案: {len(novel)}")
    print(f"\nView report: cat {output_file}")


if __name__ == "__main__":
    main()
