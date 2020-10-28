# Kinesis Firehose -> Kinesis Analytics Quickstart

## Requirements
- Terraform >= 0.13.0
- Python3.x
- GNU Make
- An AWS account with default credentials configured

## Deployment
- terraform init
- terraform apply
- make stream # to send sample data
- - Go to the AWS console and visit the SQL editor for your Kinesis Analytics application.  This will start the analytics application.
<br>
<br>
After a few minutes, you can see the output of the firehoses in S3.
