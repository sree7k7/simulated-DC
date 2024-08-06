import random
import this
import constructs
import aws_cdk as cdk
from aws_cdk import CfnTag, Duration, RemovalPolicy, Stack
import aws_cdk.aws_ec2 as ec2
from constructs import Construct
from aws_cdk import aws_logs as logs


class Network(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, config: object, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.vpc = ec2.Vpc(
            self,
            'BackupVPC',
            ip_addresses=ec2.IpAddresses.cidr(config['network']['Vpc_CIDR']),
            # availability_zones=[config['server']['availability_zone']],
            max_azs=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,                                   
                    cidr_mask=config['network']['cidr_mask']
                ),
                ec2.SubnetConfiguration(
                    name="private",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,                                   
                    cidr_mask=config['network']['cidr_mask']
                )
                ]
        )
        self.sg_group = ec2.SecurityGroup(
            self,
            'BackupSG',
            vpc=self.vpc,
        )
        self.sg_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(config['network']['Vpc_CIDR']),
            connection=ec2.Port(
                from_port=443,
                to_port=443,
                protocol=ec2.Protocol.TCP,
                string_representation='HTTPS'
            )
        )
        self.sg_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(config['network']['DestinationCIDR']),
            connection=ec2.Port(
                from_port=22,
                to_port=22,
                protocol=ec2.Protocol.TCP,
                string_representation='SSH'
            )
        )
        self.sg_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(config['network']['DestinationCIDR']),
            connection=ec2.Port(
                from_port=-1,
                to_port=-1,
                protocol=ec2.Protocol.ICMP,
                string_representation='ICMP'
            )
        )
        self.sg_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(config['network']['staticRoute']),
            connection=ec2.Port(
                from_port=-1,
                to_port=-1,
                protocol=ec2.Protocol.ICMP,
                string_representation='ICMP'
            )
        )
        self.sg_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(config['network']['staticRoute']),
            connection=ec2.Port(
                from_port=22,
                to_port=22,
                protocol=ec2.Protocol.TCP,
                string_representation='SSH'
            )
        ) 
        self.sg_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(config['network']['Vpc_CIDR']),
            connection=ec2.Port(
                from_port=80,
                to_port=80,
                protocol=ec2.Protocol.TCP,
                string_representation='TCP'
            )
        )
        # Across all tunnels in the account/region
        self.all_data_out = ec2.VpnConnection.metric_all_tunnel_data_out()
        self.vpn_connection = self.vpc.add_vpn_connection("Static",
                ip=config['network']['CustomerGatewayIP'],
                static_routes=[config['network']['DestinationCIDR']]
            )

        # cfn_vPNGateway = ec2.CfnVPNGateway(self, "MyCfnVPNGateway",
        #     type="ipsec.1",
            
        #     tags=[CfnTag(
        #         key="vpnkey",
        #         value="vpnvalue"
        #     )]
        # )


######### VPC endpoints ##########################
        # self.S3Gateway = ec2.GatewayVpcEndpoint(self, "S3endpoint",
        #     vpc=self.vpc,
        #     service=ec2.InterfaceVpcEndpointService("com.amazonaws.eu-central-1.s3", 443)
        # )        
        # ssmmessages = ec2.InterfaceVpcEndpoint(self, "ssmmessages",
        #     vpc=self.vpc,
        #     service=ec2.InterfaceVpcEndpointService("com.amazonaws.eu-central-1.ssmmessages", 443),
        #     security_groups=[self.sg_group],
        #     private_dns_enabled=True
        # )
        # VPCEndpointEC2 = ec2.InterfaceVpcEndpoint(self, "VPCEndpointEC2",
        #     vpc=self.vpc,
        #     security_groups=[self.sg_group],
        #     service=ec2.InterfaceVpcEndpointService("com.amazonaws.eu-central-1.ec2", 443),
        #     private_dns_enabled=True
        # )
        # VPCEndpointec2messages = ec2.InterfaceVpcEndpoint(self, "VPCEndpointec2messages",
        #     vpc=self.vpc,
        #     security_groups=[self.sg_group],
        #     service=ec2.InterfaceVpcEndpointService("com.amazonaws.eu-central-1.ec2messages", 443),
        #     private_dns_enabled=True
        # )
        # VPCEndpointssm = ec2.InterfaceVpcEndpoint(self, "VPCEndpointssm",
        #     vpc=self.vpc,
        #     security_groups=[self.sg_group],
        #     private_dns_enabled=True,
        #     service=ec2.InterfaceVpcEndpointService("com.amazonaws.eu-central-1.ssm", 443)
        # )
        # S3Interfaceendpoint = ec2.InterfaceVpcEndpoint(self, "s3interfaceendpoint",
        #     vpc=self.vpc,            
        #     service=ec2.InterfaceVpcEndpointService("com.amazonaws.eu-central-1.s3", 443)
        #             )


  