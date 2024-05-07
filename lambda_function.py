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
    bucket_name = "semir-test"
    S3Client.download_file('semir-test', 'priv-key/semir-Lambda.pem', '/tmp/keyname.pem')
    pem_key = paramiko.RSAKey.from_private_key_file("/tmp/keyname.pem")
    
    #Create a new client
    SSH_Client = paramiko.SSHClient()
    SSH_Client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host ="54.198.63.112"
    logging.basicConfig(level=logging.DEBUG)
    SSH_Client.connect(hostname = host, username = "ec2-user", pkey = pem_key)
    
    # Create an SFTP client
    SFTP_Client = SSH_Client.open_sftp()
    
    # Path to the source directory on the SFTP server
    s_path = '/home/ec2-user/source_dir/'

    # Transfer all files from the source directory
    for filename in SFTP_Client.listdir(s_path):
        remote_file_path = os.path.join(s_path, filename)
        local_file_path = '/tmp/' + filename
        SFTP_Client.get(remote_file_path, local_file_path)
        S3Client.upload_file(local_file_path, bucket_name, 'sftp-files/' + filename)
        SFTP_Client.remove(remote_file_path)

    # Close the SFTP and SSH connections
    SFTP_Client.close()
    SSH_Client.close()

    return {
        'statusCode': 200,
        'body': 'SFTP file transfer permitted'
    }
