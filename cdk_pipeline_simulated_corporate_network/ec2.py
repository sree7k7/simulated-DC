from aws_cdk import Tags, aws_ec2 as ec2
from aws_cdk import aws_iam as iam
import aws_cdk.aws_ssm as ssm
import aws_cdk as cdk
from aws_cdk import aws_logs as logs
from aws_cdk import RemovalPolicy, Stack
from constructs import Construct
from aws_cdk.aws_elasticloadbalancingv2 import NetworkLoadBalancer, NetworkListener, NetworkTargetGroup, Protocol, NetworkListenerAction
from aws_cdk import (
aws_elasticloadbalancingv2 as elbv2,
)
from aws_cdk import aws_elasticloadbalancingv2_targets as elasticloadbalancingv2_targets

class EC2(Stack):        
    def __init__(self, scope: Construct, construct_id: str, vpc: object, storage: object, bucket, sg_group, config: object, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.role = iam.Role(
            self,
            "BackupRole",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore'),
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'),
                iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchAgentAdminPolicy'),
            ],
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("ec2.amazonaws.com"),
                iam.ServicePrincipal("s2svpn.amazonaws.com"),
                iam.ServicePrincipal("vpc-flow-logs.amazonaws.com")
            )
        )
        log_group = logs.LogGroup(
            self, 
            "VPCFlowLogGroup",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=cdk.RemovalPolicy.DESTROY
            )
        ec2.FlowLog(
            self, 
            "VPCFlowLog",
            resource_type=ec2.FlowLogResourceType.from_vpc(vpc),
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(log_group, self.role),
            traffic_type=ec2.FlowLogTrafficType.ALL
        )
        self.parameter = ssm.StringParameter.from_string_parameter_attributes(self, "UserString",
            parameter_name="/dnac/user/passwd"
        ).string_value
        #######################user data############
        user_data = f'''
            #!/bin/bash      
            sudo timedatectl set-timezone Europe/Copenhagen
            sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -m ec2 -a start
            sudo yum update -y            
            rm /var/lib/cloud/instance/sem/config_scripts_user
            '''
        self.instance = ec2.Instance(
            self,
            'BackupInstance',
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3_AMD, ec2.InstanceSize.MICRO),
            vpc=vpc,
            machine_image=ec2.MachineImage.latest_amazon_linux(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            ),
            security_group=sg_group,
            role=self.role,
            private_ip_address= config['server']['ENI-IP'],
            user_data=ec2.UserData.custom(user_data),
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
            block_devices=[
                ec2.BlockDevice(
                device_name="/dev/xvda",
                volume=ec2.BlockDeviceVolume.ebs(
                    volume_size= config['server']['root_volume_size'],
                    volume_type= ec2.EbsDeviceVolumeType.GP3,
                    encrypted=True
                )
            ),
                ec2.BlockDevice(
                device_name="/dev/sdg",
                volume=ec2.BlockDeviceVolume.ebs(
                    volume_size= config['server']['volume_size'],
                    volume_type= ec2.EbsDeviceVolumeType.GP3,
                    encrypted=True
                )
            )                
            ]
        )
        Tags.of(self.instance).add("shellscript", "automation")
        # self.loadbalancer = NetworkLoadBalancer(
        #     self,
        #     'BackupNetworkLoadbalancer',
        #     vpc=vpc,
        #     internet_facing=True,
        #     # vpc_subnets=subnet
        # )

        ################# Target group ####################

        # ip_target = elasticloadbalancingv2_targets.IpTarget(
        #     ip_address = config['network']['targetIpPrimary'], 
        #     port = 22, 
        #     availability_zone = self.instance.instance_availability_zone
        #     )
        # ip_targettwo = elasticloadbalancingv2_targets.IpTarget(
        #     ip_address = config['network']['targetIpSecondary'], 
        #     port = 22, 
        #     availability_zone = self.instance.instance_availability_zone
        #     )

        # self.target_group = NetworkTargetGroup(
        #     self,
        #     "TargetGroup",
        #     vpc=vpc,
        #     target_type=elbv2.TargetType.IP,
        #     targets = [ip_target, ip_targettwo],
        #     port=80
        # )     
        # self.nlb_listener = NetworkListener(
        #     self,
        #     'BackupNetworkListener',
        #     protocol=Protocol.TCP,
        #     port=22,
        #     load_balancer=self.loadbalancer,
        #     default_action= NetworkListenerAction.forward([self.target_group])
        #     # default_target_groups=[self.target_group]
        # )                    
        



            # sudo echo "{storage.s3.bucket_name} /dnac-backup fuse.s3fs _netdev,allow_other,iam_role=auto,nonempty 0 0" >> /etc/fstab
            # sudo mount -a