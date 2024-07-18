import os
import boto3
import logging
from typing import Optional
logger=logging.getLogger()

SNS_TOPIC=os.getenv('SNS_TOPIC')
SNS_ENDPOINT_SUBSCRIBE=os.getenv('SNS_ENDPOINT_SUBSCRIBE')
AWS_ACCESS_KEY_ID=os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION=os.getenv('AWS_REGION')


class SubscriptionManager(object):
    """
    Class to create, manage and delete SNS subscriptions for an endpoint.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("subscriber")
        self.logger.setLevel(logging.INFO)
    
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
