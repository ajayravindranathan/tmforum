from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2, 
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr as repository,
    aws_iam as iam,
)
from constructs import Construct

class ConsumerCo2EAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "ConsumerCo2EAppQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
        #vpc = ec2.Vpc(self, "snowflake-vpc", max_azs=3)     # default is all AZs in region
        vpc = ec2.Vpc.from_lookup(self, 'default-VPC', vpc_name="default-VPC")

        cluster = ecs.Cluster(self, "ConsumerCO2eCluster", vpc=vpc)

        #Create a Fargate container image
        ecr_repository = repository.Repository.from_repository_name(self,
                id              = "ECR",
                repository_name = "tmfdtw"
            )
        #image = ecs.ContainerImage.from_ecr_repository(ecr_repository)

        ecs_task_definition = ecs.FargateTaskDefinition(
            self,
            'ECS-Task-Definition',
            cpu=512,
            memory_limit_mib=1024,
            task_role=iam.Role(
                self,
                'ECS-Task-Role',
                assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
                managed_policies=[
                    #**********************************************************************
                    # Add managed policies here to give AWS permissions to your Fargate Task
                    #**********************************************************************
                    #iam.ManagedPolicy.from_aws_managed_policy_name(
                    #    'AmazonElasticFileSystemClientReadOnlyAccess')
                    iam.ManagedPolicy.from_aws_managed_policy_name('AdministratorAccess'),
                ]
            ),
            execution_role=iam.Role(
                self,
                'ECS-Task-Execution-Role',
                assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
                managed_policies=[
                    #iam.ManagedPolicy.from_aws_managed_policy_name(
                        #'service-role/AmazonECSTaskExecutionRolePolicy'),
                    iam.ManagedPolicy.from_aws_managed_policy_name('AdministratorAccess'),
                ]
            )
        )

        ecs_container_definition = ecs.ContainerDefinition(
            self,
            id='Carbon-Footprint-Analyzer-Container',
            task_definition=ecs_task_definition,
            image=ecs.ContainerImage.from_ecr_repository(ecr_repository),
            essential=True,
            # Expose port 80 on the container
            port_mappings=[ecs.PortMapping(
                container_port=8501,
                host_port=8501,
                protocol=ecs.Protocol.TCP
            )],
        )
        # Create security group
        ecs_svc_security_group = ec2.SecurityGroup(
            self, 
            "GlobalAccessSecGroup",
            vpc = vpc,
            description='LoadBalancer Security Group',
            security_group_name='LoadBalancer-SecurityGroup'
        )

        # Add inbound rule to allow traffic from anywhere
        ecs_svc_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.all_traffic(),
            description='Allow from anyone on any port'
        )
        ecs_patterns.ApplicationLoadBalancedFargateService(self, "ConsumerCO2eService",
            cluster=cluster,            # Required
            cpu=512,                    # Default is 256
            desired_count=1,            # Default is 1
            task_definition=ecs_task_definition,
            #task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                #image=image),
            # task_subnets=ec2.SubnetSelection(
            # subnets=[ec2.Subnet.from_subnet_id(self, "subnet", "subnet-01ab9a99e055f1837")]
            # ),
            memory_limit_mib=2048,      # Default is 512
            public_load_balancer=True,  # Default is True
            assign_public_ip = True,
            security_groups = [ecs_svc_security_group])  