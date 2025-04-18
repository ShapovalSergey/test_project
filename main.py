import paramiko
import threading, time
import re
import sys

class Core():
    def __init__(self):
        self.status = False
        self.pg_conf_path = ""
        self.install_status=False
        
    def start(self):
        self.scanf()
        hosts_list = list(filter(None, re.split(' |,',self.hosts)))
        self.min_load = 101.0
        self.fhost = ""
        self.fhostdistro = ""
        for host in hosts_list:
            self.get_host_name_type(host)
        print("\n#Hostname or IP: "+self.fhost)
        print("\n#Distribution name: "+self.fhostdistro)
        thread = threading.Thread(target=self.install, args=[self.fhost, self.fhostdistro])
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
        if self.install_status:
            print("#Installation succeeded\n")
        else:
            print("#Installation failed\n")
            sys.exit()
        print("#postgresql.service status\n")
        self.check_status(self.fhost)
        self.conf_files(self.fhost)

    def get_host_name_type(self,host):
        hostname = host
        myuser   = 'root'
        mySSHK   = 'id_rsa'
        pkey = paramiko.RSAKey.from_private_key_file(mySSHK)
        sshcon   = paramiko.SSHClient() 
        sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        sshcon.connect(hostname, username=myuser, pkey=pkey)
        stdin, stdout, stderr = sshcon.exec_command("cat /proc/loadavg")
        curr_host_load = float(stdout.read().decode(encoding='UTF-8').split()[0])
        if self.min_load > curr_host_load: 
            self.min_load = curr_host_load
            self.fhost = host
            stdin, stdout, stderr = sshcon.exec_command("cat /etc/*-release | grep NAME | head -n1 | cut -d '=' -f2")
            self.fhostdistro = stdout.read().decode(encoding='UTF-8')
        sshcon.close()

    def check_status(self, hostname):
        hostname = hostname
        myuser   = 'root'
        mySSHK   = 'id_rsa'
        pkey = paramiko.RSAKey.from_private_key_file(mySSHK)
        sshcon   = paramiko.SSHClient() 
        sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        sshcon.connect(hostname, username=myuser, pkey=pkey)
        stdin, stdout, stderr = sshcon.exec_command("systemctl status postgresql.service")
        print(stdout.read().decode(encoding='UTF-8'))
        sshcon.close()

    def conf_files(self, hostname):
        hostname = hostname
        myuser   = 'root'
        mySSHK   = 'id_rsa'
        pkey = paramiko.RSAKey.from_private_key_file(mySSHK)
        sshcon   = paramiko.SSHClient() 
        sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        sshcon.connect(hostname, username=myuser, pkey=pkey)
        stdin, stdout, stderr = sshcon.exec_command("sed -i \"s|#listen_addresses = 'localhost'|listen_addresses = '*'|\" " + self.pg_conf_path + "postgresql.conf")
        stdout.read().decode(encoding='UTF-8')
        stdin, stdout, stderr = sshcon.exec_command("sed -i \"s|#port = 5432|port = 5432|\" " + self.pg_conf_path + "postgresql.conf")
        stdout.read().decode(encoding='UTF-8')
        stdin, stdout, stderr = sshcon.exec_command("systemctl restart postgresql.service")
        stdout.read().decode(encoding='UTF-8')
        stdin, stdout, stderr = sshcon.exec_command("su -c \"psql -c \\\"CREATE ROLE student WITH LOGIN SUPERUSER PASSWORD 'password'\\\"\" postgres")
        stdout.read().decode(encoding='UTF-8')
        stdin, stdout, stderr = sshcon.exec_command("echo \"host\t\tall\tstudent\t\t192.168.0.109/32\tmd5\n\" >>" + self.pg_conf_path + "pg_hba.conf")
        stdout.read().decode(encoding='UTF-8')
        stdin, stdout, stderr = sshcon.exec_command("su -c \"psql -c \\\"SELECT 1;\\\"\" postgres")
        print("#Database check (SELECT 1)\n\n"+stdout.read().decode(encoding='UTF-8'))
        sshcon.close()

    def install(self, hostname, hostdistro):
        hostname = hostname
        myuser   = 'root'
        mySSHK   = 'id_rsa'
        pkey = paramiko.RSAKey.from_private_key_file(mySSHK)
        sshcon   = paramiko.SSHClient() 
        sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        sshcon.connect(hostname, username=myuser, pkey=pkey)
        if hostdistro.startswith("\"Deb"):
            stdin, stdout, stderr = sshcon.exec_command("apt install -y postgresql-15 postgresql-contrib")
            stdout.read().decode(encoding='UTF-8')
            self.pg_conf_path="/etc/postgresql/15/main/"
        elif hostdistro.startswith("\"Alma"):
            stdin, stdout, stderr = sshcon.exec_command("dnf install -y postgresql-server;  postgresql-setup --initdb ;systemctl enable postgresql.service; systemctl start postgresql.service")
            stdout.read().decode(encoding='UTF-8')
            self.pg_conf_path="/var/lib/pgsql/data/"
        stdin, stdout, stderr = sshcon.exec_command("psql -V")
        if stderr.read().decode(encoding='UTF-8')=="":
            self.install_status = True
        sshcon.close()
        self.status = True

    def scanf(self):
        self.hosts = input("Input hostname or Ip-addresses: ")

core = Core()
core.start()
