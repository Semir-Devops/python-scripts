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

import json
import paramiko
import boto3
import os
import io
import sys

def lambda_handler(event, context):
    # Create a StringIO buffer to capture print statements
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    
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
        
        # Print the loaded configuration
        print(f"Loaded config from S3: {json.dumps(config, indent=2)}")
        
        # Download the private key to /tmp directory
        local_key_path = '/tmp/key.pem'
        s3_client.download_file(bucket_name, private_key_path, local_key_path)
        
        # Load the private key from the local file
        pem_key = paramiko.RSAKey.from_private_key_file(local_key_path)
        
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

        # Get the captured output
        output = buffer.getvalue()
        
        # Reset stdout
        sys.stdout = old_stdout

        # Format the output response
        response = {
            'statusCode': 200,
            'body': 'SFTP file transfer completed successfully',
            'logs': output
        }
        return json.dumps(response, indent=2)
    except Exception as e:
        # Get the captured output
        output = buffer.getvalue()
        
        # Reset stdout
        sys.stdout = old_stdout

        print(f"Error occurred: {str(e)}")
        
        # Format the error response
        response = {
            'statusCode': 500,
            'error': str(e),
            'logs': output
        }
        return json.dumps(response, indent=2)
