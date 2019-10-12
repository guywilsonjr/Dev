import typing
repo_name='Dev'
env_name = f'{repo_name}Env'
python_version = '3.7'
alinux_update_command = 'yum -y update && yum -y upgrade && su ec2-user && cd /usr/lib'
install_npm_command = 'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash && . /home/ec2-user/.nvm/nvm.sh && nvm install node'
install_git_command = 'yum -y install git'
install_python_command = 'yum -y install python3.7'
change_user_command = 'cd /home/ec2-user && su ec2-user'
install_aws_cdk_command = 'npm install -g aws-cdk'
create_venv_command = f'python3 -m venv {env_name}',
git_clone_commands = f'sudo ec2-user git clone https://github.com/guywilsonjr/{repo_name} && cd {repo_name}'
install_pip_reqs = 'source ../bin/activate && sudo pip3 install -r requirements.txt'
cdk_boot_command = 'cdk bootstrap 936272581790/us-west-2'
new_alias_command = 'function newalias(){   echo "alias $1=\'$2\'" >> ~/.zshrc && source ~/.zshrc; }'
git_alias_commands = [
    'newalias gstat "git status"',
    'newalias gpush "git push origin master"',
    'newalias gfet "git fetch"',
    'newalias gstatus "gfet && gstat"',
    'newalias deploy "cdk deploy --require-approval never"',
    'newalias diff "cdk diff"']

tier_0_commands = [alinux_update_command, new_alias_command]
tier_1_commands = [install_npm_command, install_git_command, install_python_command]
tier_2_commands = [install_aws_cdk_command, change_user_command]
tier_3_commands = [create_venv_command]
tier_4_commands = [f'cd {env_name}']
tier_5_commands = [git_clone_commands]
tier_6_commands = [f'cd {repo_name}']
tier_7_commands = [install_pip_reqs]

command_tier_list = [tier_0_commands, tier_1_commands, tier_2_commands, tier_1_commands, tier_4_commands, tier_5_commands, tier_6_commands, tier_7_commands]
def generate_parallel_commands(commands):
    return ' & '.join(commands)
    
INIT_COMMANDS = [generate_parallel_commands(commands) for commands in command_tier_list]
print('COMMANDS!!')
print(INIT_COMMANDS)