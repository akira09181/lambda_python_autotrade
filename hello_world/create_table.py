# table作成時に一度だけ起動する
import boto3

dynamodb = boto3.resource('dynamodb')


def create_books_table():
    table = dynamodb.create_table(
        TableName='daily_ticker',
        KeySchema=[
            {'AttributeName': 'date',
             'KeyType': 'HASH'},
            {
                'AttributeName': 'ltp',
                'Keytype': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {'AttributeName': 'date', 'AttributeType': 'N'},
            {'AttributeName': 'ltp', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10}
    )
    table.wait_until_exists()
