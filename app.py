from aws_cdk import core
from dev_stack import DevStack

app = core.App()
DevStack(app, "DevStack")
app.synth()
