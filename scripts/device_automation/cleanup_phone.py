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

run('tmux kill-server')
run('pkill -9 -f proot')
run('pkill -9 -f nginx')
run('pkill -9 -f uvicorn')
run('pkill -9 -f gunicorn')
run('pkill -9 -f tail')

time.sleep(2)
print('CHECK REMAINING PROCESSES:')
run('ps -ef')

ssh.close()
