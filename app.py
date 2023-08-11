import os.path

from aws_cdk.aws_s3_assets import Asset

from constructs import Construct

from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ssm as ssm,
    App,
    Stack,
    CfnOutput,
)

from dotenv import load_dotenv

load_dotenv()

SSH_PUBLIC_KEY = os.getenv("SSH_PUBLIC_KEY")

dirname = os.path.dirname(__file__)

name = "jammy"


class EC2InstanceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC
        vpc = ec2.Vpc(
            self,
            "VPC",
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public", subnet_type=ec2.SubnetType.PUBLIC
                )
            ],
        )

        # Instance Role and SSM Managed Policy
        role = iam.Role(
            self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
        )

        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"
            )
        )

        # Security group for ec2 instance
        sg = ec2.SecurityGroup(
            self,
            f"SG_{name}",
            vpc=vpc,
            allow_all_outbound=True,
            description=f"Security group for {name} instance",
        )

        # Allow Inbound SSH and Anvil
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(8545))
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22))

        # Ubuntu AMI
        # https://discourse.ubuntu.com/t/finding-ubuntu-images-with-the-aws-ssm-parameter-store/15507
        ubuntu_ami = ec2.MachineImage.from_ssm_parameter(
            "/aws/service/canonical/ubuntu/server/jammy/stable/current/amd64/hvm/ebs-gp2/ami-id"
        )

        # create new keypair
        key_name = f"{name}-ssh-key"
        key = ec2.CfnKeyPair(
            self,
            "KeyPair",
            key_name=key_name,
            public_key_material=SSH_PUBLIC_KEY,
        )

        # Ubuntu Jammy Instance
        ec2_instance = ec2.Instance(
            self,
            f"{name}_ec2",
            instance_type=ec2.InstanceType("t2.large"),
            machine_image=ubuntu_ami,
            vpc=vpc,
            role=role,
            security_group=sg,
            instance_name=f"{name}",
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/sda1", volume=ec2.BlockDeviceVolume.ebs(200)
                )
            ],
            key_name=key_name,  # use the public key
        )

        ssm.CfnAssociation(
            self,
            "SSMAssociation",
            name="AWS-RunShellScript",
            targets=[{"key": "InstanceIds", "values": [ec2_instance.instance_id]}],
            parameters={
                "commands": [
                    # set hostname
                    f"hostnamectl set-hostname {name}",
                    f"echo '127.0.0.1 {name}' >> /etc/hosts",
                    # fix bash shell: export PS1="\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "
                    "sed -i '/^#force_color_prompt=/s/^#//' /home/ubuntu/.bashrc",
                    # update and install packages
                    "apt-get update",
                    "apt-get install -y make jq awscli protobuf-compiler libprotobuf-dev pkg-config libssh-dev libssl-dev pkg-config build-essential neovim git net-tools netcat",
                    # install go
                    "wget https://go.dev/dl/go1.20.linux-amd64.tar.gz",
                    "tar xvzf go1.20.linux-amd64.tar.gz",
                    "sudo cp go/bin/go /usr/bin/go",
                    "sudo mv go /usr/lib",
                    "echo export GOROOT=/usr/lib/go >> /home/ubuntu/.bashrc",
                    # install docker-ce
                    "sudo apt-get install ca-certificates curl gnupg",
                    "sudo install -m 0755 -d /etc/apt/keyrings",
                    "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg",
                    "sudo chmod a+r /etc/apt/keyrings/docker.gpg",
                    "echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu   jammy stable' | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null",
                    "sudo apt-get update",
                    "sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
                    # setup ubuntu user and start docker
                    "usermod -a -G docker ubuntu",
                    "chmod 666 /var/run/docker.sock",
                    "systemctl enable docker.service",
                    "systemctl start docker.service",
                    # install rust as the ubuntu user
                    "cd /home/ubuntu",
                    "su ubuntu -c 'curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y'",
                    "echo 'export PATH=$PATH:/home/ubuntu/.cargo/bin' >> /home/ubuntu/.bashrc",
                    # install foundry
                    "su ubuntu -c 'curl -L https://foundry.paradigm.xyz | bash'",
                    "su ubuntu -c '/home/ubuntu/.foundry/bin/foundryup'",
                    # Create key
                    "su ubuntu -c 'ssh-keygen -t ed25519 -N '' -f ~/.ssh/id_ed25519 <<< y'",
                    # Clone BLS-TSS-Network code
                    "cd /home/ubuntu",
                    "su ubuntu -c 'git clone https://github.com/wrinkledeth/BLS-TSS-Network.git'",
                    # Clone Optimism
                    "su ubuntu -c 'git clone https://github.com/wrinkledeth/optimism'",
                    # run optimism testnet
                    "cd /home/ubuntu/optimism",
                    "su -l ubuntu -c 'cd /home/ubuntu/optimism; git submodule update --init'",
                    # "su -l ubuntu -c 'cd /home/ubuntu/optimism; make devnet-up-deploy'",  # -l specifies a login shell to source .bashrc
                    # git submodule update --init
                    # make devnet-up-deploy
                    # create complete file
                    "touch /tmp/complete",
                    # broadcast completion with wall
                    "wall 'SSM Commands Complete!'",
                ]
            },
        )

        # Useful Outputs
        useful_outputs = CfnOutput(
            self,
            "UsefulOutputs",
            value=f"""
aws ssm start-session --target {ec2_instance.instance_id}
ssh ubuntu@{ec2_instance.instance_public_ip}
""",
            description="Useful Outputs",
        )


app = App()
EC2InstanceStack(app, f"{name}-ec2-stack")

app.synth()
