import os
import boto3
from botocore.exceptions import BotoCoreError, ClientError

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME')
AWS_REGION = os.environ.get('AWS_REGION')

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def upload_file_to_s3(file_obj, filename, content_type):
    try:
        s3_client.upload_fileobj(
            file_obj,
            AWS_S3_BUCKET_NAME,
            filename,
            ExtraArgs={
                'ContentType': content_type
            }
        )
        file_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{filename}"
        return file_url, None
    except Exception as e:
        return None, str(e)

def generate_presigned_url(filename, expiration=300):
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': AWS_S3_BUCKET_NAME, 'Key': filename},
            ExpiresIn=expiration
        )
        return url, None
    except Exception as e:
        return None, str(e) 