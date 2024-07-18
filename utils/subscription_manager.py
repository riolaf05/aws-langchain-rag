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