# ec2-cdk

cdk to spin up development ec2 instance

## Usage

```bash
# populate .env file with ssh public key

cdk synth
cdk bootstrap
cdk deploy
```

## AWS SSM Parameter Store

```bash
ubuntu_ami = ec2.MachineImage.from_ssm_parameter(
    "/aws/service/canonical/ubuntu/server/focal/stable/current/amd64/hvm/ebs-gp2/ami-id"
)
```

Determine the image like so: 
https://discourse.ubuntu.com/t/finding-ubuntu-images-with-the-aws-ssm-parameter-store/15507

## Working commands

```bash
# install make and jq
sudo apt install -y make jq

# install go
wget https://go.dev/dl/go1.20.linux-amd64.tar.gz
tar xvzf go1.20.linux-amd64.tar.gz
sudo cp go/bin/go /usr/bin/go
sudo mv go /usr/lib
echo export GOROOT=/usr/lib/go >> ~/.bashrc

# install docker-ce
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo   "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu   jammy stable" |   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# setup ubuntu user and start docker
usermod -a -G docker ubuntu",
chmod 666 /var/run/docker.sock",
systemctl enable docker.service",
systemctl start docker.service",


# install foundry
curl -L https://foundry.paradigm.xyz | bash
/home/ubuntu/.foundry/bin/foundryup


```


## Running optimism devnet

```bash
# install foundry
curl -L https://foundry.paradigm.xyz | bash
bash
foundryup

# start optimism devnet
git clone https://github.com/ethereum-optimism/optimism.git
cd optimism/
git reset --hard f30fdd3f2a25c87c57531f0a33dbf3d902a7ca57

git submodule update --init
make devnet-clean # if you need to clean
make devnet-up-deploy # deploy flag important for this one

```