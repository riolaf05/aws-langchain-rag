import os
import boto3
import logging
from typing import Optional
from utils.aws_services import AWSS3
from fastapi import UploadFile, HTTPException
from uuid import uuid4
from botocore.exceptions import ClientError
logger=logging.getLogger()

SNS_TOPIC=os.getenv('SNS_TOPIC')
SNS_ENDPOINT_SUBSCRIBE=os.getenv('SNS_ENDPOINT_SUBSCRIBE')
AWS_ACCESS_KEY_ID=os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION=os.getenv('AWS_REGION')
AWS_S3_BUCKET_NAME=os.getenv('AWS_S3_BUCKET_NAME')

class FileUploader:
    def __init__(self):
        self.logger = logging.getLogger("fileUploader")
        self.s3_client = AWSS3(AWS_S3_BUCKET_NAME)

    def pass_file_to_upload(self, raw_document_folder,  file_obj: UploadFile) -> dict:
        """
        Upload a file to S3.

        Args:
        file_obj (UploadFile): The file to upload.

        Returns:
        dict: A dictionary containing the upload result.
        """
        file_extension = file_obj.filename.split(".")[-1]
        file_name = f"{uuid4()}.{file_extension}"
        file_path_in_s3 = f"{raw_document_folder}/{file_name}"
        
        try:
            success = self.s3_client.upload_file(
                fileobj=file_obj.file, 
                key=file_path_in_s3,  
                )
            
            if success:
                self.logger.info(
                        f"Successfully stored {file_name} to S3 bucket {AWS_S3_BUCKET_NAME}/{raw_document_folder}."
                    )
                return {
                    "success": True,
                    "message": f"Successfully stored {file_name} to S3 bucket {AWS_S3_BUCKET_NAME}/{raw_document_folder}.",
                        }
            else:
                self.logger.error(
                    f"Failed to store {file_name} to S3 bucket {AWS_S3_BUCKET_NAME}/{raw_document_folder}."
                )
                return {
                    "success": False,
                    "message": f"Failed to store {file_name} to S3 bucket {AWS_S3_BUCKET_NAME}/{raw_document_folder}.",
                }

        except ClientError as e:
            self.logger.error(f"Error uploading file '{file_obj.filename}' to S3 {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            self.logger.error(f"Error uploading file '{file_obj.filename}' to S3 {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

#####################################################

class SubscriptionManager(object):
    """
    Class to create, manage and delete SNS subscriptions for an endpoint.
    """

    _subscription_arn: Optional[str]
    
    def __init__(self):
        self.logger = logging.getLogger("subscriber")
        self.logger.setLevel(logging.INFO)
        self._subscription_arn = None
    
    def process(self, **kwargs):
        """
        Processes a message received from SNS.

        :param kwargs: Request arguments
        :return: True if the message was processed successfully, False otherwise
        """
        try:
            message_type = kwargs["Type"]
            if not message_type:
                self.logger.error("Invalid message format: 'Type field is missing")
                return False

            self.logger.info(f"MESSAGE RECEIVED. TYPE: {message_type}")

            if message_type == "Notification":
                self.logger.info(f"{kwargs['Message']}\n")
                self.logger.info("NOTIFICATION_RECEIVED")

                ###
                # Elabora qui il messaggio
                logger.info(f"Message: {kwargs}")
                ###

            elif message_type == "SubscriptionConfirmation":
                self.confirm_subscription(kwargs["Token"])

            else:
                self.logger.warning(f"Unsuported message type: {message_type}")

            return True

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return False

    @property
    def subscription_arn(self) -> str:
        return self._subscription_arn

    @subscription_arn.setter
    def subscription_arn(self, arn: str):
        self._subscription_arn = arn

    @property
    def endpoint(self) -> str:
        return self._endpoint

    def create_subscription(self):
        """
        Subscribes an endpoint of this app to an SNS topic.

        :return: None
        """
        logging.info("Subscribing to SNS")
        sns = boto3.client(
            "sns",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        response = sns.subscribe(
            TopicArn=os.getenv("SNS_TOPIC"),
            Protocol="http",
            Endpoint=f'{os.getenv("SNS_ENDPOINT_SUBSCRIBE")}'
        )
        print("SUBSCRIBE RESPONSE\n", response)
        self._subscription_arn = response["SubscriptionArn"]

    def delete_subscription(self):
        """
        Deletes the endpoint subscription.

        :return: None
        """
        logging.info("Unsubscribing from SNS")
        sns = boto3.client(
            "sns",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )
        sns.unsubscribe(self.subscription_arn)

    def confirm_subscription(self, token: str):
        """
        Confirms the subscription to the topic, given the confirmation token.

        :param token:
        :return:
        """
        logging.info("Confirming Subscription")
        sns = boto3.client(
            "sns",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )
        response = sns.confirm_subscription(
            TopicArn=os.getenv("SNS_TOPIC"),
            Token=token
        )
        self._subscription_arn = response["SubscriptionArn"]