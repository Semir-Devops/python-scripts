import os
import boto3
import paramiko
from io import BytesIO
import base64

def lambda_handler(event, context):
    # Get the base64-encoded private key from environment variable
    base64_encoded_private_key = os.getenv('PRIVATE_KEY')

    # Decode the base64-encoded private key
    private_key = base64.b64decode(base64_encoded_private_key)

    # S3 bucket name and key prefix
    bucket_name = 'semir-test'
    s3_key_prefix = 'sftp-files/'

    # Connect to the EC2 instance using paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Load the private key
        private_key_file = BytesIO(private_key)

        # Connect to the EC2 instance
        ssh.connect('44.202.105.110', username='ec2-user', pkey=paramiko.RSAKey(file_obj=private_key_file))

        # Create an SFTP client
        sftp = ssh.open_sftp()

        # Iterate over files in the remote directory
        remote_path = '/home/ec2-user/source_dir/'
        for filename in sftp.listdir(remote_path):
            remote_file_path = os.path.join(remote_path, filename)
            local_file_path = '/tmp/' + filename
            sftp.get(remote_file_path, local_file_path)

            # Upload the file to S3
            s3_client = boto3.client('s3')
            s3_key = s3_key_prefix + filename
            s3_client.upload_file(local_file_path, bucket_name, s3_key)

            # Remove the local file
            os.remove(local_file_path)

        return {
            'statusCode': 200,
            'body': 'Files transferred to S3 successfully'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
    finally:
        # Close the SFTP and SSH connections
        sftp.close()
        ssh.close()
