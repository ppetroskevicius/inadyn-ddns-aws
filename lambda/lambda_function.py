import base64
import ipaddress
import os

import boto3


def is_ipv6(ip):
  try:
    return isinstance(ipaddress.ip_address(ip), ipaddress.IPv6Address)
  except ValueError:
    return False


def lambda_handler(event, context):
  try:
    # Check authorization
    auth_header = event.get("headers", {}).get("Authorization")
    if not auth_header:
      return {"statusCode": 401, "body": "Authorization required"}

    # Extract and verify credentials
    try:
      auth_type, auth_string = auth_header.split(" ", 1)
      if auth_type.lower() != "basic":
        raise ValueError("Invalid auth type")

      decoded = base64.b64decode(auth_string).decode("utf-8")
      username, password = decoded.split(":", 1)

      # Verify against environment variable
      if username != os.environ["API_KEY"]:
        raise ValueError("Invalid credentials")

    except Exception:
      return {"statusCode": 401, "body": "Invalid credentials"}

    # Parse query parameters
    params = event.get("queryStringParameters", {})
    if not params:
      return {"statusCode": 400, "body": "Missing required parameters"}

    hostname = params.get("hostname")

    # Get client IP from request context
    # ip = event.get("requestContext", {}).get("identity", {}).get("sourceIp")
    ip = params.get("myip")

    # Determine record type based on IP version
    is_v6 = is_ipv6(ip)
    record_type = "AAAA" if is_v6 else "A"

    if not hostname or not ip:
      return {"statusCode": 400, "body": "Missing hostname or IP address"}

    # Initialize Route 53 client
    route53 = boto3.client("route53")

    # Update DNS record
    response = route53.change_resource_record_sets(
      HostedZoneId=os.environ["HOSTED_ZONE_ID"],
      ChangeBatch={
        "Changes": [
          {"Action": "UPSERT", "ResourceRecordSet": {"Name": hostname, "Type": record_type, "TTL": 300, "ResourceRecords": [{"Value": ip}]}}
        ]
      },
    )

    return {"statusCode": 200, "body": "good"}

  except Exception as e:
    print(f"Error: {str(e)}")
    return {"statusCode": 500, "body": f"Error: {str(e)}"}
