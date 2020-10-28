resource "aws_lambda_function" "processor" {
  filename         = "app.zip"
  function_name    = "${local.prefix}-processor"
  role             = aws_iam_role.processor.arn
  timeout          = 900
  handler          = "app.handlers.transform_records"
  runtime          = "python3.7"
  source_code_hash = filebase64sha256("app.zip")
}
