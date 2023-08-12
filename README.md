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

---

## Working OP Repo.

```bash
git clone https://github.com/wrinkledeth/optimism
git reset --hard f30fdd3f2a25c87c57531f0a33dbf3d902a7ca57

# edit bedrock-devnet/devnet 
['docker-compose', 'build', '--progress', 'plain'] # replace this with
["docker", "compose", "build", "--progress", "plain"] # this

# Makefile
docker-compose # replace this with
docker compose # this

# dockerfiles
# (search for string $BUILDPLATFORM) and add this to top:
ARG BUILDPLATFORM=linux/amd64
```


## Start Commands

```bash
git submodule update --init
make devnet-up-deploy 
make devnet-clean
```

## Troubleshoot Batcher

```bash
ubuntu@jammy:~/optimism$ docker logs f6804639456b
t=2023-08-11T19:46:55+0000 lvl=info msg=“Initializing Batch Submitter”
t=2023-08-11T19:46:55+0000 lvl=eror msg=“Unable to create Batch Submitter” error=“querying rollup config: Post \“http://op-node:8545\“: dial tcp 172.18.0.4:8545: connect: connection refused”
t=2023-08-11T19:46:55+0000 lvl=crit msg=“Application failed”               message=“querying rollup config: Post \“http://op-node:8545\“: dial tcp 172.18.0.4:8545: connect: connection refused”
```
