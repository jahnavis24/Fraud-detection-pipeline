# Lambda Functions

## Kinesis Lambda (Fraud Detection ETL Pipeline)

### Structure
```
kinesis_lambda_sagemaker_flow/
├── lambda_handler.py      # Main lambda handler
├── config.py              # Configuration settings
├── fraud_detector.py      # Main fraud detection processor
├── business_rules.py      # Business rules engine
├── sagemaker_client.py    # SageMaker inference client
├── data_processor.py      # DynamoDB operations
├── alert_manager.py       # SQS alert management
└── requirements.txt       # Dependencies
```

### Components

1. **main.py**: Entry point for the Lambda function
2. **fraud_detector.py**: Main orchestrator that coordinates the fraud detection pipeline
3. **business_rules.py**: Implements business logic rules for quick fraud detection
4. **sagemaker_client.py**: Handles SageMaker endpoint communication and data preprocessing
5. **data_processor.py**: Manages all DynamoDB read/write operations
6. **alert_manager.py**: Sends fraud alerts to SQS queue
7. **config.py**: Centralized configuration management

### Usage
The main handler is in `lambda_handler.py`. It creates a `FraudDetectionProcessor` instance and processes Kinesis records.

## SQS Lambda (Alert Processing)

### Structure
```
sqs_lambda_alerting/
├── lambda_handler.py     # Main lambda handler
├── config.py             # Configuration settings
├── alert_processor.py    # Main alert processor
├── data_handler.py       # DynamoDB alert storage
├── email_service.py      # Email notification service
└── requirements.txt      # Dependencies
```

### Components

1. **main.py**: Entry point for the Lambda function
2. **alert_processor.py**: Main orchestrator for processing SQS messages
3. **data_handler.py**: Handles alert storage in DynamoDB
4. **email_service.py**: Manages email notifications
5. **config.py**: Centralized configuration management

### Usage
The main handler is in `lambda_handler.py`. It creates an `AlertProcessor` instance and processes SQS messages.
