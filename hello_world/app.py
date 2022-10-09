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


def lambda_handler(event, context):
    api = pybitflyer.API()
    ticker = api.ticker(product_code='BTC_JPY')
    print(int(ticker['ltp']*0.97))
    base_url = 'https://api.bitflyer.com'
    getbalance = '/v1/me/getbalance'
    headers = header('GET', endpoint=getbalance, body='')
    response = requests.get(base_url + getbalance, headers=headers)
    print(response.json())

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }
