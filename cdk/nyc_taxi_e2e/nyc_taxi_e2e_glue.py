from aws_cdk import (
    Stack,
    aws_glue as glue,
    aws_iam as iam,
    aws_s3 as s3,
    RemovalPolicy,
    Fn,
)
from constructs import Construct

class NycTaxiE2EGlueStack(Stack):
    def __init__(self,scope:Construct,id:str,**kwargs) -> None:
        super().__init__(scope,id,**kwargs)

        # Define a new S3 bucket
        data_bucket = s3.from_bucket_name(self, "NYCTaxiE2EDataBucketNameImport", Fn.import_value("DataBucketName"))