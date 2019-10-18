import typing

# Variables
repo_name='Dev'
env_name = f'{repo_name}Env'
home_dir = '/home/ec2-user'
nvm_dir = f'{home_dir}/.nvm'
env_dir = f'{home_dir}/{env_name}'
repo_dir = f'{env_dir}/{repo_name}'
python_version = '3.7'
shell = 'bashrc'


def alias_command(alias: str, command: str) -> str:
    return f'newalias {alias} "{command}"'

def ec2_command(command: str) -> str:
    return f'sudo -u ec2-user {command}'

#Initial update Commands
yum_update = 'yum -y update'
yum_upgrade = 'yum -y upgrade && touch ~/.zshrc'
install_git = 'yum -y install git'
install_python = 'yum -y install python3.7'
initial_commands=[yum_update, yum_upgrade, install_git, install_python]


# NVM/Node installation commands
download_nvm = ec2_command('curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh') + ' | ' + ec2_command('bash')
install_node = 'nvm install node'

source_nvm = f'source {nvm_dir}/nvm.sh'
source_comp = f'source {nvm_dir}/bash_completion'

nvm_commands = [download_nvm, source_nvm, source_comp, install_node]
#Setup DevEnv
create_venv = f'python3 -m venv {env_dir}'
git_clone = ec2_command(f'git clone https://github.com/guywilsonjr/{repo_name} {repo_dir}')
grant_git_perms = f'chown ec2-user {repo_dir}/.git/* && chown ec2-user {repo_dir}/* && chown ec2-user {repo_dir}'
source_env = f'source {env_dir}/bin/activate'
install_pip_mods = f'pip3 install -r {repo_dir}/requirements.txt'
install_aws_cdk = 'npm install -g aws-cdk'
dev_env_setup_commands = [create_venv, git_clone, grant_git_perms, source_env, install_pip_mods, install_aws_cdk]
'''
https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-getting-started-instance-profile.html
'''
# alias commands
new_alias = f'function newalias(){{ echo "alias $1=\'$2\'" >> {home_dir}/.{shell} && source {home_dir}/.{shell} }};  }}'
gstat = alias_command('gstat', 'git status')
gpush = alias_command('gpush', 'git push origin master')
gfet = alias_command('gfet', 'git fetch')
gstatus = alias_command('gstatus', 'gfet && gstat')
deploy = alias_command('deploy', 'cdk deploy --require-approval never')
diff = alias_command('diff', 'cdk diff')
setup_auto_start_dir = f'echo "cd {repo_dir}" >> {home_dir}/.{shell}'

alias_commands = [new_alias, gstat, gpush, gfet, gstatus, deploy, diff]

command_list = initial_commands + nvm_commands + dev_env_setup_commands +  alias_commands + [setup_auto_start_dir]


def generate_parallel_commands(commands: list) -> str:
    return ' & '.join(commands)
    

dependency_mappings = {
    yum_update: None,
    yum_upgrade: yum_update,
    install_git: yum_upgrade,
    install_python: install_git,
    download_nvm: install_git,
    source_nvm: download_nvm,
    source_comp:download_nvm,
    create_venv: install_python,
    git_clone: install_git,
    grant_git_perms: git_clone,
    source_env: create_venv,
    install_aws_cdk: install_node
}
'''
ordered_command_list = [
    yum_update,
    yum_upgrade,
    install_git,
    download_nvm,
    source_nvm,
    source_comp,
    install_node,
    install_python,
    create_venv,
    git_clone,
    grant_git_perms,
    source_env,
    install_pip_mods,
    install_aws_cdk
    ]
'''
def get_parallel_commands(ordered_command_dict):
    list_tier = []
    for i in range(max(ordered_command_dict.values())):
        for command in ordered_command_dict.keys():
            if ordered_command_dict[str(command)] == i:
                list_tier.append(str(command))
    return list_tier

    
print('Sorted Commands', command_list)
logger_commands = ['set -x', f'exec > >(tee {home_dir}/user-data.log | logger -t user-data)', 'echo START', 'date "+%Y-%m-%d %H:%M:%S"']
INIT_COMMANDS =   logger_commands + command_list
print(INIT_COMMANDS)