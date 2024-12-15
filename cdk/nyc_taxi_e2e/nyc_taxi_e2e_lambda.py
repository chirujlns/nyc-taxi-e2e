from aws_cdk import(
    aws_lambda as lambda_1,
    aws_s3 as s3,
    aws_iam as iam,
    Stack
)

from constructs import Construct

class NycTaxiE2ELambda(Construct):
    def __init__(self, scope:Construct, id: str, **kwargs) -> None:
        super().__init__(scope,id,**kwargs)