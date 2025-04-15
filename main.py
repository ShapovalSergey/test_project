import paramiko
import threading, time
import re

class Core():
    def __init__(self):
        self.status = False
    def start(self):
        self.scanf()
        hosts_list = list(filter(None, re.split(' |,',self.hosts)))
        min_load = 101.0
        fhost = ""
        fhostdistro = ""
        for host in hosts_list:
            print(hosts_list)
            hostname = host
            myuser   = 'root'
            mySSHK   = 'id_rsa'
            pkey = paramiko.RSAKey.from_private_key_file(mySSHK)
            sshcon   = paramiko.SSHClient() 
            sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
            sshcon.connect(hostname, username=myuser, pkey=pkey)
            stdin, stdout, stderr = sshcon.exec_command("cat /proc/loadavg")
            #print(stdout.read().decode(encoding='UTF-8').split()[0])
            curr_host_load = float(stdout.read().decode(encoding='UTF-8').split()[0])
            if min_load > curr_host_load: 
                min_load = curr_host_load
                fhost = host
                stdin, stdout, stderr = sshcon.exec_command("cat /etc/*-release | grep NAME | head -n1 | cut -d '=' -f2")
                fhostdistro = stdout.read().decode(encoding='UTF-8')
        print(fhost)
        print(fhostdistro)
        thread = threading.Thread(target=self.install, args=[fhost, fhostdistro])
        thread.start()
        load_char = ["|", "/", "_", "\\"]
        c = 0
        while not self.status:
            b = "Loading " + load_char[c] 
            print (b, end="\r")
            time.sleep(0.228)
            c+=1
            if c == 4:
                c=0
        print("Installation succeeded")
        hostname = hostname
        myuser   = 'root'
        mySSHK   = 'id_rsa'
        pkey = paramiko.RSAKey.from_private_key_file(mySSHK)
        sshcon   = paramiko.SSHClient() 
        sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        sshcon.connect(hostname, username=myuser, pkey=pkey)
        stdin, stdout, stderr = sshcon.exec_command("systemctl status postgresql.service")
        print(stdout.read().decode(encoding='UTF-8'))



    def install(self, hostname, hostdistro):
        hostname = hostname
        myuser   = 'root'
        mySSHK   = 'id_rsa'
        pkey = paramiko.RSAKey.from_private_key_file(mySSHK)
        sshcon   = paramiko.SSHClient() 
        sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        sshcon.connect(hostname, username=myuser, pkey=pkey)
        if hostdistro.startswith("\"Deb"):
            stdin, stdout, stderr = sshcon.exec_command("apt install -y postgresql postgresql-contrib")
            stdout.read().decode(encoding='UTF-8')
        elif hostdistro.startswith("\"Alma"):
            stdin, stdout, stderr = sshcon.exec_command("dnf install -y postgresql postgresql-contrib")
            stdout.read().decode(encoding='UTF-8')
        time.sleep(5)
        self.status = True

    def scanf(self):
        self.hosts = input("Input hostname or Ip-addresses: ")


core = Core()
core.start()









"""
cat /etc/*-release | grep NAME | head -n1 | cut -d '=' -f2

stdin, stdout, stderr = sshcon.exec_command("apt install -y screenfetch")
if stdout.read().decode(encoding='UTF-8'):
    print("Installation succeeded")
else:
    print(stderr.read().decode(encoding='UTF-8'))

"""