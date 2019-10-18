import urllib.request
import boto3
from aws_cdk import core, aws_ec2 as ec2, aws_iam as iam
from bash_init_commands import INIT_COMMANDS
repo_name='Dev'
env_name = f'{repo_name}Env'
python_version = '3.7'


ip_address = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/public-ipv4').read().decode()
allow_all_outbound_traffic = True
class DevStack(core.Stack):
    def __init__(self, app: core.Construct, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)
        dev_subnet_type = ec2.SubnetType.PUBLIC
        subnet_name = 'Subnet'
        vpc = ec2.Vpc(
            self, 'VPC', subnet_configuration=[
                ec2.SubnetConfiguration(name=subnet_name,
                                        subnet_type=dev_subnet_type)],
                                        max_azs=1, cidr='10.0.0.0/24',
                                        enable_dns_support=True)
        
        instance_role = iam.LazyRole(self, 
            'InstanceRole',
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
            inline_policies={
                'InstancePolicy': iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=['ssm:UpdateInstanceInformation'],
                            resources=['*']
                        )
                    ]
                )}
        )
            
        ssh_port_number = 22
        port = ec2.Port(protocol=ec2.Protocol.TCP,
        from_port=ssh_port_number,
        to_port=ssh_port_number,
        string_representation='SSH')
        
        sg = ec2.SecurityGroup(self, 'SG', vpc=vpc, allow_all_outbound=True)
        sg.add_ingress_rule(peer=ec2.Peer.ipv4(f'{ip_address}/32'), connection=port)
        
        user_data = ec2.UserData.for_linux()
        for command in INIT_COMMANDS:
            print('logging command: ', command)
            user_data.add_commands(command) 
        ami = ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2, user_data=user_data)       
        instance = ec2.Instance(self, 
            'Instance', 
            role=instance_role,
            instance_type=ec2.InstanceType('t3.nano'),
            allow_all_outbound=allow_all_outbound_traffic,
            machine_image=ami, 
            key_name=repo_name, 
            vpc=vpc, 
            vpc_subnets=ec2.SubnetSelection(subnet_name=subnet_name), 
            security_group=sg)
        instance_output_id = 'InstanceOutput'
        core.CfnOutput(self, instance_output_id, value=instance.instance_public_ip, export_name=instance_output_id)
        
        