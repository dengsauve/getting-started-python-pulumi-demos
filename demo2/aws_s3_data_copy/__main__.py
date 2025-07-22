import pulumi
import pulumi_aws as aws
import pulumi_azure_native as azure

# Read the Azure Blob Storage URL prefix from another Pulumi stack
stack_ref = pulumi.StackReference("other-stack-name")
azure_blob_url_prefix = stack_ref.get_output("azure_blob_url_prefix")

# Create an S3 bucket
s3_bucket = aws.s3.Bucket("s3Bucket")

# Define a lambda function to copy data from Azure Blob to S3
lambda_role = aws.iam.Role("lambdaRole",
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Effect": "Allow",
                "Sid": ""
            }
        ]
    }""")

lambda_role_policy = aws.iam.RolePolicy("lambdaRolePolicy",
    role=lambda_role.id,
    policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject"
                ],
                "Resource": [
                    "arn:aws:s3:::%s/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": "logs:*",
                "Resource": "arn:aws:logs:*:*:*"
            }
        ]
    }""" % s3_bucket.bucket)

# Create the Lambda function
s3_lambda = aws.lambda.Function("s3Lambda",
    runtime="python3.8",
    role=lambda_role.arn,
    handler="index.handler",
    code=pulumi.AssetArchive({
        ".": pulumi.FileArchive("./lambda")
    }),
    environment=aws.lambda.FunctionEnvironmentArgs(
        variables={
            "S3_BUCKET": s3_bucket.bucket,
            "AZURE_BLOB_URL_PREFIX": azure_blob_url_prefix
        }
    ))

# Get the AWS CLI command template to copy data from Azure Blob to S3
copy_command = pulumi.Output.concat(
    "aws s3 sync ", azure_blob_url_prefix, " s3://", s3_bucket.bucket)

pulumi.export("s3_bucket_name", s3_bucket.bucket)
pulumi.export("copy_command", copy_command)