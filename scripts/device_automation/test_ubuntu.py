import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.29.94', port=8022, username='u0_a162', password='ubuntu')

def run(cmd, timeout=15):
    print(f'>>> RUNNING (get_pty=True): {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=timeout)
    out = stdout.read().decode()
    print('OUTPUT:\n', out)
    return out

run('proot-distro login ubuntu -- uname -a')
ssh.close()
