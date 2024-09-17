#!/usr/bin/env python3

from os import getenv

import aws_cdk as cdk
from dotenv import load_dotenv

from lighthouse.lighthouse_stack import LighthouseStack

load_dotenv()

env_USA = cdk.Environment(account=getenv("AWS_ACCOUNT_ID"), region="us-east-1")


app = cdk.App()
LighthouseStack(app, "LighthouseStack", env=env_USA)

app.synth()
