import boto3
import json
import csv
import time
from dotenv import load_dotenv
import os

load_dotenv()

def read_fraud_transactions_csv(file_path):
    """
    Read fraud transactions from CSV file and convert to the required JSON format
    """
    transactions = []
    
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Convert CSV row to the required JSON format
            record = {
                "transactionID": int(row['transactionID']),
                "trans_date_trans_time": row['trans_date_trans_time'],
                "cc_num": str(int(float(row['cc_num']))),  # Convert scientific notation to string
                "merchant": row['merchant'],
                "category": row['category'],
                "amt": float(row['amt']),
                "first": row['first'],
                "last": row['last'],
                "gender": row['gender'],
                "street": row['street'],
                "city": row['city'],
                "state": row['state'],
                "zip": int(row['zip']),
                "lat": float(row['lat']),
                "long": float(row['long']),
                "city_pop": int(row['city_pop']),
                "job": row['job'],
                "dob": row['dob'],
                "trans_num": row['trans_num'],
                "unix_time": int(row['unix_time']),
                "merch_lat": float(row['merch_lat']),
                "merch_long": float(row['merch_long']),
                "is_fraud": row['is_fraud']
            }
            transactions.append(record)
    
    return transactions

def send_to_kinesis(kinesis_client, record, stream_name):
    """
    Send a single record to Kinesis stream
    """
    try:
        response = kinesis_client.put_record(
            StreamName=stream_name,
            Data=json.dumps(record),
            PartitionKey=str(record['transactionID'])
        )
        return response
    except Exception as e:
        print(f"Error sending record {record['transactionID']}: {str(e)}")
        return None

def test_fraud_transactions_flow():
    """
    Main test flow to read CSV and send to Kinesis
    """
    # Initialize Kinesis client
    kinesis = boto3.client(
        'kinesis',
        region_name='ap-southeast-2',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    # Path to the fraud transactions CSV
    csv_file_path = r'c:\Users\ADMIN\Desktop\AWS_architecture\src\dataset\fraud_transactions_10.csv'
    stream_name = 'anomaly-transaction-ingesting-stream'
    
    print("Reading fraud transactions from CSV...")
    transactions = read_fraud_transactions_csv(csv_file_path)
    print(f"Found {len(transactions)} transactions")
    
    # Send each transaction to Kinesis
    successful_sends = 0
    failed_sends = 0
    
    for i, transaction in enumerate(transactions):
        print(f"Sending transaction {i+1}/{len(transactions)} - ID: {transaction['transactionID']}")
        
        response = send_to_kinesis(kinesis, transaction, stream_name)
        
        if response:
            print(f"✓ Successfully sent transaction {transaction['transactionID']}")
            print(f"  Shard ID: {response['ShardId']}")
            print(f"  Sequence Number: {response['SequenceNumber']}")
            successful_sends += 1
        else:
            print(f"✗ Failed to send transaction {transaction['transactionID']}")
            failed_sends += 1
        
        # Add small delay to avoid throttling
        time.sleep(0.1)
        print("-" * 50)
    
    print(f"\nTest completed!")
    print(f"Successful sends: {successful_sends}")
    print(f"Failed sends: {failed_sends}")
    print(f"Total transactions: {len(transactions)}")

def test_single_record():
    """
    Test with a single hardcoded record (original functionality)
    """
    record = {
        "transactionID": 7,
        "trans_date_trans_time": "2019-08-05 22:20:00",
        "cc_num": "213158000000000",
        "merchant": "fraud_Crona, Kulas and Ernser",
        "category": "gas_transport",
        "amt": 9999909.85,
        "first": "Linh",
        "last": "Luong",
        "gender": "F",
        "street": "Lai Da",
        "city": "Ninh Binh",
        "state": "VN",
        "zip": 45363,
        "lat": 37.4716,
        "long": -81.7266,
        "city_pop": 88,
        "job": "Psychologist",
        "dob": "2009-07-16",
        "trans_num": "8c0625082f2dd50be3f2591f8b4b53a2",
        "unix_time": 1325376065,
        "merch_lat": 136.4301244,
        "merch_long": 81.557866,
        "is_fraud": "1"
    }

    kinesis = boto3.client(
        'kinesis',
        region_name='ap-southeast-2',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    response = kinesis.put_record(
        StreamName='anomaly-transaction-ingesting-stream',
        Data=json.dumps(record),
        PartitionKey='transactionID'
    )

    print(json.dumps(response, indent=4, default=str))

if __name__ == "__main__":
    # Choose which test to run
    print("Choose test mode:")
    print("1. Test with fraud_transactions_10.csv")
    print("2. Test with single hardcoded record")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_fraud_transactions_flow()
    elif choice == "2":
        test_single_record()
    else:
        print("Invalid choice. Running CSV test by default...")
        test_fraud_transactions_flow()

