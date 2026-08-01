import aws_cdk as cdk                                                                                                               
from cdk_pipeline_simulated_corporate_network.network import Network                                                                
from cdk_pipeline_simulated_corporate_network.ec2 import EC2                                                                        
                                                                
app = cdk.App()


test_config = {                                                                                                                     
        'AWS_Account': '267083758392',                                                                                                  
        'network': {                                                                                                                    
            'Vpc_CIDR': '10.4.0.0/24',                                                                                                  
            'cidr_mask': 26,                                                                                                            
            'CustomerGatewayIP': '83.221.156.77',                                                                                       
            'DestinationCIDR': '192.168.31.101/32',                                                                                     
            'staticRoute': '192.168.31.101/32',                                                                                         
        },                                                                                                                              
        'server': {                                                                                                                     
            'root_volume_size': 10,                                                                                                     
            'volume_size': 10,                                                                                                          
            'ENI-IP': '10.4.0.140',                                                                                                     
        },                                                                                                                              
    }                                                                                                                                   
                                                                                                                                        
    # Define your target AWS environment                                                                                                
target_env = cdk.Environment(account=test_config['AWS_Account'], region='us-east-1')                                                
                                                                                                                                        
    # 2. Instantiate the Network Stack directly                                                                                         
network_stack = Network(                                                                                                            
        app,                                                                                                                            
        'SimulatedNetworkStack',                                                                                                        
        config=test_config,                                                                                                             
        env=target_env                                                                                                                  
    )                                                                                                                                   
                                                                                                                                        
    # 3. Instantiate the EC2 Stack and pass the necessary network variables                                                             
ec2_stack = EC2(                                                                                                                    
        app,                                                                                                                            
        "SimulatedEC2Stack",                                                                                                            
        vpc=network_stack.vpc,                                                                                                          
        config=test_config,                                                                                                             
        sg_group=network_stack.sg_group,                                                                                                
        env=target_env                                                                                                                  
    )                                                                                                                                   
                                                                                                                                        
app.synth()  
