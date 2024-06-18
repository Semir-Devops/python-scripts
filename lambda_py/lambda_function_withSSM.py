import json
import paramiko
import boto3
import io
import os
from botocore.exceptions import ClientError
from io import StringIO

def get_secret():
    secret_name = "Lambda-key"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    return secret

def lambda_handler(event, context):
    try:
        # Hardcoded bucket name and JSON file key for testing
        bucket_name = "semir-test"
        json_file_key = "config/sftp-config.json"
        
        # Read source and dest path from event payload
        source_path = event['source_path']
        dest_path = event['dest_path']
        username = event['username']
        
        # Initialize S3 client
        s3_client = boto3.client('s3')
        
        # Stream the JSON file from S3
        json_file_obj = s3_client.get_object(Bucket=bucket_name, Key=json_file_key)
        config = json.loads(json_file_obj['Body'].read().decode('utf-8'))
        
        host = config['host']
        port = config.get('port', 22)  # Default to port 22 if not specified
        
        # Print the loaded configuration
        print("Loaded config from S3:")
        print(json.dumps(config, indent=2))
        
        # Retrieve the private key from AWS Secrets Manager
        private_key = get_secret()
        
        # Debug: Print the private key
        print("Private Key Retrieved from Secrets Manager:")
        print(private_key)
        
        # Load the private key from the string
        key_file = StringIO(private_key)
        pem_key = paramiko.RSAKey.from_private_key(key_file)
        
        # Create a new SSH client
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the SFTP server
        print(f"Connecting to {host}:{port} as {username}...")
        ssh_client.connect(hostname=host, port=port, username=username, pkey=pem_key)
        
        # Create an SFTP client
        sftp_client = ssh_client.open_sftp()
        
        # Transfer files from the source directory directly to S3
        print(f"Listing files in {source_path}...")
        for filename in sftp_client.listdir(source_path):
            remote_file_path = os.path.join(source_path, filename)
            print(f"Streaming {filename} to S3...")
            
            with sftp_client.file(remote_file_path, 'rb') as remote_file:
                s3_client.upload_fileobj(remote_file, bucket_name, os.path.join(dest_path, filename))
                
            sftp_client.remove(remote_file_path)
            print(f"Transferred and removed {filename} from SFTP server.")
        
        # Close the SFTP and SSH connections
        sftp_client.close()
        ssh_client.close()

        # Format the output response
        response = {
            'statusCode': 200,
            'body': 'SFTP file transfer completed successfully'
        }
        return json.dumps(response, indent=2)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        
        # Return a simple error message
        return {
            'statusCode': 500,
            'error': str(e)
        }
