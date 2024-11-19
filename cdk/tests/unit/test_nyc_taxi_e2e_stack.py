import aws_cdk as core
import aws_cdk.assertions as assertions

from nyc_taxi_e2e.nyc_taxi_e2e_stack import NycTaxiE2EStack

# example tests. To run these tests, uncomment this file along with the example
# resource in nyc_taxi_e2e/nyc_taxi_e2e_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = NycTaxiE2EStack(app, "nyc-taxi-e2e")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
