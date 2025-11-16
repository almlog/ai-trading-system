"""
Lambda Utilities: Circuit Breaker

Prevents excessive trading and enforces risk limits
Based on DESIGN_DOC_FINAL.md Section 4.3
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from lambda.utils.constants import CIRCUIT_BREAKER_RULES, DYNAMODB_TABLES
from lambda.utils.aws_clients import get_table


class CircuitBreaker:
    """Circuit breaker for risk management"""

    def __init__(self):
        self.rules = CIRCUIT_BREAKER_RULES
        self.trigger_table = get_table(DYNAMODB_TABLES['trigger_history'])
        self.positions_table = get_table(DYNAMODB_TABLES['positions'])

    def check(self, trigger_type: str) -> Dict[str, any]:
        """
        Check if system should proceed

        Args:
            trigger_type: Type of trigger (news/volatility/calendar)

        Returns:
            {
                "allowed": bool,
                "reason": str (if not allowed)
            }
        """

        # Check 1: Triggers per hour limit
        hourly_check = self._check_hourly_triggers()
        if not hourly_check['allowed']:
            return hourly_check

        # Check 2: Positions per day limit
        daily_trades_check = self._check_daily_trades()
        if not daily_trades_check['allowed']:
            return daily_trades_check

        # Check 3: Daily loss limit
        daily_loss_check = self._check_daily_loss()
        if not daily_loss_check['allowed']:
            return daily_loss_check

        # Check 4: Total loss limit
        total_loss_check = self._check_total_loss()
        if not total_loss_check['allowed']:
            return total_loss_check

        # Check 5: Minimum interval
        interval_check = self._check_minimum_interval()
        if not interval_check['allowed']:
            return interval_check

        return {"allowed": True, "reason": "All checks passed"}

    def _check_hourly_triggers(self) -> Dict[str, any]:
        """Check if hourly trigger limit exceeded"""
        try:
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            timestamp_str = one_hour_ago.isoformat()

            response = self.trigger_table.query(
                IndexName='TimestampIndex',  # Assumes GSI exists
                KeyConditionExpression='timestamp > :hour_ago',
                ExpressionAttributeValues={':hour_ago': timestamp_str}
            )

            count = len(response.get('Items', []))

            if count >= self.rules['max_triggers_per_hour']:
                return {
                    "allowed": False,
                    "reason": f"Hourly trigger limit reached ({count}/{self.rules['max_triggers_per_hour']})"
                }

            return {"allowed": True}

        except Exception as e:
            print(f"Error checking hourly triggers: {e}")
            return {"allowed": True}  # Fail open for now

    def _check_daily_trades(self) -> Dict[str, any]:
        """Check if daily trade limit exceeded"""
        try:
            today = datetime.utcnow().date().isoformat()

            response = self.positions_table.query(
                IndexName='DateIndex',  # Assumes GSI exists
                KeyConditionExpression='trade_date = :today',
                ExpressionAttributeValues={':today': today}
            )

            count = len(response.get('Items', []))

            if count >= self.rules['max_positions_per_day']:
                return {
                    "allowed": False,
                    "reason": f"Daily trade limit reached ({count}/{self.rules['max_positions_per_day']})"
                }

            return {"allowed": True}

        except Exception as e:
            print(f"Error checking daily trades: {e}")
            return {"allowed": True}

    def _check_daily_loss(self) -> Dict[str, any]:
        """Check if daily loss limit exceeded"""
        try:
            today = datetime.utcnow().date().isoformat()

            response = self.positions_table.query(
                IndexName='DateIndex',
                KeyConditionExpression='trade_date = :today',
                ExpressionAttributeValues={':today': today}
            )

            total_pnl = sum(item.get('pnl', 0) for item in response.get('Items', []))

            if total_pnl <= -self.rules['daily_loss_limit_usd']:
                return {
                    "allowed": False,
                    "reason": f"Daily loss limit reached (${total_pnl:.2f})"
                }

            return {"allowed": True}

        except Exception as e:
            print(f"Error checking daily loss: {e}")
            return {"allowed": True}

    def _check_total_loss(self) -> Dict[str, any]:
        """Check if total project loss limit exceeded"""
        try:
            response = self.positions_table.scan()

            total_pnl = sum(item.get('pnl', 0) for item in response.get('Items', []))

            if total_pnl <= -self.rules['total_loss_limit_usd']:
                return {
                    "allowed": False,
                    "reason": f"CRITICAL: Total loss limit reached (${total_pnl:.2f}). System stopped."
                }

            return {"allowed": True}

        except Exception as e:
            print(f"Error checking total loss: {e}")
            return {"allowed": True}

    def _check_minimum_interval(self) -> Dict[str, any]:
        """Check minimum interval between triggers"""
        try:
            response = self.trigger_table.scan(Limit=1)
            items = response.get('Items', [])

            if not items:
                return {"allowed": True}

            last_trigger = items[0]
            last_timestamp = datetime.fromisoformat(last_trigger['timestamp'])
            elapsed = (datetime.utcnow() - last_timestamp).total_seconds()

            if elapsed < self.rules['min_interval_seconds']:
                return {
                    "allowed": False,
                    "reason": f"Minimum interval not met ({elapsed:.0f}s < {self.rules['min_interval_seconds']}s)"
                }

            return {"allowed": True}

        except Exception as e:
            print(f"Error checking minimum interval: {e}")
            return {"allowed": True}

    def log_trigger(self, trigger_type: str, details: dict):
        """Log trigger event to DynamoDB"""
        try:
            item = {
                'trigger_id': f"{trigger_type}_{datetime.utcnow().isoformat()}",
                'timestamp': datetime.utcnow().isoformat(),
                'trigger_type': trigger_type,
                'details': details
            }

            self.trigger_table.put_item(Item=item)

        except Exception as e:
            print(f"Error logging trigger: {e}")
