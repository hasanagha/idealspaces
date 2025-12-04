import uuid
import boto3
import logging

from django.conf import settings

aws_logger = logging.getLogger("aws")


class AWS():
    ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
    SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
    S3_URL = settings.S3DIRECT_URL

    @classmethod
    def upload_file(cls, fileobj, bucket_name='rightdoors-listing-assets'):
        # We use this to support using Minio in development
        endpoint_url = getattr(settings, "AWS_S3_ENDPOINT_URL", None)

        client = boto3.client(
            's3',
            aws_access_key_id=cls.ACCESS_KEY_ID,
            aws_secret_access_key=cls.SECRET_ACCESS_KEY,
            endpoint_url=endpoint_url
        )

        filename = uuid.uuid4().hex

        try:
            client.upload_fileobj(
                fileobj, bucket_name, filename,
                ExtraArgs={
                    'ContentType': fileobj.content_type,
                    'CacheControl': 'max-age=2592000',
                    'ACL': 'public-read'
                }
            )

            url = '{}/{}/{}'.format(
                cls.S3_URL,
                bucket_name,
                filename
            )

        except Exception as e:
            url = None
            aws_logger.debug("Trying to upload to s3 and got [{}]".format(e))

        return url
