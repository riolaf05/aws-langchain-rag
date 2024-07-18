output "bucket_name" {
  value = module.s3.bucket_name
}

output "sns_raw_arn" {
  value = module.sns_raw.topic_arn
}

output "sns_enpoint_subscription_url" {
  value = "${local.backend_endpoint}/summarization"
}

