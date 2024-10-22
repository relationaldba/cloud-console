import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from constructs import Construct

# from constructs.Construct import AwsCustomResource

project_name = "acme"
env = "demo"
region = "us-east-1"
vpc_name = f"{project_name}-{env}-vpc"
subnet_name = f"{project_name}-{env}-subnet"
sg_name = f"{project_name}-{env}-sg"
ec2_name = f"{project_name}-{env}-ec2"
keypair_name = f"{project_name}-{env}-keypair"
role_name = f"{project_name}-{env}-role"
instance_profile_name = f"{project_name}-{env}-instance-profile"
vpc_cidr = "10.24.15.0/24"
subnet_mask = 26


class Ec2Standalone(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        public_key: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self,
            vpc_name,
            ip_addresses=ec2.IpAddresses.cidr(vpc_cidr),
            max_azs=3,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"{subnet_name}",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=subnet_mask,
                ),
            ],
        )
        security_group = ec2.SecurityGroup(
            self,
            sg_name,
            vpc=vpc,
            allow_all_outbound=True,
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.SSH,
            "Allow SSH access on port 22",
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.HTTP,
            "Allow HTTP access on port 80",
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.HTTPS,
            "Allow HTTPS access on port 443",
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp_range(8000, 9999),
            "Allow all API endpoints",
        )

        key_pair = ec2.KeyPair(self, keypair_name, public_key_material=public_key)

        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "yum update -y",
            "yum install docker -y",
            "systemctl enable docker",
            "systemctl start docker",
            "usermod -aG docker ec2-user",
            "docker pull postgres:17",
            "docker pull nginx:latest",
            "docker pull traefik:latest",
            "mkdir -p /usr/local/lib/docker/cli-plugins",
            "curl -sL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m) -o /usr/local/lib/docker/cli-plugins/docker-compose",  # Download the docker compose plugin
            "test -f /usr/local/lib/docker/cli-plugins/docker-compose && chown root:root /usr/local/lib/docker/cli-plugins/docker-compose",  # Set ownership to root
            "test -f /usr/local/lib/docker/cli-plugins/docker-compose && sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose",  # Make executable
        )

        ec2_instance = ec2.Instance(
            self,
            "MyInstance",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE4_GRAVITON,
                ec2.InstanceSize.SMALL,
            ),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(
                edition=ec2.AmazonLinuxEdition.STANDARD,
                cpu_type=ec2.AmazonLinuxCpuType.ARM_64,
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            key_pair=key_pair,
            security_group=security_group,
            user_data=user_data,
        )
        cdk.CfnOutput(self, "InstanceId", value=ec2_instance.instance_id)
        cdk.CfnOutput(self, "InstancePublicIp", value=ec2_instance.instance_public_ip)
        cdk.CfnOutput(
            self, "InstancePublicDNS", value=ec2_instance.instance_public_dns_name
        )
        cdk.CfnOutput(self, "KeyName", value=key_pair.key_pair_name)
