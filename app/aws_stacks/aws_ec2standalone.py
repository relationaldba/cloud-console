import base64
import configparser
import io
import json
from datetime import datetime

import inflection
import paramiko
from aws_cdk import App, CfnOutput, Environment, SecretValue, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_secretsmanager as secretsmanager
from boto3 import client
from constructs import Construct
from fabric import Connection
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.aws_stacks.config import (
    AWS_AVAILABILITY_ZONES,
    NGINX_CONFIG,
    SMILE_CDR_DEFAULT_PROPERTIES,
    SMILECDR_COMPOSE_YAML,
)


class AWSEc2Standalone(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        public_key: str,
        private_key_base64: str,
        env: Environment,
        vpc_cidr: str,
        instance_class: ec2.InstanceClass | None,
        instance_size: ec2.InstanceSize | None,
        disk_size: int | None,
        subnet_mask: int = 26,
        hosted_zone_domain: str = "cloud.relationaldba.com",
        user_data: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, env=env, **kwargs)
        # vpc_name = f"{construct_id}-vpc"
        # subnet_name = f"{construct_id}-subnet"
        # sg_name = f"{construct_id}-sg"
        # ec2_name = f"{construct_id}-ec2"
        # keypair_name = f"{construct_id}-keypair"
        # hosted_zone_name = f"{construct_id}-hosted-zone"
        hosted_zone_name = "cloud.relationaldba.com"
        # route53_arecord_name = f"{construct_id}-arecord"

        if not instance_class:
            instance_class = ec2.InstanceClass.BURSTABLE4_GRAVITON

        if not instance_size:
            instance_size = ec2.InstanceSize.LARGE

        if not disk_size:
            disk_size = 10

        vpc = ec2.Vpc(
            self,
            id=f"{construct_id}-vpc",
            ip_addresses=ec2.IpAddresses.cidr(vpc_cidr),
            # max_azs=3,
            availability_zones=AWS_AVAILABILITY_ZONES.get(env.region or "us-east-2"),
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"{construct_id}-subnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=subnet_mask,
                ),
            ],
        )
        security_group = ec2.SecurityGroup(
            self,
            id=f"{construct_id}-sg",
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

        key_pair = ec2.KeyPair(
            self, id=f"{construct_id}-keypair", public_key_material=public_key
        )

        ec2_instance = ec2.Instance(
            self,
            id=f"{construct_id}-ec2",
            instance_type=ec2.InstanceType.of(instance_class, instance_size),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(
                edition=ec2.AmazonLinuxEdition.STANDARD,
                cpu_type=ec2.AmazonLinuxCpuType.ARM_64,
            ),
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(
                        volume_size=disk_size,
                        delete_on_termination=True,
                        encrypted=True,
                        volume_type=ec2.EbsDeviceVolumeType.GP3,
                    ),
                )
            ],
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            key_pair=key_pair,
            security_group=security_group,
            # user_data=user_data,
        )

        hosted_zone = route53.HostedZone.from_hosted_zone_attributes(
            self,
            hosted_zone_name,
            hosted_zone_id="Z08786672SMI6WB30FCK7",  # Replace with your hosted zone ID
            zone_name=hosted_zone_name,  # Replace with your domain name
        )

        # Route 53 A Record pointing to EC2 instance
        route53_arecord = route53.ARecord(
            self,
            id=f"{construct_id}-arecord",
            record_name=construct_id,
            zone=hosted_zone,
            target=route53.RecordTarget.from_ip_addresses(
                ec2_instance.instance_public_ip
            ),
        )

        secretsmanager.Secret(
            self,
            id=f"{construct_id}-private-key",
            secret_string_value=SecretValue.unsafe_plain_text(private_key_base64),
            description="Private SSH key for accessing EC2 instances",
        )

        # Output the stack details
        CfnOutput(
            self,
            id="StackArn",
            value=ec2_instance.stack.stack_id,
        )
        # CfnOutput(
        #     self,
        #     id="StackName",
        #     value=ec2_instance.stack.stack_name,
        # )

        # Output the EC2 instance details
        CfnOutput(
            self,
            id="ec2InstanceId",
            value=ec2_instance.instance_id,
        )
        CfnOutput(
            self,
            id="ec2InstancePublicIp",
            value=ec2_instance.instance_public_ip,
        )
        CfnOutput(
            self,
            id="ec2InstancePublicDns",
            value=ec2_instance.instance_public_dns_name,
        )
        # CfnOutput(
        #     self,
        #     id="ec2InstancePrivateIp",
        #     value=ec2_instance.instance_private_ip,
        # )
        # CfnOutput(
        #     self,
        #     id="ec2InstancePrivateDns",
        #     value=ec2_instance.instance_private_dns_name,
        # )
        # CfnOutput(
        #     self,
        #     id="ec2InstanceOsType",
        #     value=ec2_instance.os_type.name,
        # )
        CfnOutput(
            self,
            id="ec2InstanceAvailabilityZone",
            value=ec2_instance.instance_availability_zone,
        )

        # Output the key pair details
        # CfnOutput(
        #     self,
        #     id="ec2KeyPairName",
        #     value=key_pair.key_pair_name,
        # )

        # Route53 A Record
        CfnOutput(
            self,
            id="route53ARecordDomainName",
            value=route53_arecord.domain_name,
        )


