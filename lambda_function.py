'''
This python script runs an AWS Lambda function that uses SFTP
to send files securely from an EC2 instance into a S3 Bucket.
I have attached a paramiko library with all its dependencies
to be able to run this function named "SFTP-ParamikoLayer.zip"
Update:
The parameters are being passed from a config.json file,
some of them are passed from the payload feature on cli
which is equivalent to a test-event parameter on the console
'''

import logging
import json
import paramiko
import boto3
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

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
        private_key_path = config['key_path']  # Ensure the key name matches the JSON structure
        
        # Log the loaded configuration
        logger.debug(f"Loaded config from S3: {json.dumps(config)}")
        
        # Download the private key to /tmp directory
        local_key_path = '/tmp/key.pem'
        s3_client.download_file(bucket_name, private_key_path, local_key_path)
        
        # Load the private key from the local file
        pem_key = paramiko.RSAKey.from_private_key_file(local_key_path)
        
        # Create a new SSH client
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the SFTP server
        logger.debug(f"Connecting to {host}:{port} as {username}...")
        ssh_client.connect(hostname=host, port=port, username=username, pkey=pem_key)
        
        # Create an SFTP client
        sftp_client = ssh_client.open_sftp()
        
        # Transfer files from the source directory directly to S3
        logger.debug(f"Listing files in {source_path}...")
        for filename in sftp_client.listdir(source_path):
            remote_file_path = os.path.join(source_path, filename)
            logger.debug(f"Streaming {filename} to S3...")
            
            with sftp_client.file(remote_file_path, 'rb') as remote_file:
                s3_client.upload_fileobj(remote_file, bucket_name, os.path.join(dest_path, filename))
                
            sftp_client.remove(remote_file_path)
            logger.info(f"Transferred and removed {filename} from SFTP server.")
        
        # Close the SFTP and SSH connections
        sftp_client.close()
        ssh_client.close()

        return {
            'statusCode': 200,
            'body': json.dumps('SFTP file transfer completed successfully\n')
        }
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
