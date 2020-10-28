resource "aws_s3_bucket" "destination" {
  bucket = "${local.prefix}-destination"
  acl    = "private"
}