def generate_key_pair(bits: int = 2048) -> dict[str, str]:
    key = paramiko.RSAKey.generate(bits)
    keyout = io.StringIO()
    key.write_private_key(keyout)
    private_key = keyout.getvalue()
    private_key_base64 = base64.b64encode(private_key.encode("utf-8")).decode("utf-8")
    public_key = f"{key.get_name()} {key.get_base64()} Generated-by-CF"
    return {
        "private_key": private_key,
        "private_key_base64": private_key_base64,
        "public_key": public_key,
    }


def synth_cfn_template(
    deployment_name: str,
    public_key: str,
    private_key_base64: str,
    aws_account_id: str,
    aws_region: str,
    vpc_cidr: str,
    instance_class: ec2.InstanceClass | None,
    instance_size: ec2.InstanceSize | None,
    disk_size: int | None,
) -> str:
    app = App()
    stack = AWSEc2Standalone(
        scope=app,
        construct_id=deployment_name,
        public_key=public_key,
        private_key_base64=private_key_base64,
        env=Environment(account=aws_account_id, region=aws_region),
        vpc_cidr=vpc_cidr,
        subnet_mask=26,
        instance_class=instance_class,
        instance_size=instance_size,
        disk_size=disk_size,
    )

    # Synthesize the stack
    cloud_assembly = app.synth()

    # Get the CloudFormation template
    template = cloud_assembly.get_stack_artifact(stack.artifact_id).template

    template_body = json.dumps(template)

    return template_body


