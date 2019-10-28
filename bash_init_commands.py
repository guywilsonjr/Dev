import typing

# Variables
repo_name='Dev'
env_name = f'{repo_name}Env'
home_dir = '/home/ec2-user'
nvm_dir = f'/.nvm'
env_dir = f'{home_dir}/{env_name}'
repo_dir = f'{env_dir}/{repo_name}'
python_version = '3.7'
shell = 'bashrc'


def alias_command(alias: str, command: str) -> str:
    return f'newalias {alias} "{command}"'

def ec2_command(command: str) -> str:
    return f'sudo -u ec2-user {command}'

def yum_install(command: str) -> str:
    return f'yum -y install {command}'
    
#Initial update Commands
yum_update = 'yum -y update'
yum_upgrade = 'yum -y upgrade'
install_nodejs = yum_install('nodejs')
install_git = yum_install('git')
install_python = yum_install('python3')
install_gcc = yum_install('gcc-c++')


# NVM/Node installation commands
download_nvm = 'curl https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh > /home/ec2-user/install.sh'
install_nvm = 'chmod +x install.sh && ./install.sh'
install_node = 'nvm install node'

source_nvm = f'source {nvm_dir}/nvm.sh && echo "source {nvm_dir}/nvm.sh" >> /root/.bashrc'
source_comp = f'source {nvm_dir}/bash_completion && echo "source {nvm_dir}/bash_completion" >> /root/.bashrc && \cp -r {nvm_dir}/ /home/ec2-user'

#Setup DevEnv
create_venv = ec2_command(f'python3 -m venv {env_dir}')
git_clone = ec2_command(f'git clone https://github.com/guywilsonjr/{repo_name} {repo_dir}')
grant_git_perms = f'chown ec2-user {repo_dir}/.git/* && chown ec2-user {repo_dir}/* && chown ec2-user {repo_dir}'
install_aws_cdk = ec2_command('npm install -g aws-cdk')
dev_env_setup_commands = [create_venv, git_clone, grant_git_perms, install_aws_cdk]
change_user = 'su ec2-user'

# alias commands
new_alias = f'function newalias(){{ echo "alias $1=\'$2\'" >> {home_dir}/.{shell} && source {home_dir}/.{shell} }};  }}'
gstat = alias_command('gstat', 'git status')
gpush = alias_command('gpush', 'git push origin master')
gfet = alias_command('gfet', 'git fetch')
gstatus = alias_command('gstatus', 'gfet && gstat')

deploy = alias_command('deploy', 'cdk deploy --require-approval never')
diff = alias_command('diff', 'cdk diff')
go_home = f'cd {home_dir}'
install_nak = ec2_command('npm install -g nak')
install_cloud9 = 'nvm install node && chmod +x c9install.sh && ./c9install.sh'
download_cloud9 = 'curl -L https://raw.githubusercontent.com/c9/install/master/install.sh > c9install.sh'

setup_auto_start_dir = f'echo "cd {repo_dir}" >> {home_dir}/.{shell}'
source_nvm_all = f'echo "source {home_dir}/.nvm/.nvm.sh && source {home_dir}/.nvm/bash_completion" >> {home_dir}/.{shell}'


