# AI News Analysis & Automated Trading System
# Makefile

.PHONY: help setup clean

# Default target
.DEFAULT_GOAL := help

# ============================================
# General Commands
# ============================================

help: ## Show this help message
	@echo "AI News Analysis & Automated Trading System - Available Commands"
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""

setup: ## Initial setup - create venv and install dependencies
	python -m venv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  Windows: venv\\Scripts\\activate"
	@echo "  Unix:    source venv/bin/activate"
	@echo "Then run: make install-deps"

install-deps: ## Install all Python dependencies
	pip install --upgrade pip
	pip install -r requirements.txt

clean: ## Clean up temporary files and caches
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete

# ============================================
# Phase 0: Data Analysis
# ============================================

phase0-setup: ## Setup Phase 0 environment
	pip install -r requirements.txt
	python -m nltk.downloader vader_lexicon
	python -m nltk.downloader punkt
	@echo "Phase 0 setup complete!"

phase0-download-data: ## Download Kaggle datasets for Phase 0
	@echo "Downloading datasets from Kaggle..."
	@if [ ! -f ~/.kaggle/kaggle.json ]; then \
		echo "ERROR: Kaggle API credentials not found!"; \
		echo "Please place kaggle.json in ~/.kaggle/"; \
		exit 1; \
	fi
	python phase0_data_analysis/scripts/download_kaggle_data.py

phase0-notebook: ## Launch Jupyter Notebook for Phase 0
	jupyter notebook phase0_data_analysis/notebooks/

phase0-analyze: ## Run Phase 0 pattern discovery analysis
	python phase0_data_analysis/scripts/pattern_discovery.py

phase0-validate: ## Validate Phase 0 output (patterns_v1.json)
	python phase0_data_analysis/scripts/validate_patterns.py

# ============================================
# Phase 1: Lambda & AWS Deployment
# ============================================

phase1-test-local: ## Run local tests for Lambda functions
	pytest lambda/tests/ -v

phase1-package: ## Package Lambda functions for deployment
	python scripts/package_lambda.py

phase1-deploy-dev: ## Deploy to AWS Dev environment
	cd infrastructure/terraform/environments/dev && \
	terraform init && \
	terraform plan && \
	terraform apply

phase1-deploy-prod: ## Deploy to AWS Prod environment (WARNING: Production!)
	@echo "WARNING: You are deploying to PRODUCTION!"
	@read -p "Are you sure? [y/N]: " confirm && [ "$$confirm" = "y" ]
	cd infrastructure/terraform/environments/prod && \
	terraform init && \
	terraform plan && \
	terraform apply

phase1-destroy-dev: ## Destroy AWS Dev environment
	cd infrastructure/terraform/environments/dev && terraform destroy

# ============================================
# Phase 2-3: Evaluation & Analysis
# ============================================

phase2-analyze-raw: ## Run Phase 2 raw data analysis
	python phase0_data_analysis/scripts/pattern_discovery_raw.py

phase2-compare: ## Compare Phase 0 (A) vs Phase 2 (B) patterns
	python scripts/compare_patterns.py

phase3-evaluate-daily: ## Run daily performance evaluation
	python scripts/daily_performance_evaluator.py

phase3-generate-report: ## Generate final research report
	python scripts/generate_final_report.py

# ============================================
# AWS Utilities
# ============================================

aws-costs: ## Check AWS costs for current month
	aws ce get-cost-and-usage \
		--time-period Start=$$(date -d "1 day ago" +%Y-%m-01),End=$$(date +%Y-%m-%d) \
		--granularity MONTHLY \
		--metrics UnblendedCost \
		--query 'ResultsByTime[0].Total.UnblendedCost.Amount' \
		--output text | \
		awk '{printf "Current month AWS costs: $%.2f\n", $$1}'

lambda-logs: ## View Lambda function logs (specify FUNCTION=name)
	@if [ -z "$(FUNCTION)" ]; then \
		echo "ERROR: Please specify FUNCTION=<lambda_name>"; \
		echo "Example: make lambda-logs FUNCTION=news_fetch_lambda"; \
		exit 1; \
	fi
	aws logs tail /aws/lambda/$(FUNCTION) --follow

dynamodb-scan: ## Scan DynamoDB table (specify TABLE=name)
	@if [ -z "$(TABLE)" ]; then \
		echo "ERROR: Please specify TABLE=<table_name>"; \
		echo "Example: make dynamodb-scan TABLE=trigger_history"; \
		exit 1; \
	fi
	aws dynamodb scan --table-name $(TABLE) --output json

# ============================================
# Development & Testing
# ============================================

test: ## Run all tests
	pytest tests/ -v

lint: ## Run code linting
	flake8 lambda/ phase0_data_analysis/ scripts/
	black --check lambda/ phase0_data_analysis/ scripts/

format: ## Format code with black
	black lambda/ phase0_data_analysis/ scripts/

# ============================================
# Git Workflow
# ============================================

git-status: ## Show git status and current branch
	@git branch --show-current
	@git status

git-feature: ## Create new feature branch (specify NAME=feature-name)
	@if [ -z "$(NAME)" ]; then \
		echo "ERROR: Please specify NAME=<feature-name>"; \
		echo "Example: make git-feature NAME=phase1-triggers"; \
		exit 1; \
	fi
	git checkout -b feature/$(NAME)

# ============================================
# Documentation
# ============================================

docs: ## Open project documentation
	@echo "Opening documentation..."
	@if command -v xdg-open > /dev/null; then \
		xdg-open docs/DESIGN_DOC_FINAL.md; \
	elif command -v open > /dev/null; then \
		open docs/DESIGN_DOC_FINAL.md; \
	else \
		echo "Please open docs/DESIGN_DOC_FINAL.md manually"; \
	fi
