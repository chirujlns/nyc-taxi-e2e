from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as actions,
    aws_codebuild as codebuild,
    aws_iam as iam,
    RemovalPolicy,
)
from constructs import Construct

class NycTaxiE2EPipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # S3 bucket for pipeline artifacts
        # artifact_bucket = s3.Bucket(
        #     self, "PipelineArtifactsBucket",
        #     bucket_name="nyc-taxi-e2e-pipeline-artifacts",
        #     versioned=True,
        #     encryption=s3.BucketEncryption.S3_MANAGED,
        #     removal_policy=RemovalPolicy.RETAIN,
        # )
                # S3 bucket for pipeline artifacts
        artifact_bucket = s3.Bucket.from_bucket_name(
            self, "PipelineArtifactsBucket", "nyc-taxi-e2e-pipeline-artifacts"
        )

        # Source artifact from CodeStar Connections
        source_output = codepipeline.Artifact()

        # Glue scripts artifact
        glue_scripts_output = codepipeline.Artifact()

        # CDK deployment artifact
        cdk_output = codepipeline.Artifact()

        # Create an IAM role for CodePipeline
        pipeline_role = iam.Role(
            self, "PipelineRole",
            assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodePipeline_FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeBuildAdminAccess"),
            ]
        )

        # Source Action: Pull from GitHub via CodeStar Connection
        source_action = actions.CodeStarConnectionsSourceAction(
            action_name="GitHubSource",
            connection_arn="arn:aws:codeconnections:us-east-1:116981765406:connection/60429ec3-2e5f-4220-abd2-ca1f2a6b63fe",
            owner="chirujlns",           # GitHub username
            repo="nyc-taxi-e2e",         # Repository name
            branch="main",               # Branch to track
            output=source_output,
        )

        # Build project: Upload Glue scripts to S3
        glue_build_project = codebuild.PipelineProject(
            self, "GlueScriptsBuild",
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {"python": "3.x"},
                    },
                    "build": {
                        "commands": [
                            "aws s3 sync glue_scripts/ s3://nyc-taxi-e2e/scripts/"
                        ]
                    }
                },
                "artifacts": {"files": ["**/*"]},
            }),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
            )
        )

        # Build project: CDK Deployment
        cdk_build_project = codebuild.PipelineProject(
            self, "CDKBuild",
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {"nodejs": "14"},
                        "commands": [
                            "npm install -g aws-cdk",
                            "pip install -r requirements.txt"
                        ]
                    },
                    "build": {
                        "commands": [
                            "cdk synth",
                            "cdk deploy --require-approval never"
                        ]
                    }
                },
                "artifacts": {"files": ["**/*"]},
            }),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
            )
        )

        # Define the CodePipeline
        pipeline = codepipeline.Pipeline(
            self, "NycTaxiE2EPipeline",
            pipeline_name="NycTaxiE2EPipeline",
            artifact_bucket=artifact_bucket,
            role=pipeline_role,  # Attach the IAM role to the pipeline
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[source_action],
                ),
                codepipeline.StageProps(
                    stage_name="UploadGlueScripts",
                    actions=[
                        actions.CodeBuildAction(
                            action_name="UploadGlueScripts",
                            project=glue_build_project,
                            input=source_output,
                            outputs=[glue_scripts_output],
                        )
                    ],
                ),
                codepipeline.StageProps(
                    stage_name="DeployCDK",
                    actions=[
                        actions.CodeBuildAction(
                            action_name="DeployCDK",
                            project=cdk_build_project,
                            input=glue_scripts_output,
                            outputs=[cdk_output],
                        )
                    ],
                ),
            ],
        )