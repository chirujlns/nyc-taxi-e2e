from aws_cdk import (
    Stack,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    Duration,
    Fn
)
from constructs import Construct


class NycTaxiE2EStepFunctionStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        
         # Import DataBrew Job Names from Outputs
        profiling_job_name = Fn.import_value("TripDataProfilingJobName")
        cleaning_job_name = Fn.import_value("TripDataCleaningJobName")

        # Profiling Job Task
        profiling_task = tasks.CallAwsService(
            self, "DataBrewProfilingTask",
            service="databrew",
            action="startJobRun",
            parameters={"Name": profiling_job_name},
            iam_resources=["*"],
            result_path="$.profilingResult"
        )

        # Cleaning Job Task
        cleaning_task = tasks.CallAwsService(
            self, "DataBrewCleaningTask",
            service="databrew",
            action="startJobRun",
            parameters={"Name": cleaning_job_name},
            iam_resources=["*"],
            result_path="$.cleaningResult"
        )

        # Success State
        success_state = sfn.Succeed(
            self, "Success",
            comment="DataBrew tasks completed successfully"
        )

        # Define the Step Function workflow
        definition = profiling_task.next(cleaning_task).next(success_state)

        # State Machine
        state_machine = sfn.StateMachine(
            self, "NycTaxiE2EStateMachine",
            definition=definition,
            timeout=Duration.minutes(30)
        )