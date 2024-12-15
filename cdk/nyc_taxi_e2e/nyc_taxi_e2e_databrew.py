from aws_cdk import (
    Stack,
    aws_databrew as databrew,
    aws_iam as iam,
    aws_s3 as s3,
    Fn
)
from constructs import Construct

class NycTaxiE2EDataBrewStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Import the S3 bucket name from another stack
        bucket_name = Fn.import_value("DataBucketName")
        print(bucket_name)
        
        # Reference the existing bucket by name
        bucket = s3.Bucket.from_bucket_name(self, "ImportedDataBucket", bucket_name)

        # IAM Role for DataBrew
        databrew_role = iam.Role(
            self, "DataBrewRole",
            assumed_by=iam.ServicePrincipal("databrew.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSGlueServiceRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
            ]
        )

        # DataBrew Dataset
        raw_trip_data_dataset = databrew.CfnDataset(
            self, "RawTripDataDataset",
            input=databrew.CfnDataset.InputProperty(
                s3_input_definition=databrew.CfnDataset.S3LocationProperty(
                    bucket=bucket_name,
                    key="raw_tripdata/"
                )
            ),
            name="RawTripDataDataset"
        )

        # DataBrew Recipe
        trip_data_cleaning_recipe = databrew.CfnRecipe(
            self, "TripDataCleaningRecipe",
            name="TripDataCleaningRecipe",
            steps=[
                databrew.CfnRecipe.RecipeStepProperty(
                    action=databrew.CfnRecipe.ActionProperty(
                        operation="YEAR",
                        parameters={
                            "sourceColumn": "tpep_pickup_datetime",
                            "targetColumn": "year"
                        }
                    )
                ),
                databrew.CfnRecipe.RecipeStepProperty(
                    action=databrew.CfnRecipe.ActionProperty(
                        operation="MONTH",
                        parameters={
                            "sourceColumn": "tpep_pickup_datetime",
                            "targetColumn": "month"
                        }
                    )
                ),
                databrew.CfnRecipe.RecipeStepProperty(
                    action=databrew.CfnRecipe.ActionProperty(
                        operation="REMOVE_VALUES",
                        parameters={
                            "sourceColumn": "year"
                        }
                    ),
                    condition_expressions=[
                        databrew.CfnRecipe.ConditionExpressionProperty(
                            condition="IS_NOT",
                            value="[\"2019\"]",
                            target_column="year"
                        )
                    ]
                ),
                databrew.CfnRecipe.RecipeStepProperty(
                    action=databrew.CfnRecipe.ActionProperty(
                        operation="REMOVE_VALUES",
                        parameters={
                            "sourceColumn": "month"
                        }
                    ),
                    condition_expressions=[
                        databrew.CfnRecipe.ConditionExpressionProperty(
                            condition="IS_NOT",
                            value="[\"1\"]",
                            target_column="month"
                        )
                    ]
                ),
                
            ]
        )

        # DataBrew Cleaning Job
        databrew.CfnJob(
            self, "TripDataCleaningJob",
            name="TripDataCleaningJob",
            role_arn=databrew_role.role_arn,
            type="RECIPE",
            dataset_name=raw_trip_data_dataset.name,
            recipe=databrew.CfnJob.RecipeProperty(
                name=trip_data_cleaning_recipe.name,
                version="1.0"
            ),
            outputs=[databrew.CfnJob.OutputProperty(
                location=databrew.CfnJob.S3LocationProperty(
                    bucket=bucket_name,
                    key="databrew-output/cleaning/"
                ),
                format="CSV"
            )]
        )

       