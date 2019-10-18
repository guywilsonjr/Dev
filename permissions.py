from aws_cdk.iam import aws_iam as iam

SSM_USER_DATA_ACTIONS = ['ssm:UpdateInstanceInformation']

SSM_SESSION_MANAGER_ACTIONS = [
    'ssmmessages:CreateDataChannel', 
    'ssmmessages:OpenControlChannel',
    'ssmmessages:OpenDataChannel', 
    'ssmmessages:CreateControlChannel',
    's3:GetEncryptionConfiguration']

SSM_POLICY = iam.Policy(
    self, 
    'SSMPolicy', 
    statements=iam.PolicyStatement(
        actions=SSM_SESSION_MANAGER_ACTIONS + SSM_USER_DATA_ACTIONS, resources='*'))

CODE_PIPELINE_POLICY = iam.ManagedPolicy.from_aws_managed_policy_name('AWSCodePipelineFullAccess')

def attach_ssm_policy(role: IAM.IRole) -> None:
    SSM_POLICY.attach_to_role(role)
    
def attach_code_pipeline_policy(role: IAM.IRole) -> None:
    CODE_PIPELINE_POLICY.attach_to_role(role)
    