#!/usr/bin/env python3
"""
Phase 0: Validate Discovered Patterns

Validates that patterns_v1.json:
1. Has correct JSON structure
2. Each pattern has required fields
3. Sample sizes are sufficient (>=10)
4. Confidence scores are valid (0.0-1.0)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def validate_pattern_structure(pattern: Dict[str, Any], idx: int) -> List[str]:
    """Validate a single pattern's structure"""

    errors = []
    required_fields = [
        'pattern_id',
        'name',
        'conditions',
        'prediction',
        'sample_size',
        'hypothesis'
    ]

    # Check required fields
    for field in required_fields:
        if field not in pattern:
            errors.append(f"Pattern {idx}: Missing field '{field}'")

    # Validate prediction structure
    if 'prediction' in pattern:
        pred = pattern['prediction']
        pred_required = ['direction', 'magnitude', 'confidence']

        for field in pred_required:
            if field not in pred:
                errors.append(f"Pattern {idx}: Missing prediction.{field}")

        # Validate confidence
        if 'confidence' in pred:
            conf = pred['confidence']
            if not isinstance(conf, (int, float)) or not (0.0 <= conf <= 1.0):
                errors.append(f"Pattern {idx}: Invalid confidence {conf} (must be 0.0-1.0)")

        # Validate direction
        if 'direction' in pred:
            if pred['direction'] not in ['Up', 'Down', 'Hold']:
                errors.append(f"Pattern {idx}: Invalid direction '{pred['direction']}'")

    # Validate sample size
    if 'sample_size' in pattern:
        size = pattern['sample_size']
        if not isinstance(size, int) or size < 10:
            errors.append(f"Pattern {idx}: Insufficient sample_size {size} (need >=10)")

    # Validate conditions (should be list)
    if 'conditions' in pattern:
        if not isinstance(pattern['conditions'], list):
            errors.append(f"Pattern {idx}: 'conditions' must be a list")

    return errors


def validate_patterns_file(file_path: Path) -> bool:
    """
    Validate patterns_v1.json file

    Returns:
        True if valid, False otherwise
    """

    print("=== Validating Patterns ===\n")
    print(f"File: {file_path}\n")

    # Check file exists
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        return False

    # Load JSON
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}")
        return False

    # Check top-level structure
    if 'patterns' not in data:
        print("ERROR: Missing top-level 'patterns' key")
        return False

    patterns = data['patterns']

    if not isinstance(patterns, list):
        print("ERROR: 'patterns' must be a list")
        return False

    if len(patterns) == 0:
        print("WARNING: No patterns found")
        return False

    print(f"Found {len(patterns)} patterns\n")

    # Validate each pattern
    all_errors = []

    for idx, pattern in enumerate(patterns, 1):
        errors = validate_pattern_structure(pattern, idx)
        all_errors.extend(errors)

        if errors:
            print(f"❌ Pattern {idx} ({pattern.get('pattern_id', 'unknown')}): {len(errors)} errors")
            for error in errors:
                print(f"     - {error}")
        else:
            print(f"✓ Pattern {idx} ({pattern.get('pattern_id', 'unknown')}): Valid")
            print(f"    Name: {pattern.get('name', 'N/A')}")
            print(f"    Sample size: {pattern.get('sample_size', 'N/A')}")
            print(f"    Confidence: {pattern.get('prediction', {}).get('confidence', 'N/A')}")

    print("\n=== Validation Summary ===")

    if all_errors:
        print(f"❌ Validation FAILED with {len(all_errors)} errors\n")
        return False
    else:
        print(f"✓ All {len(patterns)} patterns are valid!\n")

        # Summary statistics
        total_samples = sum(p.get('sample_size', 0) for p in patterns)
        avg_confidence = sum(p.get('prediction', {}).get('confidence', 0) for p in patterns) / len(patterns)

        print("Statistics:")
        print(f"  Total patterns: {len(patterns)}")
        print(f"  Total samples: {total_samples}")
        print(f"  Average confidence: {avg_confidence:.2f}")
        print(f"  Min sample size: {min(p.get('sample_size', 0) for p in patterns)}")
        print(f"  Max sample size: {max(p.get('sample_size', 0) for p in patterns)}")

        return True


def main():
    """Main execution"""

    patterns_file = Path(__file__).parent.parent / "outputs" / "patterns_v1.json"

    is_valid = validate_patterns_file(patterns_file)

    if is_valid:
        print("\n✓ Phase 0 validation complete!")
        print("You can proceed to Phase 1")
        sys.exit(0)
    else:
        print("\n❌ Validation failed!")
        print("Please fix the errors and run again")
        sys.exit(1)


if __name__ == "__main__":
    main()
