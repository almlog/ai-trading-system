"""
Lambda Utilities: Constants

System-wide constants and configuration values
"""

# Stock symbols (テック大手5社)
SYMBOLS = [
    "AAPL",  # Apple
    "MSFT",  # Microsoft
    "GOOGL", # Alphabet/Google
    "AMZN",  # Amazon
    "NVDA"   # NVIDIA
]

# Circuit breaker rules (DESIGN_DOC_FINAL.md Section 4.3)
CIRCUIT_BREAKER_RULES = {
    "max_triggers_per_hour": 10,
    "max_positions_per_day": 5,
    "min_interval_seconds": 300,  # 5 minutes
    "daily_loss_limit_usd": 20,
    "total_loss_limit_usd": 100,
}

# Volatility thresholds (DESIGN_DOC_FINAL.md Section 4.2)
VOLATILITY_THRESHOLDS = {
    "AAPL": 2.0,   # ±2%
    "MSFT": 2.0,   # ±2%
    "GOOGL": 2.0,  # ±2%
    "AMZN": 2.5,   # ±2.5%
    "NVDA": 2.5,   # ±2.5%
}

# Trading parameters (DESIGN_DOC_FINAL.md Section 5.7-5.8)
TRADING_PARAMS = {
    "stop_loss_pct": -1.0,           # -1% automatic stop loss
    "take_profit_trigger_pct": 1.0,  # +1% triggers AI evaluation
    "max_holding_time_sec": 1800,    # 30 minutes
    "max_position_size": 1,          # 1 share per position
}

# DynamoDB table names
DYNAMODB_TABLES = {
    "trigger_history": "ai-trading-trigger-history",
    "positions": "ai-trading-positions",
    "economic_calendar": "ai-trading-economic-calendar",
}

# S3 bucket names
S3_BUCKETS = {
    "news_archive": "ai-trading-news-archive",
    "pattern_library": "ai-trading-pattern-library",
}

# SSM parameter paths
SSM_PARAMS = {
    "patterns": "/ai-trading/patterns",
    "prompt_realtime_analysis": "/ai-trading/prompts/realtime-analysis",
    "prompt_exit_evaluation": "/ai-trading/prompts/exit-evaluation",
}

# API endpoints
API_ENDPOINTS = {
    "finnhub_news": "https://finnhub.io/api/v1/company-news",
    "alpha_vantage_quote": "https://www.alphavantage.co/query",
}