def deploy_stack(
    deployment_name: str,
    template_body: str,
    aws_region: str,
    aws_access_key_id: str,
    aws_secret_access_key: str,
):
    cfn_client = client(
        "cloudformation",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region,
    )

    # Check if stack exists
    try:
        cfn_client.describe_stacks(
            StackName=deployment_name,
        )
        stack_exists = True
    except cfn_client.exceptions.ClientError:
        stack_exists = False

    if stack_exists:
        # If stack exists, update existing stack
        try:
            cfn_client.update_stack(
                StackName=deployment_name,
                TemplateBody=template_body,
                Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
            )
            print(f"{deployment_name} - Updating stack")
            waiter = cfn_client.get_waiter("stack_update_complete")
            waiter.wait(StackName=deployment_name)
            print(f"{deployment_name} - Successfully updated stack")

        except cfn_client.exceptions.ClientError as e:
            if "No updates are to be performed" in str(e):
                print(f"{deployment_name} - No updates were needed")
                return
            else:
                print(f"{deployment_name} - Update error: {str(e)}")
                raise e

    else:
        # If stack doesn't exist, create new stack
        try:
            cfn_client.create_stack(
                StackName=deployment_name,
                TemplateBody=template_body,
                Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
            )
            print(f"{deployment_name} - Creating stack")
            waiter = cfn_client.get_waiter("stack_create_complete")
            waiter.wait(StackName=deployment_name)
            print(f"{deployment_name} - Successfully Created stack")

        except cfn_client.exceptions.ClientError as e:
            print(f"{deployment_name} - Create error: {str(e)}")
            # Get and print the stack events for more information
            events = cfn_client.describe_stack_events(StackName=deployment_name)[
                "StackEvents"
            ]
            for event in events[:50]:  # Print the 10 most recent events
                print(
                    f"Event: {event['LogicalResourceId']} - {event['ResourceStatus']} - {event.get('ResourceStatusReason', 'No reason provided')}"
                )
            raise e

    # Get stack outputs and return them
    stack_info = cfn_client.describe_stacks(StackName=deployment_name)
    outputs = stack_info["Stacks"][0].get("Outputs", [])
    for output in outputs:
        print(f"{output['OutputKey']}: {output['OutputValue']}")

    return outputs


def install_docker(conn: Connection):
    commands = [
        "sudo yum update -y",
        "sudo yum install docker -y",
        "sudo usermod -aG docker ec2-user",
        "sudo systemctl enable docker",
        "sudo systemctl start docker",
        "sudo docker pull postgres:17",
        "sudo docker pull nginx:latest",
        "sudo mkdir -p /usr/local/lib/docker/cli-plugins",
        "sudo curl -sL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m) -o /usr/local/lib/docker/cli-plugins/docker-compose",  # Download the docker compose plugin
        "sudo test -f /usr/local/lib/docker/cli-plugins/docker-compose && sudo chown root:root /usr/local/lib/docker/cli-plugins/docker-compose",  # Set ownership to root
        "sudo test -f /usr/local/lib/docker/cli-plugins/docker-compose && sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose",  # Make executable
        "sudo ln -s /usr/local/lib/docker/cli-plugins/docker-compose /usr/local/bin/docker-compose",
    ]

    for command in commands:
        conn.run(command)

    return True


def install_certbot(conn: Connection, domain: str, email: str):
    commands = [
        "mkdir -p /home/ec2-user/certs",
        "sudo docker pull certbot/certbot",
        f"sudo docker run --rm -it -p 80:80 -v /home/ec2-user/certs:/etc/letsencrypt certbot/certbot certonly --standalone -d {domain} --non-interactive --agree-tos --email {email}",
        "sudo chmod -R 755 /home/ec2-user/certs",
    ]

    for command in commands:
        conn.run(command)

    return True


def install_smilecdr(
    conn: Connection,
    smilecdr_version: str,
    smilecdr_domain: str,
    smilecdr_properties_base64: str | None,
    docker_username: str | None = None,
    docker_password: str | None = None,
):
    # Read default properties file
    smile_cfg = configparser.ConfigParser(allow_unnamed_section=True)
    smile_cfg.optionxform = str # type: ignore
    smile_cfg.read_string(SMILE_CDR_DEFAULT_PROPERTIES)

    if smilecdr_properties_base64:
        # Read user-supplied properties file
        smilecdr_properties = base64.b64decode(smilecdr_properties_base64)
        smilecdr_properties = smilecdr_properties.decode("utf-8")
        user_cfg = configparser.ConfigParser(allow_unnamed_section=True)
        user_cfg.optionxform = str # type: ignore
        user_cfg.read_string(smilecdr_properties)

        # Overwrite default values with user supplied values
        for key, value in user_cfg.items(configparser.UNNAMED_SECTION):  # type: ignore
            smile_cfg.set(configparser.UNNAMED_SECTION, key, value) # type: ignore
    

    if docker_username and docker_password:
        conn.run(
            f"docker login -u {docker_username} -p {docker_password} docker.smilecdr.com"
        )
    compose_yaml_file = SMILECDR_COMPOSE_YAML.replace(
        "SMILECDR_VERSION", smilecdr_version
    ).replace("SMILECDR_DOMAIN", smilecdr_domain)
    conn.put(io.StringIO(compose_yaml_file), "compose.yaml")

    # Upload the properties file read by the configparser smile_cfg
    properties_string = io.StringIO()
    smile_cfg.write(properties_string)
    conn.put(properties_string, "cdr-config-Master.properties")
    nginx_config_file = NGINX_CONFIG.replace("SMILECDR_DOMAIN", smilecdr_domain)
    conn.put(io.StringIO(nginx_config_file), "nginx.conf")

    conn.run("docker compose down")
    conn.run("docker compose up certbot")
    conn.run("docker compose up -d")
    conn.run("sleep 60")  # Allow time for Smile CDR to start

    return True


