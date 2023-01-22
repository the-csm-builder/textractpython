import boto3
import json

def lambda_handler(event, context):
    print(event)
    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Set up client for Textract
    textract = boto3.client('textract')
    s3 = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')

    # Extract text from image file
    response = textract.detect_document_text(
        Document={'S3Object': {'Bucket': bucket, 'Name': key}})
    text = ""
    for block in response['Blocks']:
        if block['BlockType'] == 'LINE':
            text += block['Text'] + '\n'
    print(text)

    # Insert the extracted text into DynamoDB. Create DynamoDB table if it doesn't exist
    table = dynamodb.Table('TABLE_NAME')
    table.put_item(
        Item={
            'file_name': key,
            'text': text
        }
    )

    # Copy object to another location
    copy_source = {'Bucket': bucket, 'Key': key}
    s3.copy_object(Bucket='BUCKET', CopySource=copy_source,
                   Key='DESTINATION_KEY/'+key)
