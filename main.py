import paramiko
hostname = '192.168.0.113' 
myuser   = 'root'
mySSHK   = 'id_rsa'
pkey = paramiko.RSAKey.from_private_key_file(mySSHK)
sshcon   = paramiko.SSHClient() 
sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
sshcon.connect(hostname, username=myuser, pkey=pkey)