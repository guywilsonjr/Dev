import json
from aws_cdk import core
from aws_cdk import aws_iam as iam
from PyAwnfra.pyawnfra.secretsmanager.secretsmanager import PreDefinedSecret, Secrets
from PyAwnfra.pyawnfra.iam.actions import IAMIAMActions, SecretsManagerActions, CFNActions, KMSActions, LambdaActions
from PyAwnfra.pyawnfra import iam as pyiam
app = core.App()


class DevStack(core.Stack):

    def __init__(self, parent: core.App, name: str):
        super().__init__(parent, name)
        accessible_apps = ['GWJR', 'Dev']
        accessible_lamb_app_regs = ['arn:aws:{}:{}:{}:function:*{}*'.format(LambdaActions.name, self.region, self.account, app) for app in accessible_apps]
        accessible_cfn_app_regs = ['arn:aws:{}:{}:{}:*{}*'.format(CFNActions.name, self.region, self.account, app) for app in accessible_apps]
        accessible_iam_app_regs = ['arn:aws:{}::{}:role/*{}*'.format(IAMIAMActions.name, self.account, app) for app in accessible_apps]
        accessible_app_regs = accessible_cfn_app_regs + accessible_iam_app_regs + accessible_lamb_app_regs

        self.app_access_statement = iam.PolicyStatement(
            actions=[CFNActions.FULL_ACCESS, IAMIAMActions.FULL_ACCESS, LambdaActions.INVOKE_FUNCTION],
            resources=accessible_app_regs)

        self.sb_user = iam.User(
            self,
            'SBUser',
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AWSLambdaReadOnlyAccess'),
                iam.ManagedPolicy.from_aws_managed_policy_name('IAMReadOnlyAccess'),
                iam.ManagedPolicy.from_aws_managed_policy_name('AWSCloudFormationReadOnlyAccess'),
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonRoute53ReadOnlyAccess'),
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'),
                iam.ManagedPolicy(
                self,
                'SBUserPolicy',
                statements=[self.app_access_statement]
            )]
        )

        self.sb_user_access_key = iam.CfnAccessKey(
            self,
            'SBUserAccessKey',
            user_name=self.sb_user.user_name,
            status='Active')
        creds = json.dumps({
            'AWS_ACCESS_KEY_ID': self.sb_user_access_key.ref,
            'AWS_SECRET_ACCESS_KEY': self.sb_user_access_key.attr_secret_access_key
        })

        self.aws_cred_secret = PreDefinedSecret(
            'SBCreds',
            creds
        )

        self.secret_stack = Secrets(
            self,
            "Secrets",
            authorized_users=[self.sb_user],
            predefined_secrets=[self.aws_cred_secret])

        self.deploy_role = iam.Role(
            self,
            'DepRol',
            assumed_by=pyiam.CFN_PRINCIPAL,
            inline_policies={'Pol': iam.PolicyDocument(
                statements=[iam.PolicyStatement(
                    actions=[
                        CFNActions.FULL_ACCESS,
                        IAMIAMActions.FULL_ACCESS,
                        SecretsManagerActions.FULL_ACCESS,
                        KMSActions.FULL_ACCESS
                    ],
                    resources=[
                        'arn:aws:{}:{}:{}:*'.format(KMSActions.name, self.region, self.account),
                        'arn:aws:{}:{}:{}:*{}*'.format(CFNActions.name, self.region, self.account, self.stack_name),
                        'arn:aws:{}::{}:role/*{}*'.format(IAMIAMActions.name, self.account, self.stack_name),
                        'arn:aws:{}::{}:user/*{}*'.format(IAMIAMActions.name, self.account, self.stack_name),
                        'arn:aws:{}::{}:policy/*{}*'.format(IAMIAMActions.name, self.account, self.stack_name),
                        'arn:aws:{}:{}:{}:*{}*'.format(SecretsManagerActions.name, self.region, self.account,  self.stack_name),
                        'arn:aws:{}:{}:{}:*{}*'.format(SecretsManagerActions.name, self.region, self.account, self.aws_cred_secret.secret_name)
                    ] + ['arn:aws:{}::{}:role/*{}*'.format(IAMIAMActions.name, self.account, accessible_app) for accessible_app in accessible_apps]
                ), iam.PolicyStatement(
                    actions=[KMSActions.FULL_ACCESS],
                    resources=['*'])
                ])})
        core.CfnOutput(self, 'DeployRoleArn', value=self.deploy_role.role_arn)
        core.CfnOutput(self, 'SBUserName', value=self.sb_user.user_name)


DevStack(app, "Dev")
app.synth()

