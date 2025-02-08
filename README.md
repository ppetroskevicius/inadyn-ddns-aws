# Internet Automated Dynamic DNS Client on AWS

This repository contains the AWS stack for [Inadyn](https://github.com/troglobit/inadyn) compatible
Dynamic DNS (DDNS) APIs to update the DNS records on AWS Route 53 DNS service. It could be used in
the routers like [Unifi Cloud Gateway](https://ui.com/jp/en/cloud-gateways) instead of other paid
alternatives. More details on configuring custom DDNS on Unifi Gateways could be found
[here](https://community.ui.com/questions/How-to-Guide-to-Unifi-Gateway-DDNS-Dynamic-DNS-Services/6733acd9-61b3-4eba-80c1-d45df912e698).

## Setup

Below steps setup the AWS side of the Inadyn compatible APIs.

### AWS CLI

### Python and CDK

Create and activate the virtual environment, install project dependencies:

```sh
uv venv
uv sync
source .venv/bin/activate
```

### Run

```sh
cdk bootstrap    # if this is the first time you're using CDK in your AWS account and region
API_KEY=<put your key here> cdk deploy       # deploy the stack
```

### Useful commands

- `cdk ls` list all stacks in the app
- `API_KEY=<put your key here> cdk deploy` deploy this stack to your default AWS account/region
- `cdk diff` compare deployed stack with current state
- `API_KEY=<put your key here> cdk destroy` destroy the stack with all AWS resources

### Test the API

```sh
curl "https://xyz123.execute-api.amazonaws.com/update?hostname=my.domain.com&myip=1.2.3.4"
# or
curl "https://xyz123.execute-api.amazonaws.com/update?hostname=my.domain.com&myip=::1234:5678"
```

### Security

The Inadyn compatible DDNS end point is protected by the
The stack is created and run as default AWS IAM user.

### Router side setup

Below are the steps to setup the Inadyn client on the router side (Unifi Cloud Gateway or other).

1. Edit the Inadyn process configuration file `/run/ddns-eth4-inadyn.conf`.

```txt
#
# Generated automatically by ubios-udapi-server
#
iface = eth4

period = 300
allow-ipv6 = true

# ipv6
custom hhmavquije.execute-api.us-east-2.amazonaws.com:2 {
    checkip-server = default   # will default to ipv6
    hostname = "host6.example.com"
    username = "<API KEY>"
    password = "NO_PASSWORD_NEEDED"
    ddns-server = "my-iandyn-stack.amazonaws.com"
    ddns-path = "/prod/update?hostname=%h&myip=%i"
}

# ipv4
custom hhmavquije.execute-api.us-east-2.amazonaws.com:1 {
    checkip-command = "/usr/bin/curl -s -4 https://ifconfig.me/ip"   # will be forced to ipv4
    hostname = "host4.example.com"
    username = "<API KEY>"
    password = "NO_PASSWORD_NEEDED"
    ddns-server = "my-iandyn-stack.amazonaws.com"
    ddns-path = "/prod/update?hostname=%h&myip=%i"
}
```

2. Clear cache:

```sh
rm -rf  /var/cache/inadyn/*
```

3. Check the `inadyn` process ID:

```sh
# ps -ef | grep inadyn
root     3658249    1647  0 22:17 ?        00:00:00 /usr/sbin/inadyn -n -s -C -f /run/ddns-eth4-inadyn.conf
```

4. Restart the `inadyn` process:

```sh
kill -HUP 3658249
```

5. Check the AWS Route 53 that the DNS got updated:

```sh
dig A host4.example.com
dig AAAA host6.example.com
```

## Other

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
