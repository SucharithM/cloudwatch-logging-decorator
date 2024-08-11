import boto3
from datetime import datetime
from typing import Union
from botocore.exceptions import ClientError
import logging

from configs.configs import AWS_REGION, DEFAULT_LOG_GROUP


class CloudWatchHandler:
    """
    A class to interact with CloudWatch Logs.
    """

    def __init__(self, region_name: str = AWS_REGION):
        """
        Initializes the CloudWatch client with the specified region.

        Args:
            region_name (str, optional): The AWS region where CloudWatch resides. Defaults to our server region from the Configs File.
        """
        self.client = boto3.client("logs", region_name=region_name)
        self.create_log_group(
            log_group_name=DEFAULT_LOG_GROUP
        )  # Default group of the server (can be overridden)

    def create_log_group(self, log_group_name: str) -> bool:
        """
        Creates a log group if it doesn't already exist.

        Args:
            log_group_name (str): The name of the log group to create.

        Returns:
            bool: True if the log group was created or already exists, False otherwise.
        """

        try:
            self.client.create_log_group(logGroupName=log_group_name)
            logging.info(f"Log group '{log_group_name}' created.")
            return True
        except ClientError as error:
            if error.response["Error"]["Code"] == "ResourceAlreadyExistsException":
                logging.info(f"Log group '{log_group_name}' already exists.")
                return True
            else:
                logging.exception(f"An error occurred creating log group: {error}")
                return False
        except Exception as exc:
            logging.exception(f"Unexpected error: {exc}")
            return False

    def create_log_stream(self, log_group_name: str, log_stream_name: str) -> bool:
        """
        Creates a log stream within a log group.

        Args:
            log_group_name (str): The name of the log group to create the stream in.
            log_stream_name (str): The name of the log stream to create.

        Returns:
            bool: True if the log stream was created or already exists, False otherwise.
        """

        try:
            self.client.create_log_stream(
                logGroupName=log_group_name, logStreamName=log_stream_name
            )
            logging.info(
                f"Log stream '{log_stream_name}' in group '{log_group_name}' created."
            )
            return True
        except ClientError as error:
            if error.response["Error"]["Code"] == "ResourceAlreadyExistsException":
                logging.info(
                    f"Log stream '{log_stream_name}' already exists in group '{log_group_name}'."
                )
                return True
            else:
                logging.exception(f"An error occurred creating log stream: {error}")
                return False
        except Exception as exc:
            logging.exception(f"Unexpected error: {exc}")
            return False

    def put_log_event(
        self, log_group_name: str, log_stream_name: str, message: Union[str, dict]
    ) -> bool:
        """
        Adds a log event to a specific log stream.

        Args:
            log_group_name (str): The name of the log group containing the stream.
            log_stream_name (str): The name of the log stream to write the event to.
            message (Union[str, dict]): The message to log, can be a string or a dictionary
                containing additional information for the event.

        Returns:
            bool: True if the log event was added successfully, False otherwise.
        """

        try:
            event = {
                "timestamp": int(datetime.now().timestamp() * 1000),
                "message": str(message),
            }
            self.client.put_log_events(
                logGroupName=log_group_name,
                logStreamName=log_stream_name,
                logEvents=[event],
            )
            logging.info(
                f"Log event added to '{log_stream_name}' in group '{log_group_name}'."
            )
            return True
        except Exception as exc:
            logging.exception(f"An error occurred adding log event: {exc}")
            return False