def destroy_stack(
    deployment_id: int,
    deployment_name: str,
    db: Session,
):
    deployment = db.scalar(
        select(models.Deployment).where(models.Deployment.id == deployment_id)
    )
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "DEPLOYMENT_NOT_FOUND",
                "module": "deployments",
                "message": "The requested deployment(s) could not be found, or you do not have permission to access them.",
            },
        )

    # Get the environment details
    environment = db.scalar(
        select(models.Environment).where(
            models.Environment.id == deployment.environment_id
        )
    )
    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "ENVIRONMENT_NOT_FOUND",
                "module": "deployments",
                "message": "The requested environment(s) could not be found, or you do not have permission to access them.",
            },
        )

    aws_region = environment.aws_region
    aws_access_key_id = environment.aws_access_key_id
    aws_secret_access_key = environment.aws_secret_access_key

    cfn_client = client(
        "cloudformation",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region,
    )

    try:
        # Delete the stack
        cfn_client.delete_stack(StackName=deployment_name)
        print(f"{deployment_name} - Deleting stack")
        waiter = cfn_client.get_waiter("stack_delete_complete")
        waiter.wait(StackName=deployment_name)
        print(f"{deployment_name} - Stack deleted successfully")

        deployment.status = models.DeploymentStatusEnum.DELETED
        deployment.deleted_at = datetime.now()
        db.commit()

    except cfn_client.exceptions.ClientError as e:
        print(f"{deployment_name} - Delete error: {str(e)}")
        deployment.status = models.DeploymentStatusEnum.ERROR
        db.commit()
        raise e


