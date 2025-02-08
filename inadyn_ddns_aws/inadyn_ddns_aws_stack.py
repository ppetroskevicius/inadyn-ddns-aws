import os

from aws_cdk import (
  CfnOutput,
  Stack,
)
from aws_cdk import (
  aws_apigateway as apigateway,
)
from aws_cdk import (
  aws_iam as iam,
)
from aws_cdk import (
  aws_lambda as _lambda,
)
from constructs import Construct


class InadynDdnsAwsStack(Stack):
  def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # AWS Route 53 Hosted Zone ID and the API key has to be set in the environment
    HOSTED_ZONE_ID = os.environ["AWS_HOSTED_ZONE_ID"]
    API_KEY = os.environ["API_KEY"]

    # Create IAM Policy with Least Privilege for Route 53 updates
    route53_policy = iam.PolicyStatement(
      effect=iam.Effect.ALLOW,
      actions=["route53:ChangeResourceRecordSets", "route53:ListResourceRecordSets"],
      resources=[f"arn:aws:route53:::hostedzone/{HOSTED_ZONE_ID}"],
    )

    # Create IAM Role for Lambda with CloudWatch Logs permissions
    lambda_role = iam.Role(self, "Route53DdnsLambdaRole", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))
    lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
    lambda_role.add_to_policy(route53_policy)

    # Create Lambda function
    lambda_function = _lambda.Function(
      self,
      "Route53DdnsLambda",
      runtime=_lambda.Runtime.PYTHON_3_9,
      handler="lambda_function.lambda_handler",
      code=_lambda.Code.from_asset("lambda"),
      role=lambda_role,
      environment={
        "HOSTED_ZONE_ID": HOSTED_ZONE_ID,
        "API_KEY": API_KEY,
      },
    )

    # Create API Gateway
    api = apigateway.RestApi(
      self,
      "Route53DdnsAPI",
      rest_api_name="Route 53 DDNS API",
      description="API for In-a-Dyn compatible Dynamic DNS updates",
    )

    # Create usage plan with throttling
    plan = api.add_usage_plan("Route53DdnsUsagePlan", name="ddns-usage-plan", throttle=apigateway.ThrottleSettings(rate_limit=0.1, burst_limit=3))

    # Create API Gateway endpoint: /update
    update_resource = api.root.add_resource("update")
    update_resource.add_method(
      "GET",
      apigateway.LambdaIntegration(lambda_function),
      api_key_required=False,  # Changed to false as we'll use basic auth
    )

    # Output the API Gateway URL
    CfnOutput(self, "ApiUrl", value=api.url)
