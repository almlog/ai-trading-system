#!/usr/bin/env python3
"""
Phase 3: Daily Performance Evaluator

Evaluates daily trading performance and logs metrics.
Based on DESIGN_DOC_FINAL.md Section 5.15
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import boto3
from decimal import Decimal

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class PerformanceEvaluator:
    """Daily performance evaluation"""

    def __init__(self, environment: str = "dev"):
        self.environment = environment
        self.dynamodb = boto3.resource('dynamodb')
        self.s3 = boto3.client('s3')

        # Table names
        self.positions_table_name = f"ai-trading-positions-{environment}"
        self.positions_table = self.dynamodb.Table(self.positions_table_name)

        # S3 bucket for performance logs
        self.bucket_name = f"ai-trading-pattern-library-{environment}"

    def evaluate_daily_performance(self, date: str = None) -> Dict[str, Any]:
        """
        Evaluate performance for a specific date

        Args:
            date: Date in YYYY-MM-DD format (defaults to yesterday)

        Returns:
            Performance metrics dictionary
        """

        if date is None:
            date = (datetime.utcnow() - timedelta(days=1)).date().isoformat()

        print(f"Evaluating performance for {date}...")

        # Query positions for the date
        try:
            response = self.positions_table.query(
                IndexName='DateIndex',
                KeyConditionExpression='trade_date = :date',
                ExpressionAttributeValues={':date': date}
            )

            trades = response.get('Items', [])

        except Exception as e:
            print(f"Error querying positions: {e}")
            return {}

        if not trades:
            print(f"No trades found for {date}")
            return {
                'date': date,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_pnl': 0.0,
                'accuracy': 0.0
            }

        # Calculate metrics
        results = {
            'date': date,
            'total_trades': len(trades),
            'winning_trades': 0,
            'losing_trades': 0,
            'neutral_trades': 0,
            'total_pnl': 0.0,
            'max_win': 0.0,
            'max_loss': 0.0,
            'avg_pnl': 0.0,
            'accuracy': 0.0,
            'trades_by_symbol': {},
            'trades_by_pattern': {}
        }

        for trade in trades:
            pnl = float(trade.get('pnl', 0))

            results['total_pnl'] += pnl

            if pnl > 0:
                results['winning_trades'] += 1
                results['max_win'] = max(results['max_win'], pnl)
            elif pnl < 0:
                results['losing_trades'] += 1
                results['max_loss'] = min(results['max_loss'], pnl)
            else:
                results['neutral_trades'] += 1

            # By symbol
            symbol = trade.get('symbol', 'UNKNOWN')
            if symbol not in results['trades_by_symbol']:
                results['trades_by_symbol'][symbol] = {'count': 0, 'pnl': 0.0}
            results['trades_by_symbol'][symbol]['count'] += 1
            results['trades_by_symbol'][symbol]['pnl'] += pnl

            # By pattern
            pattern_id = trade.get('matched_pattern_id', 'UNKNOWN')
            if pattern_id not in results['trades_by_pattern']:
                results['trades_by_pattern'][pattern_id] = {'count': 0, 'pnl': 0.0}
            results['trades_by_pattern'][pattern_id]['count'] += 1
            results['trades_by_pattern'][pattern_id]['pnl'] += pnl

        # Calculate accuracy
        if results['total_trades'] > 0:
            results['accuracy'] = results['winning_trades'] / results['total_trades']
            results['avg_pnl'] = results['total_pnl'] / results['total_trades']

        print(f"✓ Evaluation complete: {results['total_trades']} trades, ${results['total_pnl']:.2f} P&L")

        return results

    def save_to_s3(self, results: Dict):
        """Save performance results to S3"""

        try:
            date = results['date']
            key = f"performance_logs/{date}.json"

            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(results, indent=2, default=str),
                ContentType='application/json'
            )

            print(f"✓ Saved to S3: s3://{self.bucket_name}/{key}")

        except Exception as e:
            print(f"Error saving to S3: {e}")

    def append_to_csv(self, results: Dict):
        """Append results to local CSV (for Phase 3 final report)"""

        try:
            output_dir = project_root / "claudedocs"
            output_dir.mkdir(exist_ok=True)

            csv_file = output_dir / "performance_log.csv"

            # Create header if file doesn't exist
            if not csv_file.exists():
                with open(csv_file, 'w') as f:
                    f.write("date,total_trades,winning_trades,losing_trades,total_pnl,accuracy,avg_pnl,max_win,max_loss\n")

            # Append data
            with open(csv_file, 'a') as f:
                f.write(
                    f"{results['date']},"
                    f"{results['total_trades']},"
                    f"{results['winning_trades']},"
                    f"{results['losing_trades']},"
                    f"{results['total_pnl']:.2f},"
                    f"{results['accuracy']:.2%},"
                    f"{results['avg_pnl']:.2f},"
                    f"{results['max_win']:.2f},"
                    f"{results['max_loss']:.2f}\n"
                )

            print(f"✓ Appended to CSV: {csv_file}")

        except Exception as e:
            print(f"Error appending to CSV: {e}")


def lambda_handler(event, context):
    """
    AWS Lambda handler (for automated daily evaluation)

    Triggered by: EventBridge schedule (daily at 23:59 UTC)
    """

    environment = os.environ.get('ENVIRONMENT', 'dev')

    evaluator = PerformanceEvaluator(environment)

    # Evaluate yesterday's performance
    results = evaluator.evaluate_daily_performance()

    if results:
        # Save to S3
        evaluator.save_to_s3(results)

        # Send notification if significant loss
        if results['total_pnl'] < -10:
            # TODO: Send SNS notification
            print(f"⚠️ WARNING: Daily loss ${results['total_pnl']:.2f}")

    return {
        'statusCode': 200,
        'body': json.dumps(results, default=str)
    }


def main():
    """CLI execution"""

    print("=== Daily Performance Evaluator ===\n")

    environment = os.environ.get('ENVIRONMENT', 'dev')
    evaluator = PerformanceEvaluator(environment)

    # Evaluate yesterday
    results = evaluator.evaluate_daily_performance()

    if results:
        # Save
        evaluator.save_to_s3(results)
        evaluator.append_to_csv(results)

        # Display summary
        print("\n" + "="*50)
        print(f"Date: {results['date']}")
        print(f"Total trades: {results['total_trades']}")
        print(f"Winning: {results['winning_trades']} | Losing: {results['losing_trades']}")
        print(f"Accuracy: {results['accuracy']:.2%}")
        print(f"Total P&L: ${results['total_pnl']:.2f}")
        print(f"Average P&L: ${results['avg_pnl']:.2f}")
        print(f"Max win: ${results['max_win']:.2f}")
        print(f"Max loss: ${results['max_loss']:.2f}")
        print("="*50)


if __name__ == "__main__":
    main()
