#!/usr/bin/env python3
import aws_cdk as cdk

from inadyn_ddns_aws.inadyn_ddns_aws_stack import InadynDdnsAwsStack

app = cdk.App()
InadynDdnsAwsStack(app, "InadynDdnsAwsStack")
app.synth()