add_cloud9_ssh_key = f'echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDOxeUOO6tA55DARFySNv60fIALefIw9fleGvDZOMY7cmNle7cAbOk7/B4kQHyPKdL/IMe9e3h11Pg8425LtTjAZMxcC787nDi282p4gz5o0d8MFjomyD3nJIOWAfIMli4XVso5qrdKFsuFuXtSd1jfYr4uqLCm0c0xIMtMA2RvJ1nt4A177nKlfWk3wNCz1DsXtv1tXMRdG3F9hVZDevY6iG+ppYpLY8NGuFuVxJlHufpaIlXS6bVeduhLvc48WmNpnk0gGUsG4ieMoPli33eQqpXXXJr0l1XkL67aAvJdRdxGnFgH5dwZrLfKDXyYhZkQOiULT48ATk+ZXMG1be57bAks+rJsMOoNadqPTVU5vP3DzhVnc9d0Qr9wcLyqLoWtwBQcpll4aLpAsgmB2vxw6d/G2iX3/Z+/QvdKD9PItMTvDStcPEXbZOK4Vvfx/hZlPcm3Q/9r6KMZwsnpgyAFkCL3u5fwB24l9ihh3evNJwRGmXCQyrq437Arpz8178xMKkV7GZTwo9gUhDerbYUgO7NZ3I2XauYHEGC2upIEyT6yRkJXB9n1Tk3wMFhNlpbTYZX+O93CtxhJoj8h2QlFB1ftEKv/exDIw1YQwxTOxXPObERT+UP3VVIQOsuGjsIHz8p1rKfMPJZnte1qi2cD9fERXK5bnccXDXsZifkJcw== DevUser+936272581790@cloud9.amazon.com" >> {home_dir}/.ssh/authorized_keys'



def generate_parallel_commands(commands: list) -> str:
    return ' & '.join(commands)


set_x = 'set -x'
keep_logs = f'exec > >(tee {home_dir}/user-data.log | logger -t user-data)'
echo_start = 'echo START'
get_time = 'date "+%Y-%m-%d %H:%M:%S"'

dependency_mappings = {
    yum_update: keep_logs,
    yum_upgrade: yum_update,
    set_x: None,
    keep_logs: set_x,
    echo_start: keep_logs,
    install_gcc: keep_logs,
    install_git: keep_logs,
    add_cloud9_ssh_key: keep_logs,
    #change_user: install_gcc,
    download_cloud9: install_python,
    go_home: install_gcc,
    download_nvm: go_home,
    install_nvm: download_nvm,
    source_nvm: source_nvm_all,
    source_comp: source_nvm,
    source_nvm_all: install_nvm,
    install_node: install_cloud9,
    setup_auto_start_dir: git_clone,
    install_cloud9: download_cloud9,
    get_time: keep_logs,
    install_python: source_comp,
    create_venv: install_cloud9,
    git_clone: create_venv,
}
'''
    rpm: 
      epel: "http://download.fedoraproject.org/pub/epel/5/i386/epel-release-5-4.noarch.rpm"
    yum: 
      python3: []
      gcc-c++: []
      nodejs: []
    python3:
    
    node:
    '''
def get_map_ranks():
    rank_maps = dict()
    rank = 0
    target_list = []
    command_length = len(dependency_mappings)
    while(len(rank_maps) != command_length):
        new_target_list = []
        for key, value in dependency_mappings.items():
            if (key not in target_list)  and (value in target_list or value == None):
                rank_maps[key] = rank
                new_target_list.append(key)
                
        target_list = target_list + new_target_list
        rank = rank + 1
    
    return rank_maps
    

def all_dependencies_satisfied(command: str, dependency_list: str, already_executed_list: str) -> bool:
     
     deps_executed = [ ( dep in already_executed_list) for dep in dependency_list]
     if False in deps_executed:
         return False
         
     return True
def get_parallel_commands():
    ordered_list = None
    map_ranks = get_map_ranks()
    
    for i in range(1 + max(map_ranks.values())):
        tiered_list = []
        for command, rank in map_ranks.items():
            if rank == i:

                tiered_list.append(f'({command})')
        
        parallel_command_core = generate_parallel_commands(tiered_list)
        
        if ordered_list:
            ordered_list = ordered_list + [parallel_command_core]
        else:
            ordered_list = [parallel_command_core]
            
    return ordered_list

    
def get_serial_commands():
    
    map_ranks = get_map_ranks()
    tiered_list = []
    for i in range(1 + max(map_ranks.values())):
        
        for command, rank in map_ranks.items():
            if rank == i:

                tiered_list.append(command)
        
            
    return tiered_list

INIT_COMMANDS = ''#  get_serial_commands()

[print(command) for command in INIT_COMMANDS]




