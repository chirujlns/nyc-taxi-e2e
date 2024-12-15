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
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define the single S3 bucket with raw and processed folders
        data_bucket = s3.Bucket.from_bucket_name(self, "DataBucket", Fn.import_value("DataBucketName"))
        script_bucket = s3.Bucket.from_bucket_name(self, "ScriptBucket", f'{Fn.import_value("DataBucketName")}/scripts/')

        
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


        # Glue Database
        glue_database = glue.CfnDatabase(
            self,
            "NycTaxiDatabase",
            catalog_id=self.account,
            database_input={"Name": "nyc_taxi_db"},
        )

        # Glue IAM Role
        glue_role = iam.Role(
            self,
            "GlueServiceRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole"),
            ],
            inline_policies={
                "GlueBucketAccess": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "s3:ListBucket",
                                "s3:GetObject",
                                "s3:DeleteObject",
                                "s3:PutObject"
                            ],
                            resources=[
                                f"{data_bucket.bucket_arn}",  # Access to the bucket
                                f"{data_bucket.bucket_arn}/raw_tripdata/*",  # Access to the raw folder
                                f"{data_bucket.bucket_arn}/scripts/*",
                                f"{data_bucket.bucket_arn}/*"
                            ],
                        ),
                        # Glue Permissions
                        iam.PolicyStatement(
                            actions=[
                                "glue:GetDatabase",
                                "glue:CreateDatabase",
                                "glue:UpdateDatabase",
                                "glue:GetTable",
                                "glue:CreateTable",
                                "glue:UpdateTable"
                            ],
                            resources=[
                                f"arn:aws:glue:{self.region}:{self.account}:catalog",
                                f"arn:aws:glue:{self.region}:{self.account}:database/nyc_taxi_db",
                                f"arn:aws:glue:{self.region}:{self.account}:table/nyc_taxi_db/*"
                            ],
                        ),
                        # CloudWatch Logs Permissions
                        iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents"
                            ],
                            resources=[
                                f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws-glue/*",
                                f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws-glue/*:log-stream/*"
                            ],
                        ),
                        # Optional: Tagging Permissions
                        iam.PolicyStatement(
                            actions=[
                                "glue:TagResource",
                                "glue:UntagResource"
                            ],
                            resources=["*"],
                        )
                    ]
                )
            },
        )

        # Glue Crawler: Crawl the raw folder and add to the Glue database
        crawler_role = iam.Role(
            self,
            "CrawlerRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            inline_policies={
                "CrawlerBucketAccess": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "s3:GetObject",
                                "s3:ListBucket",
                            ],
                            resources=[
                                f"{data_bucket.bucket_arn}",  # Access to the bucket
                                f"{data_bucket.bucket_arn}/raw_tripdata/*",  # Access to the raw folder
                                f"{data_bucket.bucket_arn}/processed_tripdata/*"
                            ],
                        ),
                        iam.PolicyStatement(
                            actions=["glue:*"],
                            resources=["*"],  # Update based on your Glue database permissions
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                                "logs:DescribeLogStreams"
                            ],
                            resources=[
                                f"arn:aws:logs:{self.region}:{self.account}:log-group:/aws-glue/crawlers:*"
                            ],
                        ),
                    ]
                )
            },
        )

        glue_crawler = glue.CfnCrawler(
            self,
            "NycTaxiCrawler",
            role=crawler_role.role_arn,
            database_name="nyc_taxi_db",
            targets={
                "s3Targets": [{"path": f"s3://{data_bucket.bucket_name}/processed_tripdata/"}]
            },
            table_prefix="raw_",
        )

        # Glue Job: Convert CSV to Parquet
        glue_job = glue.CfnJob(
            self,
            "CSVToParquetJob",
            role=glue_role.role_arn,
            command={
                "name": "glueetl",
                "scriptLocation": f"s3://{Fn.import_value('DataBucketName')}/scripts/csv_to_parquet.py",
                "pythonVersion": "3",
            },
            default_arguments={
                "--TempDir": f"s3://{data_bucket.bucket_name}/tmp/",
                "--enable-metrics": "",
                "--job-bookmark-option": "job-bookmark-enable",
            },
            glue_version="3.0",
            max_retries=2,
            timeout=30,
            number_of_workers=2,
            worker_type="G.1X",
        )