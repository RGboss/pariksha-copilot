import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.29.94', port=8022, username='u0_a162', password='ubuntu')

def run_cmd(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
    return stdout.read().decode() + stderr.read().decode()

print('=== TMUX CAPTURE BEFORE ===')
print(run_cmd('tmux capture-pane -pt pariksha:0 -S -10'))

# Let's send Ctrl-C to pariksha:0 and see if we get a prompt
run_cmd('tmux send-keys -t pariksha:0 C-c')
time.sleep(1)
run_cmd('tmux send-keys -t pariksha:0 "echo HELLO_PARIKSHA" C-m')
time.sleep(1)

print('=== TMUX CAPTURE AFTER ===')
print(run_cmd('tmux capture-pane -pt pariksha:0 -S -10'))

ssh.close()
