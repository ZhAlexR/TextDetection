import boto3

from settings import settings


def crete_textract_client():
    return boto3.client(
        "textract",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        region_name=settings.AWS_REGION,
    )

def extract_text(image_path: str):
    textract_client = crete_textract_client()
    with open(image_path, "rb") as image:
        response = textract_client.detect_document_text(Document={"Bytes": image.read()})
    print(response)
