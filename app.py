import os
import aws_cdk as cdk
from cdk_pipeline_simulated_corporate_network.cdk_pipeline_simulated_corporate_network_stack import CdkPipelineSimulatedCorporateNetworkStack

app = cdk.App()
CdkPipelineSimulatedCorporateNetworkStack(app, "CdkPipelineSimulatedCorporateNetworkStack",
    env=cdk.Environment(account='619831221558', region='eu-central-1'),
)

app.synth()