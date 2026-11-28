import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.29.94', port=8022, username='u0_a162', password='ubuntu')

def run(cmd):
    print(f'>>> {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
    out = stdout.read().decode()
    err = stderr.read().decode()
    print(out + err)

run('tmux new-session -d -s pariksha "bash ~/start-pariksha.sh"')
for i in range(10):
    time.sleep(2)
    print(f'--- Check {i} ---')
    stdin, stdout, stderr = ssh.exec_command('tmux capture-pane -pt pariksha:0 -S -30')
    print(stdout.read().decode())
    if 'ONLINE at :8082' in stdout.read().decode():
        break

ssh.close()
