from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2, 
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr as repository,
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
                repository_name = "tmfdtw:consumerco2emission"
            )
        image = ecs.ContainerImage.from_ecr_repository(ecr_repository)

        ecs_patterns.ApplicationLoadBalancedFargateService(self, "ConsumerCO2eService",
            cluster=cluster,            # Required
            cpu=512,                    # Default is 256
            desired_count=1,            # Default is 1
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image),
            # task_subnets=ec2.SubnetSelection(
            # subnets=[ec2.Subnet.from_subnet_id(self, "subnet", "subnet-01ab9a99e055f1837")]
            # ),
            memory_limit_mib=2048,      # Default is 512
            public_load_balancer=True)  # Default is True