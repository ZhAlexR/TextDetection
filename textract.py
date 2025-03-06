import boto3
from trp import Document

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
        response = textract_client.analyze_document(
            Document={"Bytes": image.read()},
            FeatureTypes=["TABLES"]
        )
    return response


if __name__ == "__main__":
    response = extract_text("data/nutrition-facts-label.jpg")

    doc = Document(response)

    # Process the tables
    for page in doc.pages:
        for table in page.tables:
            print(f"Table detected with {len(table.rows)} rows and {len(table.rows[0].cells)} columns")
            for row_idx, row in enumerate(table.rows):
                for cell_idx, cell in enumerate(row.cells):
                    print(f"Table[{row_idx}][{cell_idx}] = {cell.text}")