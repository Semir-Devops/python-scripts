'''
This python script runs an AWS Lambda function that uses SFTP
to send files securely from an EC2 instance into a S3 Bucket.
I have attached a paramiko library with all its dependencies
to be able to run this function named "SFTP-ParamikoLayer.zip"
'''

import logging
import json
import paramiko
import boto3
import os

def lambda_handler(event, context):
    S3Client = boto3.client('s3')
    bucket_name = "name-of-s-bucket"
    S3Client.download_file('name-of-bucket', 'key-path-stored-on-S3', '/tmp/keyname.pem') #'/tmp/keyname.pem' parameter stores key within Lambda environment
    pem_key = paramiko.RSAKey.from_private_key_file("/tmp/keyname.pem")
    
    #Create a new client
    SSH_Client = paramiko.SSHClient()
    SSH_Client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host ="###.###.###.###" #thi is IP address of the host EC2 instance
    logging.basicConfig(level=logging.DEBUG)
    SSH_Client.connect(hostname = host, username = "ec2-user", pkey = pem_key)
    
    # Create an SFTP client
    SFTP_Client = SSH_Client.open_sftp()
    
    # Path to the source directory on the SFTP server
    s_path = '/home/ec2-user/source_dir/' #this can be any directory, this is purely an example

    # Transfer all files from the source directory
    for filename in SFTP_Client.listdir(s_path):
        remote_file_path = os.path.join(s_path, filename)
        local_file_path = '/tmp/' + filename
        SFTP_Client.get(remote_file_path, local_file_path)
        S3Client.upload_file(local_file_path, bucket_name, 'sftp-files/' + filename)
        #'sftp-files' is the directory where files transferred will be directed on S3 bucket, must be created on S3 bucket
        SFTP_Client.remove(remote_file_path)

    # Close the SFTP and SSH connections
    SFTP_Client.close()
    SSH_Client.close()

    return {
        'statusCode': 200,
        'body': 'SFTP file transfer permitted'
    }
