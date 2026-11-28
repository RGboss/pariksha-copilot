import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.29.94', port=8022, username='u0_a162', password='ubuntu')

stdin, stdout, stderr = ssh.exec_command('ps -ef')
lines = stdout.read().decode().splitlines()
for l in lines:
    print(l)

ssh.close()
