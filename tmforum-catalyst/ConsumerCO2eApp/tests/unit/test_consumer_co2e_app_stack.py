import aws_cdk as core
import aws_cdk.assertions as assertions

from consumer_co2e_app.consumer_co2e_app_stack import ConsumerCo2EAppStack

# example tests. To run these tests, uncomment this file along with the example
# resource in consumer_co2e_app/consumer_co2e_app_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ConsumerCo2EAppStack(app, "consumer-co2e-app")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
