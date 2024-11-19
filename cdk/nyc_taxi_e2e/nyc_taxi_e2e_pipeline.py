from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as actions,
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from constructs import Construct

class NycTaxiE2EPipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # S3 bucket for pipeline artifacts
        artifact_bucket = s3.Bucket(
            self, "PipelineArtifactsBucket",
            bucket_name="nyc-taxi-e2e-pipeline-artifacts",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.RETAIN,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        # Source artifact from CodeCommit or GitHub
        source_output = codepipeline.Artifact()

        # Glue scripts artifact
        glue_scripts_output = codepipeline.Artifact()

        # CDK deployment artifact
        cdk_output = codepipeline.Artifact()

        # Source Action: Pull from CodeCommit (or use GitHubActions for GitHub)
        source_action = actions.CodeCommitSourceAction(
            action_name="Source",
            repository=codecommit.Repository.from_repository_name(
                self, "CodeCommitRepo", "nyc-taxi-e2e"
            ),
            branch="main",
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
                            "aws s3 sync glue-scripts/ s3://nyc-taxi-e2e/scripts/"
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