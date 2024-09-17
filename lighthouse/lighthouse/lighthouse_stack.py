from os import path

import aws_cdk.aws_apigatewayv2 as api_gw
import aws_cdk.aws_apigatewayv2_integrations as intgs
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_iam as iam
from aws_cdk import BundlingOptions
from aws_cdk import CfnOutput
from aws_cdk import Duration
from aws_cdk import Stack
from aws_cdk import aws_lambda as lmbda
from constructs import Construct

DIRNAME = path.dirname(__file__)


class LighthouseStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_role = iam.Role(
            self,
            "LighthouseLambdaRole",
            role_name="LighthouseLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        dynamodb.TableV2(
            self,
            "TasksTable",
            partition_key=dynamodb.Attribute(
                name="taskId", type=dynamodb.AttributeType.STRING
            ),
            billing=dynamodb.Billing.on_demand(),
            table_name="TasksTable",
        )

        lambda_fxn = lmbda.Function(
            self,
            "TasksFxn",
            function_name="TasksFunction",
            runtime=lmbda.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=lmbda.Code.from_asset(
                path.join(DIRNAME, "src"),
                bundling=BundlingOptions(
                    image=lmbda.Runtime.PYTHON_3_11.bundling_image,
                    command=[
                        "bash",
                        "-c",
                        "pip install -r requirements.txt -t /asset-output && cp -au . /asset-output",
                    ],
                    user="root",
                ),
            ),
            role=lambda_role,
            environment={},
        )

        # Attach policies to Lambda Execution role
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
        )

        http_api = api_gw.HttpApi(
            self,
            "LighthouseApi",
            api_name="LighthouseApi",
            cors_preflight=api_gw.CorsPreflightOptions(
                allow_methods=[
                    api_gw.CorsHttpMethod.GET,
                    api_gw.CorsHttpMethod.POST,
                    api_gw.CorsHttpMethod.PUT,
                    api_gw.CorsHttpMethod.DELETE,
                ],
                allow_origins=["*"],
                max_age=Duration.days(10),
            ),
        )

        http_api.add_routes(
            path="/tasks",
            methods=[api_gw.HttpMethod.POST],
            integration=intgs.HttpLambdaIntegration(
                "LambdaProxyIntegration", handler=lambda_fxn
            ),
        )

        http_api.add_routes(
            path="/tasks/{id}",
            methods=[
                api_gw.HttpMethod.GET,
                api_gw.HttpMethod.PUT,
                api_gw.HttpMethod.DELETE,
            ],
            integration=intgs.HttpLambdaIntegration(
                "LambdaProxyIntegration", handler=lambda_fxn
            ),
        )

        # Output
        CfnOutput(
            self,
            "API Endpoint",
            description="API Endpoint",
            value=http_api.api_endpoint,
        )
