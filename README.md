# Internet Automated Dynamic DNS Client on AWS

This repository contains code to create an AWS stack with [Inadyn](https://github.com/troglobit/inadyn)-compatible
Dynamic DNS (DDNS) APIs for updating DNS records in AWS Route 53 DNS service. The provided DDNS APIs
can be used to configure DDNS in routers like the [Unifi Cloud Gateway](https://ui.com/jp/en/cloud-gateways) (UCG),
offering an alternative to paid services. For more details on configuring custom DDNS on UCG, please refer to
[this guide](https://community.ui.com/questions/How-to-Guide-to-Unifi-Gateway-DDNS-Dynamic-DNS-Services/6733acd9-61b3-4eba-80c1-d45df912e698).

## Overview

### What is Dynamic DNS?

Dynamic DNS (DDNS) is a service that automatically updates DNS records when an IP address changes. This is particularly useful for home networks and small businesses where the ISP provides dynamic (changing) IP addresses instead of static ones. DDNS ensures that your domain name (e.g., `home.example.com`) always points to your current IP address, even when it changes.

### What is Inadyn?

[Inadyn](https://github.com/troglobit/inadyn) (Internet Automated Dynamic DNS Client) is an open-source DDNS client that:

- Periodically checks your IP address for changes
- Automatically updates DNS records when changes are detected
- Supports multiple DDNS service providers
- Is widely used in routers and network devices
- Follows standard protocols for DDNS updates

### What This Project Does

This project creates an AWS infrastructure that:

1. Provides an Inadyn-compatible API endpoint using AWS API Gateway
2. Uses AWS Lambda to process DDNS update requests
3. Updates DNS records in AWS Route 53 (AWS's DNS service)
4. Supports both IPv4 and IPv6 address updates
5. Implements security through API key authentication

## System Requirements

The scripts are developed on Ubuntu Server 24.04. It might work on MacOS or other Linux flawors as well.
I have `uv` installed to manage Python dependencies.
You also need to have AWS CLI [installed](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
and [configured](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html#getting-started-quickstart-new).
[CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) is used to define and manage
AWS stack and is installed as Python dependency.

## Setup: AWS Side

### 1. AWS CLI Installation and Configuration

Install AWS CLI:

```sh
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

Configure AWS CLI:

```sh
$ aws configure
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-west-2
Default output format [None]: json
```

Required environment variables:

```sh
$ env | grep AWS
AWS_ACCESS_KEY_ID=...
AWS_HOSTED_ZONE_ID=...
AWS_SECRET_ACCESS_KEY=...
```

### 2. Python Dependencies Setup

```sh
uv venv
uv sync
source .venv/bin/activate
```

### 3. AWS Stack Initialization

```sh
# Only required for first-time CDK usage in your AWS account/region
cdk bootstrap
```

### 4. AWS Stack Deployment

```sh
API_KEY="<put your key here>" cdk deploy
```

Useful CDK commands:

- `cdk ls` - List all stacks
- `cdk diff` - Compare deployed stack with current state
- `cdk destroy` - Destroy the stack and all AWS resources

### 5. API Testing

```sh
# IPv4 test
curl "https://xyz123.execute-api.amazonaws.com/update?hostname=my.domain.com&myip=1.2.3.4"

# IPv6 test
curl "https://xyz123.execute-api.amazonaws.com/update?hostname=my.domain.com&myip=::1234:5678"
```

## Setup: Router side

Below are the steps to configure existing Inadyn client on the router side, like [Unifi Cloud Gateway](https://ui.com/us/en/cloud-gateways/compact) or other.

### 1. Router SSH Access

Follow your router's manual for SSH access instructions.

### 2. Locate Inadyn Installation

```sh
$ which inadyn
/usr/sbin/inadyn
$ inadyn --version
2.12.0
```

### 3. Locate Inadyn Configuration

```sh
$ ps -ef | grep inadyn
root     3658249    1647  0 Feb08 ?        00:00:01 /usr/sbin/inadyn -n -s -C -f /run/ddns-eth4-inadyn.conf
```

### 4. Configure Inadyn

Edit `/run/ddns-eth4-inadyn.conf`:

```conf
#
# Generated automatically by ubios-udapi-server
#
iface = eth4

period = 300
allow-ipv6 = true

# IPv6 configuration
custom hhmavquije.execute-api.us-east-2.amazonaws.com:2 {
    checkip-server = default
    hostname = "host6.example.com"
    username = "<API KEY>"
    password = "NO_PASSWORD_NEEDED"
    ddns-server = "my-iandyn-stack.amazonaws.com"
    ddns-path = "/prod/update?hostname=%h&myip=%i"
}

# IPv4 configuration
custom hhmavquije.execute-api.us-east-2.amazonaws.com:1 {
    checkip-command = "/usr/bin/curl -s -4 https://ifconfig.me/ip"
    hostname = "host4.example.com"
    username = "<API KEY>"
    password = "NO_PASSWORD_NEEDED"
    ddns-server = "my-iandyn-stack.amazonaws.com"
    ddns-path = "/prod/update?hostname=%h&myip=%i"
}
```

### 5. Restart Inadyn Service

```sh
# Clear cache
rm -rf /var/cache/inadyn/*

# Get process ID
ps -ef | grep inadyn

# Restart process
kill -HUP <process_id>
```

### 6. Verify DNS Updates

```sh
dig A host4.example.com
dig AAAA host6.example.com
```

## AWS Cost Considerations

This solution uses several AWS services that may incur costs:

- AWS Lambda (free tier: 1M requests/month)
- API Gateway (free tier: 1M calls/month)
- Route 53 (hosted zone: $0.50/month + query costs)

## Further Enhancements

Currently implemented:

- [x] Inadyn compatible DDNS endpoint with API key protection

Future considerations:y

- [ ] IAM role switching implementation
- [ ] CloudWatch logging integration
- [ ] AWS Systems Manager Parameter Store for credentials. Currently `API_KEY` and `AWS_HOSTED_ZONE_ID` have to be setup in the environment variables.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Directory Structure

```txt
inadyn-ddns-aws/
│── lambda/
│   ├── lambda_function.py  # Lambda function to update Route 53
│── inadyn_ddns_aws/
│   ├── __init__.py
│   ├── inadyn_ddns_aws_stack.py  # CDK Stack
│── app.py  # CDK Application Entry Point
│── pyproject.toml  # Dependencies managed by uv
```
