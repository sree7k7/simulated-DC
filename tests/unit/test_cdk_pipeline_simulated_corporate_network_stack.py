import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_pipeline_simulated_corporate_network.cdk_pipeline_simulated_corporate_network_stack import CdkPipelineSimulatedCorporateNetworkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_pipeline_simulated_corporate_network/cdk_pipeline_simulated_corporate_network_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkPipelineSimulatedCorporateNetworkStack(app, "cdk-pipeline-simulated-corporate-network")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
