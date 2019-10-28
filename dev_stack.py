import urllib.request
import json
import boto3
from aws_cdk import core, aws_ec2 as ec2, aws_iam as iam
from bash_init_commands import INIT_COMMANDS
repo_name='Dev'
env_name = f'{repo_name}Env'
python_version = '3.7'

SSH_PORT_NUM = 22
HTTP_PORT_NUM = 8080
TLS_PORT_NUM = 443
SSH_PORT = ec2.Port(protocol=ec2.Protocol.TCP, string_representation=f'{SSH_PORT_NUM}', from_port=SSH_PORT_NUM, to_port=SSH_PORT_NUM)
HTTP_PORT = ec2.Port(protocol=ec2.Protocol.TCP, string_representation=f'{HTTP_PORT_NUM}', from_port=HTTP_PORT_NUM, to_port=HTTP_PORT_NUM)
TLS_PORT = ec2.Port(protocol=ec2.Protocol.TCP, string_representation=f'{TLS_PORT_NUM}', from_port=TLS_PORT_NUM, to_port=TLS_PORT_NUM)
ALL_PORTS = ec2.Port(protocol=ec2.Protocol.ALL, string_representation=f'ALL', from_port=0, to_port=65535)

PORT_NAME_MAPPINGS = {SSH_PORT: ('SSH', SSH_PORT), TLS_PORT: ('TLS', TLS_PORT), HTTP_PORT: ('HTTP', HTTP_PORT)}
ALLOWED_SERVICES = {'CLOUD9': SSH_PORT, 'CLOUD9': TLS_PORT, 'EC2': TLS_PORT, 'EC2_INSTANCE_CONNECT': TLS_PORT}

ADDITIONAL_IPS = []
CURRENT_IP = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/public-ipv4').read().decode()
ADDITIONAL_IPS = [CURRENT_IP, '73.53.30.91']

ip_ranges_resp = urllib.request.urlopen('https://ip-ranges.amazonaws.com/ip-ranges.json').read().decode()
ip_ranges = json.loads(ip_ranges_resp)['prefixes']
PDX_RANGES = list(filter(lambda ip_range: ip_range['region'] == 'us-west-2', ip_ranges))

        
class AMI(ec2.IMachineImage):
    def __init__(self, app: core.Construct, id: str):
        super().__init__(app, id)
        
    
    def get_image(self, app: core.Construct):
        return ec2.MachineImageConfig(image_id='ami-00b97faad6302457a', os_type=ec2.OperatingSystemType.LINUX)
        
    def to_json(self):
        return json.dumps(self)
    
        

class DevStack(core.Stack):
    def __init__(self, app: core.Construct, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)
    
        dev_subnet_type = ec2.SubnetType.PUBLIC
        subnet_name = 'Subnet'
        self.vpc = ec2.Vpc(
            self, 'VPC', subnet_configuration=[
                ec2.SubnetConfiguration(name=subnet_name,
                                        subnet_type=dev_subnet_type)],
                                        max_azs=1, cidr='10.0.0.0/24',
                                        enable_dns_support=True)
        
        instance_role = iam.LazyRole(self, 
            'Role',
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
            
        service_sgs = [self.get_service_sg(ip_port=serv) for serv in ALLOWED_SERVICES.items()]
        sg = ec2.SecurityGroup(self, 'SG', vpc=self.vpc, allow_all_outbound=True)
        [sg.add_ingress_rule(peer=serv_sg, connection=TLS_PORT) for serv_sg in service_sgs]
        sg.add_ingress_rule(peer=self.additional_ip_sg(), connection=ALL_PORTS)
        user_data = ec2.UserData.for_linux()
        for command in INIT_COMMANDS:
            #print('logging command: ', command)
            
            user_data.add_commands(command) 
        
        ami = ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2, user_data=user_data)       
        instance = ec2.Instance(self, 
            'Instaedk', 
            role=instance_role,
            instance_type=ec2.InstanceType('t3.nano'),
            allow_all_outbound=True,
            machine_image=ami, 
            key_name=repo_name, 
            vpc=self.vpc, 
            vpc_subnets=ec2.SubnetSelection(subnet_name=subnet_name), 
            security_group=sg)
        #instance.node.children[1].image_id = 'ami-0d4504ae0554bf367'
        instance_output_id = 'InstanceOutput'
        core.CfnOutput(self, instance_output_id, value=instance.instance_public_ip, export_name=instance_output_id)
        
     
     
    def additional_ip_sg(self) -> ec2.SecurityGroup:
        add_sg = ec2.SecurityGroup(self, 'AddSG', vpc=self.vpc, allow_all_outbound=True)
        [add_sg.add_ingress_rule(peer=ec2.Peer.ipv4(f'{ip}/32'), connection=ALL_PORTS) for ip in ADDITIONAL_IPS]
        
        return add_sg
    
        
        
    def get_service_sg(self, ip_port: tuple) -> ec2.SecurityGroup:
        service = ip_port[0]
        port_num = ip_port[1]
        port_name = PORT_NAME_MAPPINGS[port_num][0]
        port = PORT_NAME_MAPPINGS[port_num][1]
        cidrs = [prefix['ip_prefix'] for prefix in PDX_RANGES]
        print("NumCidrs: ", len(cidrs))
        string_representation = port_name
        ranges = list(filter(lambda ip_range: ip_range['service'] == service, PDX_RANGES))
        service_sg = ec2.SecurityGroup(self, f'{service}{port_name}SG', vpc=self.vpc, allow_all_outbound=True)
        service_sg.add_ingress_rule(peer=ec2.Peer.any_ipv4(), connection=port)
        return service_sg
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        