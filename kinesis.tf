resource "aws_kinesis_firehose_delivery_stream" "input" {
  name        = "${local.prefix}-input"
  destination = "extended_s3"

  server_side_encryption {
    enabled = true
  }

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose.arn
    bucket_arn = aws_s3_bucket.destination.arn
    prefix     = "firehose-raw/"
  }

}

resource "aws_kinesis_analytics_application" "main" {
  name = "${local.prefix}-analytics-v1"

  lifecycle {
    ignore_changes = [code]
  }

  code = <<CODE
CREATE OR REPLACE STREAM "PRIME_NUMBER_STREAM" (number numeric, 
                                                   isPrime boolean);
-- CREATE OR REPLACE PUMP to insert into output
CREATE OR REPLACE PUMP "STREAM_PUMP" AS 
  INSERT INTO "PRIME_NUMBER_STREAM"
      SELECT "number", "isPrime"
      FROM   "firehose_in_001"
      WHERE  "isPrime";
CODE

  inputs {
    name_prefix = "firehose_in"

    kinesis_firehose {
      resource_arn = aws_kinesis_firehose_delivery_stream.input.arn
      role_arn     = aws_iam_role.analytics.arn
    }

    parallelism {
      count = 1
    }

    processing_configuration {

      lambda {
        resource_arn = "${aws_lambda_function.processor.arn}:$LATEST"
        role_arn     = aws_iam_role.analytics.arn
      }
    }

    schema {
      record_columns {
        mapping  = "$.content"
        name     = "content"
        sql_type = "VARCHAR(8)"
      }

      record_columns {
        mapping  = "$.size"
        name     = "size"
        sql_type = "NUMERIC"
      }

      record_columns {
        mapping  = "$.number"
        name     = "number"
        sql_type = "NUMERIC"
      }

      record_columns {
        mapping  = "$.isPrime"
        name     = "isPrime"
        sql_type = "BOOLEAN"
      }

      record_columns {
        mapping  = "$.cubeRoot"
        name     = "cubeRoot"
        sql_type = "REAL"
      }

      record_encoding = "UTF-8"

      record_format {
        mapping_parameters {
          json {
            record_row_path = "$"
          }
        }
      }
    }
  }

  outputs {
    name = "PRIME_NUMBER_STREAM"

    kinesis_firehose {
      resource_arn = aws_kinesis_firehose_delivery_stream.output.arn
      role_arn     = aws_iam_role.analytics.arn
    }

    schema {
      record_format_type = "CSV"
    }

  }

}

resource "aws_kinesis_firehose_delivery_stream" "output" {
  name        = "${local.prefix}-output"
  destination = "extended_s3"

  server_side_encryption {
    enabled = true
  }

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose.arn
    bucket_arn = aws_s3_bucket.destination.arn
    prefix     = "firehose-processed/"
  }

}
