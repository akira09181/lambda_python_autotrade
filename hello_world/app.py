import json

import boto3
import pybitflyer
import time
import hashlib
import requests
import hmac
# import requests
REGION = 'ap-northeast-1'


def header(method: str, endpoint: str, body: str) -> dict:
    ssm = boto3.client('ssm', region_name=REGION)
    response = ssm.get_parameters(
        Names=[
            'buy-btc-apikey',
            'buy-btc-apisecret',
        ],
        WithDecryption=True
    )
    apikey = response['Parameters'][0]['Value']
    apisecret = response['Parameters'][1]['Value']
    timestamp = str(time.time())
    if body == '':
        message = timestamp + method + endpoint
    else:
        message = timestamp + method + endpoint + body
    signature = hmac.new(apisecret.encode('utf-8'), message.encode('utf-8'),
                         digestmod=hashlib.sha256).hexdigest()
    headers = {
        'Content-Type': 'application/json',
        'ACCESS-KEY': apikey,
        'ACCESS-TIMESTAMP': timestamp,
        'ACCESS-SIGN': signature
    }
    return headers


def put_daily_ticker(ticker):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('daily_ticker')
    table.update_item(
        Key={
            'date': ticker['timestamp']
        },
        UpdateExpression="SET productcode = :product_code, best_bid = :best_bid, best_ask= :best_ask,last_traded_price = :ltp",
        ExpressionAttributeValues={
            ':product_code': ticker['product_code'],
            ':best_bid': ticker['best_bid'],
            ':best_ask': ticker['best_ask'],
            ':ltp': ticker['ltp']
        },
    )

    return ""


def lambda_handler(event, context):
    api = pybitflyer.API()
    ticker = api.ticker(product_code='BTC_JPY')
    put_daily_ticker(ticker)
    base_url = 'https://api.bitflyer.com'
    sendparentorder = '/v1/me/sendparentorder'
    body = {
        'order_method': 'IFD',
        'parameters': [{
            'product_code': 'BTC_JPY',
            'condition_type': 'LIMIT',
            'side': 'BUY',
            'price': int(ticker['ltp']*0.97),
            'size':0.001
        },
            {
            'product_code': 'BTC_JPY',
            'condition_type': 'LIMIT',
            'side': 'SELL',
            'price': int(ticker['ltp']*1.03),
            'size':0.001
        }
        ]}
    body = json.dumps(body)
    headers = header('POST', endpoint=sendparentorder, body=body)
    response = requests.post(base_url + sendparentorder,
                             data=body, headers=headers)

    return response
