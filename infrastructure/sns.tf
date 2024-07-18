locals {
  app_name         = "rio-fastapi-sns"
  backend_endpoint = ""
}

module "sns_raw" {
  source = "git::https://github.com/riolaf05/terraform-modules//aws/sns-topic"
  project_name = "${local.app_name}-raw-documents"
  bucket_name = module.s3.bucket_name
  bucket_arn = module.s3.bucket_arn
  filter_prefix = aws_s3_object.object_raw.key
}

module "sns_processed" {
  source = "git::https://github.com/riolaf05/terraform-modules//aws/sns-topic"
  project_name = "${local.app_name}-processed-documents"
  bucket_name = module.s3.bucket_name
  bucket_arn = module.s3.bucket_arn
  filter_prefix = aws_s3_object.object_processed.key
}

#processed messages subscription
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = module.s3.bucket_name

  topic {
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "raw_documents/"
    filter_suffix = null
    topic_arn     = module.sns_raw.topic_arn
  }
  topic {
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = aws_s3_object.object_processed.key
    filter_suffix = null
    topic_arn     = module.sns_processed.topic_arn
  }
}

# resource "aws_sns_topic_subscription" "sns_raw" {
#   topic_arn = module.sns_raw.topic_arn
#   protocol  = "https"
#   endpoint  = "${local.backend_endpoint}/summarization"
#   endpoint_auto_confirms = false
#   delivery_policy = <<EOF
#         {
#             "healthyRetryPolicy": {
#             "minDelayTarget": 1,
#             "maxDelayTarget": 60,
#             "numRetries": 50,
#             "numNoDelayRetries": 3,
#             "numMinDelayRetries": 2,
#             "numMaxDelayRetries": 35,
#             "backoffFunction": "linear"
#         },
#         "throttlePolicy": {
#             "maxReceivesPerSecond": 10
#         },
#         "requestPolicy": {
#             "headerContentType": "application/json; charset=UTF-8"
#         }
#     }
#     EOF
# }
