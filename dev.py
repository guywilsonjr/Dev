from aws_cdk import core
from dev_stack import DevStack

app = core.App()
DevStack(app, "Dev", env={'region': 'us-west-2'})
app.synth()
