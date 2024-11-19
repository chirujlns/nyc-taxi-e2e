from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_s3_deployment as s3_deployment,
    Duration,  # Import Duration from aws_cdk
    CfnOutput,
    RemovalPolicy,
)
from constructs import Construct

class NycTaxiE2ES3Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define a new S3 bucket
        data_bucket = s3.Bucket(
            self, "NYCTaxiE2EDataBucket",
            bucket_name="nyc-taxi-e2e",  # Custom bucket name
            versioned=True,             # Enable versioning for data protection
            encryption=s3.BucketEncryption.S3_MANAGED,  # S3-managed encryption
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,  # Block all public access
            removal_policy=RemovalPolicy.RETAIN,  # Retain bucket when stack is destroyed
            auto_delete_objects=False             # Do not delete objects automatically
        )

        # Create lifecycle rules for transitioning data to Glacier and cleanup
        data_bucket.add_lifecycle_rule(
            id="MoveToGlacier",
            prefix="processed/",  # Lifecycle for processed data
            transitions=[
                s3.Transition(
                    storage_class=s3.StorageClass.GLACIER,
                    transition_after=Duration.days(30)  # Move to Glacier after 30 days
                )
            ],
            expiration=Duration.days(365)  # Delete after 1 year
        )

        data_bucket.add_lifecycle_rule(
            id="DeleteOldRawData",
            prefix="raw/",  # Lifecycle for raw data
            expiration=Duration.days(90)  # Delete raw data after 90 days
        )

        # Create the raw and processed folders
        s3_deployment.BucketDeployment(
            self, "CreateFolders",
            sources=[s3_deployment.Source.asset("./dummy-folder")],  # Deploys empty content
            destination_bucket=data_bucket,
            destination_key_prefix="raw/"  # Creates the raw/ folder
        )
        s3_deployment.BucketDeployment(
            self, "CreateProcessedFolder",
            sources=[s3_deployment.Source.asset("./dummy-folder")],  # Deploys empty content
            destination_bucket=data_bucket,
            destination_key_prefix="processed/"  # Creates the processed/ folder
        )

        s3_deployment.BucketDeployment(
            self, "CreateScriptsFolder",
            sources=[s3_deployment.Source.asset("./dummy-folder")],  # Deploys empty content
            destination_bucket=data_bucket,
            destination_key_prefix="scripts/"  # Creates the scripts/ folder
        )

        # Define a policy statement for Glue access to the bucket
        glue_access_policy = iam.PolicyStatement(
            actions=[
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket",
                "s3:DeleteObject"
            ],
            resources=[
                data_bucket.bucket_arn,
                f"{data_bucket.bucket_arn}/*"
            ]
        )


        # Export outputs for cross-stack reference
        CfnOutput(self, "DataBucketNameExport", value=data_bucket.bucket_name, export_name="DataBucketName")