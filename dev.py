import json
from aws_cdk import core
from aws_cdk import aws_iam as iam
from PyAwnfra.pyawnfra.secretsmanager.secretsmanager import PreDefinedSecret, Secrets
from PyAwnfra.pyawnfra.iam.actions import IAMIAMActions, SecretsManagerActions, CFNActions, KMSActions
from PyAwnfra.pyawnfra import iam as pyiam
app = core.App()



class DevStack(core.Stack):

    def __init__(self, parent: core.App, id: str):
        super().__init__(parent, id)
        self.sb_user = iam.User(
            self,
            'SBUser'
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
            'DeployRole',
            assumed_by=pyiam.CFN_PRINCIPAL,
            inline_policies={'Policy': iam.PolicyDocument(
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
                        'arn:aws:{}:{}:{}:*{}*'.format(SecretsManagerActions.name, self.region, self.account,  self.stack_name),
                        'arn:aws:{}:{}:{}:*{}*'.format(SecretsManagerActions.name, self.region, self.account, self.aws_cred_secret.secret_name)
                    ]
                ), iam.PolicyStatement(
                    actions=[KMSActions.FULL_ACCESS],
                    resources=['*'])
                ])})


dev_stack = DevStack(app, "Dev")
app.synth()
