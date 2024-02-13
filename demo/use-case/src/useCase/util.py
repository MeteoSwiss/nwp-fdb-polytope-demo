import logging
import os

import boto3
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


def upload(filename, object_name):
    if (bucket := os.environ.get("UPLOAD_TO_S3_BUCKET")) is None:
        return

    client = boto3.client("s3")
    try:
        client.upload_file(filename, bucket, object_name)
    except ClientError as e:
        logger.error(e)
    else:
        logger.info("Uploaded output to S3 %s: %s", bucket, object_name)
