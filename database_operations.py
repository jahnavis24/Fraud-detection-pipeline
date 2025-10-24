from decimal import Decimal
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class AnomalyTransactions:
    """Encapsulates DynamoDB operations for anomaly detection on transactions.
    
    This class manages two DynamoDB tables:
    - transactions: Contains transaction data for analysis
    - results: Stores prediction results and associated metadata
    """
    
    def __init__(self, region_name='ap-southeast-2', aws_access_key_id=None, aws_secret_access_key=None):
        """
        Initialize the AnomalyTransactions class with DynamoDB client and tables.
        
        :param region_name: AWS region name
        :param aws_access_key_id: AWS access key ID
        :param aws_secret_access_key: AWS secret access key
        """
        self.region_name = region_name
        
        # Initialize DynamoDB client
        self.dynamodb = boto3.client(
            'dynamodb',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        
        # Initialize DynamoDB resource for table operations
        self.dyn_resource = boto3.resource(
            'dynamodb',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        
        # Initialize table references
        self.transactions_table = None
        self.results_table = None
    
    def list_tables(self, limit=10):
        """
        List all DynamoDB tables in the current AWS account.
        
        :param limit: Maximum number of tables to return per page
        :return: List of table names
        """
        try:
            paginator = self.dynamodb.get_paginator("list_tables")
            page_iterator = paginator.paginate(Limit=limit)
            
            table_names = []
            print("Here are the DynamoDB tables in your account:")
            
            for page in page_iterator:
                for table_name in page.get("TableNames", []):
                    print(f"- {table_name}")
                    table_names.append(table_name)
            
            if not table_names:
                print("You don't have any DynamoDB tables in your account.")
            else:
                print(f"\nFound {len(table_names)} tables.")
            
            return table_names
            
        except ClientError as err:
            logger.error(
                "Couldn't list tables. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
    
    def initialize_tables(self, transactions_table_name='transactions', results_table_name='detections', alerts_table_name='alerts'):
        """
        Initialize table references for transactions, results, and alerts.

        :param transactions_table_name: Name of the transactions table
        :param results_table_name: Name of the results table
        """
        try:
            self.transactions_table = self.dyn_resource.Table(transactions_table_name)
            self.results_table = self.dyn_resource.Table(results_table_name)
            self.alerts_table = self.dyn_resource.Table(alerts_table_name)

            # Verify tables exist by loading their metadata
            self.transactions_table.load()
            self.results_table.load()
            self.alerts_table.load()

        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                logger.error(
                    "One or both tables don't exist. Please create them first."
                )
            else:
                logger.error(
                    "Couldn't initialize tables. Here's why: %s: %s",
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
            raise
    
    def convert_floats(self, obj):
        """
        Recursively convert float values to Decimal for DynamoDB compatibility.
        
        :param obj: Object to convert (can be dict, list, or primitive)
        :return: Object with floats converted to Decimal
        """
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {k: self.convert_floats(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_floats(i) for i in obj]
        return obj
    
    def store_transaction(self, transaction_data):
        """
        Store a transaction in the transactions table.
        
        :param transaction_data: Dictionary containing transaction details
        """
        if not self.transactions_table:
            raise ValueError("Transactions table not initialized. Call initialize_tables() first.")
        
        try:
            # Convert all float values to Decimal for DynamoDB
            transaction_data = self.convert_floats(transaction_data)
            
            # Store the item in DynamoDB
            self.transactions_table.put_item(
                Item=transaction_data
            )
            
            logger.info(f"Stored transaction {transaction_data['transactionID']} successfully!")
            
        except ClientError as err:
            logger.error(
                "Couldn't store transaction. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
    
    def store_result(self, prediction_response, transaction_id, csv_row):
        """
        Store prediction results in the results table.
        
        :param prediction_response: The ML model prediction response
        :param transaction_id: Unique identifier for the transaction
        :param csv_row: Original CSV data row for the transaction
        """
        if not self.results_table:
            raise ValueError("Results table not initialized. Call initialize_tables() first.")
        
        try:
            # Convert all float values to Decimal for DynamoDB
            prediction_response = self.convert_floats(prediction_response)
            transaction_id = self.convert_floats(transaction_id)
            csv_row = self.convert_floats(csv_row)
            
            # Store the item in DynamoDB
            self.results_table.put_item(
                Item={
                    'transactionID': transaction_id,  # Primary key
                    'prediction': prediction_response,
                    'csv_data': csv_row
                }
            )
            
            logger.info(f"Stored prediction for transaction {transaction_id} successfully!")
            
        except ClientError as err:
            logger.error(
                "Couldn't store prediction result. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
    
    def list_transactions(self, limit=10):
        """
        List all transactions in the transactions table.
        
        :param limit: Maximum number of transactions to return per page
        :return: List of transaction items
        """
        if not self.transactions_table:
            raise ValueError("Transactions table not initialized. Call initialize_tables() first.")
        
        try:
            paginator = self.transactions_table.scan(
                Limit=limit
            )
            transactions = []
            
            for page in paginator['Items']:
                transactions.append(page)
            
            return transactions
            
        except ClientError as err:
            logger.error(
                "Couldn't list transactions. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
    
    def list_results(self, limit=10):
        """
        List all results in the results table.
        
        :param limit: Maximum number of results to return per page
        :return: List of result items
        """
        if not self.results_table:
            raise ValueError("Results table not initialized. Call initialize_tables() first.")
        
        try:
            paginator = self.results_table.scan(
                Limit=limit
            )
            results = []
            
            for page in paginator['Items']:
                results.append(page)
            
            return results
            
        except ClientError as err:
            logger.error(
                "Couldn't list results. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
    
    def list_alerts(self, limit=10):
        """
        List all alerts in the alerts table.
        
        :param limit: Maximum number of alerts to return per page
        :return: List of alert items
        """
        if not self.alerts_table:
            raise ValueError("Alerts table not initialized. Call initialize_tables() first.")
        
        try:
            paginator = self.alerts_table.scan(
                Limit=limit
            )
            alerts = []
            
            for page in paginator['Items']:
                alerts.append(page)
            
            return alerts
            
        except ClientError as err:
            logger.error(
                "Couldn't list alerts. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
    
    def get_transaction(self, transaction_id):
        """
        Retrieve a specific transaction from the transactions table.
        
        :param transaction_id: The ID of the transaction to retrieve
        :return: Transaction data
        """
        if not self.transactions_table:
            raise ValueError("Transactions table not initialized. Call initialize_tables() first.")
        
        try:
            response = self.transactions_table.get_item(
                Key={'transactionID': transaction_id}
            )
            return response.get('Item')
            
        except ClientError as err:
            logger.error(
                "Couldn't get transaction %s. Here's why: %s: %s",
                transaction_id,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
    
    def get_result(self, transaction_id: int):
        """
        Retrieve prediction results for a specific transaction.
        
        :param transaction_id: The ID of the transaction
        :return: Prediction results data
        """
        if not self.results_table:
            raise ValueError("Results table not initialized. Call initialize_tables() first.")
        
        try:
            response = self.results_table.get_item(
                Key={'transactionID': transaction_id}
            )
            return response.get('Item')
            
        except ClientError as err:
            logger.error(
                "Couldn't get result for transaction %s. Here's why: %s: %s",
                transaction_id,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
    
    def batch_store_results(self, results_data):
        """
        Store multiple prediction results in batch for better performance.
        
        :param results_data: List of dictionaries containing prediction data
                           Each dict should have: prediction_response, transaction_id, csv_row
        """
        if not self.results_table:
            raise ValueError("Results table not initialized. Call initialize_tables() first.")
        
        try:
            with self.results_table.batch_writer() as batch:
                for result in results_data:
                    # Convert floats to Decimal
                    prediction_response = self.convert_floats(result['prediction_response'])
                    transaction_id = self.convert_floats(result['transaction_id'])
                    csv_row = self.convert_floats(result['csv_row'])
                    
                    batch.put_item(
                        Item={
                            'transactionID': transaction_id,
                            'prediction': prediction_response,
                            'csv_data': csv_row
                        }
                    )
            
            logger.info(f"Batch stored {len(results_data)} prediction results successfully!")
            
        except ClientError as err:
            logger.error(
                "Couldn't batch store results. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    def batch_get_transactions(self, transaction_ids):
        """
        Retrieve multiple transactions in batch.
        
        :param transaction_ids: List of transaction IDs to retrieve
        :return: List of transaction items
        """
        if not self.transactions_table:
            raise ValueError("Transactions table not initialized. Call initialize_tables() first.")
        
        try:
            keys = [{'transactionID': tid} for tid in transaction_ids]
            response = self.transactions_table.batch_get_item(
                RequestItems={
                    self.transactions_table.name: {
                        'Keys': keys
                    }
                }
            )
            return response.get('Responses', {}).get(self.transactions_table.name, [])
            
        except ClientError as err:
            logger.error(
                "Couldn't batch get transactions. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
    
    def batch_store_transactions(self, transactions_data):
        """
        Store multiple transactions in batch for better performance.
        
        :param transactions_data: List of dictionaries containing transaction data
        """
        if not self.transactions_table:
            raise ValueError("Transactions table not initialized. Call initialize_tables() first.")
        
        try:
            with self.transactions_table.batch_writer() as batch:
                for transaction in transactions_data:
                    # Convert floats to Decimal
                    transaction = self.convert_floats(transaction)
                    
                    batch.put_item(
                        Item=transaction
                    )
            
            logger.info(f"Batch stored {len(transactions_data)} transactions successfully!")
            
        except ClientError as err:
            logger.error(
                "Couldn't batch store transactions. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise