import boto3
from trp import Document
from openai import OpenAI
from pydantic import BaseModel, Field

from settings import settings


def crete_textract_client():
    return boto3.client(
        "textract",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        region_name=settings.AWS_REGION,
    )

def extract_text(byte_file):
    textract_client = crete_textract_client()
    response = textract_client.analyze_document(
        Document={"Bytes": byte_file},
        FeatureTypes=["TABLES", "FORMS"]
    )
    return response


class NutritionRation(BaseModel):
    calories: int = Field(description="kcal the product contains per 100g")
    proteins: float = Field(description="proteins the product contains per 100g")
    fats: float = Field(description="fats the product contains per 100g")
    carbohydrates: float = Field(description="carbohydrates the product contains per 100g")


    def __str__(self):
        return f"Calories: {self.calories}, proteins: {self.proteins}, fats: {self.fats}, carbohydrates: {self.carbohydrates}"


explanation = """
You are an AI tasked with extracting structured nutritional values from raw OCR output.  
Each row represents a single entry from a nutrition table.  
The table data may be presented in different languages or contain multiple languages within the same entry.  

### Input Format:  
The input is a string containing multiple rows, where each row follows this format: 
    '|| index: <row index in the table> || data: <parsed data> ||\n'
Where:
    '||' represents table edges.
    '||\n' denotes the end of a row
Example Input: 
    '''
        || index: 0 || data: Näringsvärde / Naeringsvaerdi / Ravintoarvot / Nutrition  information  /  Nährwertangaben  ||
        || index: 1 || data:  100 g  23,5 g  %*/23,5 g  ||
        || index: 2 || data: Energi / Energiaa / Energy / Energie  2333 kJ 559 kcal  548 kJ 131 kcal  7%  ||
        || index: 3 || data: Fett / Fedt / Rasvaa / Fat  35 g  8,2 g  12 %  ||
        || index: 4 || data: varav mättat fett / heraf mattede fedtsyrer / josta tyydyttyneità rasvoja / of which saturates / davon gesättigte Fettsäuren  21 g  4,9 g  24%  ||
        || index: 5 || data: Kolhydrat / Kulhydrat / Hiilihydraattia / Carbohydrate / Kohlenhydrate  55 g  13 g  5 %  ||
        || index: 6 || data: varav sockerarter / heraf sukkerarter / josta sokereita / of which sugars / davon Zucker  50 g  12 g  13 %  ||
        || index: 7 || data: Fiber / Kostfibre / Ravintokuitua / Fibre / Ballaststoffe  2,3 g  0,5 g  -  ||
        || index: 8 || data: Protein / Proteiinia / Eiweiss  4,7 g  1,1 g  2 %  ||
        || index: 9 || data: Salt / Suolaa / Salz  0,35 g  0,08 g  1%  || 
    '''
"""



def crate_structured_response(input_data):

    open_api_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    completion = open_api_client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": explanation
            },
            {
                "role": "user",
                "content": input_data,
            },
        ],
        response_format=NutritionRation
    )

    return completion.choices[0].message.parsed



def get_nutrition_table(path_to_photo) -> NutritionRation:
    response = extract_text(path_to_photo)

    doc = Document(response)

    data = ""
    for page in doc.pages:
        for table in page.tables:
            for index, row in enumerate(table.rows):
                table_line = " ".join([cell.text for cell in row.cells])
                data += f"|| index: {index} || data: {table_line} ||\n"

    return crate_structured_response(data)
