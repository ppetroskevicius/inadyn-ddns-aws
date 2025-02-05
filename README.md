# inadyn-ddns-aws

AWS stack for [Inadyn](https://github.com/troglobit/inadyn) compatible DDNS APIs.

Create and activate the virtual environment:

```sh
uv venv
source .venv/bin/activate
```

See the dependency tree for the project:

```sh
uv tree
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

- `cdk ls` list all stacks in the app
- `cdk synth` emits the synthesized CloudFormation template
- `cdk deploy` deploy this stack to your default AWS account/region
- `cdk diff` compare deployed stack with current state
- `cdk docs` open CDK documentation

Enjoy!
