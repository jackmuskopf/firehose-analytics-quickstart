// - firehose role - //
resource "aws_iam_role" "firehose" {
  name = "${local.prefix}-firehose"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "firehose.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "firehose" {
  role = aws_iam_role.firehose.name

  policy = <<EOF
{
    "Version": "2012-10-17",  
    "Statement":
    [    
        {      
            "Effect": "Allow",      
            "Action": [
                "s3:AbortMultipartUpload",
                "s3:GetBucketLocation",
                "s3:GetObject",
                "s3:ListBucket",
                "s3:ListBucketMultipartUploads",
                "s3:PutObject"
            ],      
            "Resource": [        
                "${aws_s3_bucket.destination.arn}",
                "${aws_s3_bucket.destination.arn}/*"      
            ]    
        }
    ]
}
EOF
}

// - analytics role - //
resource "aws_iam_role" "analytics" {
  name = "${local.prefix}-analytics"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "kinesisanalytics.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "analytics" {
  role = aws_iam_role.analytics.name

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Firehose",
      "Effect": "Allow",
      "Action": [
        "firehose:DescribeDeliveryStream",
        "firehose:Get*",
        "firehose:Put*"
      ],
      "Resource": [
        "${aws_kinesis_firehose_delivery_stream.input.arn}",
        "${aws_kinesis_firehose_delivery_stream.output.arn}"
      ]
    },
    {
       "Effect": "Allow", 
       "Action": [
           "lambda:InvokeFunction", 
           "lambda:GetFunctionConfiguration" 
       ],
       "Resource": [
          "${aws_lambda_function.processor.arn}:*",
          "${aws_lambda_function.processor.arn}"
       ]
    },
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Effect" : "Allow",
      "Resource" : "*"
    }
  ]
}
EOF
}

// - lambda role - //
resource "aws_iam_role" "processor" {
  name = "${local.prefix}-processor"

  assume_role_policy = <<EOF
{
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
}
EOF
}

resource "aws_iam_role_policy" "processor" {
  role = aws_iam_role.processor.name

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
        "Effect": "Allow",
        "Action": [
          "ec2:DescribeNetworkInterfaces",
          "ec2:CreateNetworkInterface",
          "ec2:DeleteNetworkInterface"
        ],
        "Resource": "*"
    },
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Effect" : "Allow",
      "Resource" : "*"
    }
  ]
}
EOF
}
