"""
Lambda Utilities: AWS Clients

Centralized AWS service clients
"""

import boto3
import os
from typing import Optional


class AWSClients:
    """Singleton AWS clients"""

    _dynamodb = None
    _s3 = None
    _bedrock = None
    _sns = None
    _ssm = None
    _events = None

    @classmethod
    def get_dynamodb(cls):
        """Get DynamoDB client"""
        if cls._dynamodb is None:
            cls._dynamodb = boto3.resource('dynamodb')
        return cls._dynamodb

    @classmethod
    def get_s3(cls):
        """Get S3 client"""
        if cls._s3 is None:
            cls._s3 = boto3.client('s3')
        return cls._s3

    @classmethod
    def get_bedrock(cls):
        """Get Bedrock Runtime client"""
        if cls._bedrock is None:
            cls._bedrock = boto3.client('bedrock-runtime')
        return cls._bedrock

    @classmethod
    def get_sns(cls):
        """Get SNS client"""
        if cls._sns is None:
            cls._sns = boto3.client('sns')
        return cls._sns

    @classmethod
    def get_ssm(cls):
        """Get SSM client"""
        if cls._ssm is None:
            cls._ssm = boto3.client('ssm')
        return cls._ssm

    @classmethod
    def get_eventbridge(cls):
        """Get EventBridge client"""
        if cls._events is None:
            cls._events = boto3.client('events')
        return cls._events


def get_table(table_name: str):
    """Get DynamoDB table"""
    dynamodb = AWSClients.get_dynamodb()
    return dynamodb.Table(table_name)


def get_ssm_parameter(param_name: str) -> Optional[str]:
    """Get SSM parameter value"""
    try:
        ssm = AWSClients.get_ssm()
        response = ssm.get_parameter(Name=param_name, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        print(f"Error getting SSM parameter {param_name}: {e}")
        return None


def put_eventbridge_event(source: str, detail_type: str, detail: dict):
    """Put custom event to EventBridge"""
    try:
        events = AWSClients.get_eventbridge()
        response = events.put_events(
            Entries=[
                {
                    'Source': source,
                    'DetailType': detail_type,
                    'Detail': str(detail)
                }
            ]
        )
        return response
    except Exception as e:
        print(f"Error putting EventBridge event: {e}")
        return None
