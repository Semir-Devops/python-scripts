import paramiko
import os

# Define the path to the private key file
private_key_path = '/home/semir-testing/SFTP/private-key.pem'

# Define the SFTP details
host = '54.146.167.126'
port = 22
username = 'ec2-user'
remote_path = '/home/ec2-user/source_dir'
local_path = '/home/semir-testing/SFTP-files'

# Load the RSA private key with passphrase
private_key = paramiko.RSAKey.from_private_key_file(private_key_path)

# Create an SSH client
ssh_client = paramiko.SSHClient()

# Automatically add the EC2 instance's host key
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect to the EC2 instance using the private key
ssh_client.connect(hostname=host, port=port, username=username, pkey=private_key)

# Create an SFTP session
sftp = ssh_client.open_sftp()

# Transfer files from local machine to EC2 instance
for file_name in os.listdir(local_path):
    local_file_path = os.path.join(local_path, file_name)
    remote_file_path = os.path.join(remote_path, file_name)
    sftp.put(local_file_path, remote_file_path)

# Close the SFTP session and the SSH connection
sftp.close()
ssh_client.close()

print("Files transferred successfully.")