def synth_and_deploy(
    deployment_id: int,
    deployment_name: str,
    vpc_cidr: str,
    db: Session,
):
    deployment = db.scalar(
        select(models.Deployment).where(models.Deployment.id == deployment_id)
    )
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "DEPLOYMENT_NOT_FOUND",
                "module": "deployments",
                "message": "The requested deployment(s) could not be found, or you do not have permission to access them.",
            },
        )

    deployment.status = models.DeploymentStatusEnum.SYNTHESIZING
    db.commit()

    # Get the environment details
    environment = db.scalar(
        select(models.Environment).where(
            models.Environment.id == deployment.environment_id
        )
    )
    if not environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "ENVIRONMENT_NOT_FOUND",
                "module": "deployments",
                "message": "The requested environment(s) could not be found, or you do not have permission to access them.",
            },
        )

    stack_properties = db.scalars(
        select(models.StackProperty).where(
            models.StackProperty.deployment_id == deployment_id
        )
    )

    product_properties = db.scalars(
        select(models.ProductProperty).where(
            models.ProductProperty.deployment_id == deployment_id
        )
    )

    instance_class = None
    instance_size = None
    disk_size = None

    for stack_property in stack_properties:
        if stack_property.name == "instance_class":
            instance_class = ec2.InstanceClass[stack_property.value]
        elif stack_property.name == "instance_size":
            instance_size = ec2.InstanceSize[stack_property.value]
        elif stack_property.name == "disk_size":
            disk_size = stack_property.value


    properties_base64 = None

    for product_property in product_properties:
        if product_property.name == "properties_base64":
            properties_base64 = product_property.value

    print(f"{deployment_name} - Properties base64: {properties_base64}")

    

    aws_account_id = environment.aws_account_id
    aws_region = environment.aws_region
    aws_access_key_id = environment.aws_access_key_id
    aws_secret_access_key = environment.aws_secret_access_key

    # Generate an SSH keypair
    keypair = generate_key_pair()
    public_key = keypair["public_key"]
    private_key_base64 = keypair["private_key_base64"]
    private_key_str = keypair["private_key"]
    private_key = paramiko.RSAKey.from_private_key(io.StringIO(private_key_str))

    # Synthesize the stack
    cfn_template = synth_cfn_template(
        deployment_name=deployment_name,
        public_key=public_key,
        private_key_base64=private_key_base64,
        aws_account_id=aws_account_id,
        aws_region=aws_region,
        vpc_cidr=vpc_cidr,
        instance_class=instance_class,
        instance_size=instance_size,
        disk_size=int(disk_size) if disk_size else None,
    )

    deployment.status = models.DeploymentStatusEnum.CREATING
    db.commit()

    # Deploy the stack
    response = deploy_stack(
        deployment_name=deployment_name,
        template_body=cfn_template,
        aws_region=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    if not response:
        deployment.status = "FAILED"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "INTERNAL_SERVER_ERROR",
                "module": "deployments",
                "message": "An internal server error occurred. We could not deploy the stack. Please try again later.",
            },
        )

    stack_output = []
    for dict in response:
        stack_output.append(
            models.StackProperty(
                name=inflection.underscore(dict.get("OutputKey")),
                value=dict.get("OutputValue"),
                stack_id=deployment.stack_id,
                deployment_id=deployment_id,
            )
        )
        # Get the public IP address of the EC2 instance
        if dict.get("OutputKey") == "ec2InstancePublicIp":
            host_public_ip = dict.get("OutputValue")

    db.bulk_save_objects(stack_output)
    db.commit()

    # Install docker
    deployment.status = models.DeploymentStatusEnum.INSTALLING
    db.commit()

    with Connection(
        host=host_public_ip,
        user="ec2-user",
        port=22,
        connect_kwargs={
            "pkey": private_key,
        },
    ) as conn:
        install_docker(conn=conn)

    # Install certbot
    # deployment.status = "INSTALLING CERTBOT"
    # db.commit()

    # with Connection(
    #     host=host_public_ip,
    #     user="ec2-user",
    #     port=22,
    #     connect_kwargs={
    #         "pkey": private_key,
    #     },
    # ) as conn:
    #     install_certbot(
    #         conn=conn,
    #         domain=f"{deployment_name.lower()}.cloud.relationaldba.com",
    #         email="email@acme.com",
    #     )

    # Get the product details
    product = db.scalar(
        select(models.Product).where(models.Product.id == deployment.product_id)
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": "PRODUCT_NOT_FOUND",
                "module": "deployments",
                "message": "The requested product(s) could not be found, or you do not have permission to access them.",
            },
        )

    docker_username = product.repository_username or None
    docker_password = product.repository_password or None
    smilecdr_version = product.version

    with Connection(
        host=host_public_ip,
        user="ec2-user",
        port=22,
        connect_kwargs={
            "pkey": private_key,
        },
    ) as conn:
        install_smilecdr(
            conn=conn,
            docker_username=docker_username,
            docker_password=docker_password,
            smilecdr_version=smilecdr_version,
            smilecdr_properties_base64=properties_base64,
            smilecdr_domain=f"{deployment_name.lower()}.cloud.relationaldba.com",
        )

    deployment.status = models.DeploymentStatusEnum.ONLINE
    db.commit()

    return True
