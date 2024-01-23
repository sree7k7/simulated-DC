import aws_cdk as cdk
from aws_cdk import Stack  # Duration,; aws_sqs as sqs,
from aws_cdk import aws_codecommit as codecommit
import aws_cdk.aws_ec2 as ec2
from aws_cdk.pipelines import ManualApprovalStep
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from constructs import Construct
from cdk_pipeline_simulated_corporate_network.stage import Stage

class CdkPipelineSimulatedCorporateNetworkStack(Stack):


    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.backend_repository =  codecommit.Repository.from_repository_name(
            self,
            "Simulated-network",
            repository_name="simulated-network" 
        )
        pipeline = CodePipeline(
            self,
            "simulated-network",
            pipeline_name=self.backend_repository.repository_name,
            cross_account_keys=True,
            self_mutation=True,
            synth=ShellStep("Synth",
                            input=CodePipelineSource.code_commit(
                                repository=self.backend_repository, branch="main"),
                            commands=[
                                "npm install -g aws-cdk",
                                "python -m pip install -r requirements.txt",
                                "cdk synth",
                            ]
                            )        
        )    
        
        ######aws ######        
        test_config= {
            'AWS_Account':'619831221558',               # account
            'network': {                                
                'Vpc_CIDR': '10.4.0.0/24',              # vpc cidr
                'cidr_mask': 26,                        # subnet mask
                'CustomerGatewayIP': '83.221.156.77',   # CGW device public ip
                'DestinationCIDR': '192.168.31.101/32', # vpn
                'staticRoute': '192.168.31.101/32',     # vpn (private ip/32 of cgw (you receive from onprem/customer))
            },   
            'server': {
                'root_volume_size': 10,
                'volume_size': 10,                      #EBS
                'ENI-IP': '10.4.0.140',
                # 'availability_zone': 'eu-central-1b'
            },
        }        
        test_stage = pipeline.add_stage(Stage(
            self,
            "test-env", #change
            config = test_config,
            env=cdk.Environment(account=test_config['AWS_Account'], region="eu-central-1")
            )
        )
        # test_stage.add_pre(ManualApprovalStep('approval'))