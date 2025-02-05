import aws_cdk as core
import aws_cdk.assertions as assertions

from inadyn_ddns_aws.inadyn_ddns_aws_stack import InadynDdnsAwsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in inadyn_ddns_aws/inadyn_ddns_aws_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = InadynDdnsAwsStack(app, "inadyn-ddns-aws")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
