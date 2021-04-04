import json
import sys
import traceback
from io import StringIO
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier, Clock
from os import environ
from urllib.parse import urlencode


SLACK_OAUTH_TOKEN = environ['SLACK_OAUTH_TOKEN']
SLACK_SIGNING_SECRET = environ['SLACK_SIGNING_SECRET']

def execute(statement: str) -> str:
    out = StringIO()
    try:
        sys.stdout = out
        exec(statement)
        return out.getvalue()
    except Exception:
        return traceback.format_exc()
    finally:
        sys.stdout = sys.__stdout__


def pyccho(user_id: str, channel_id: str, statement: str):
    result = f'```{execute(statement)}```'

    blocks = [{
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': f'<@{user_id}> `/pyccho {statement}` の実行結果だよ〜'
        }
    }, {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': result
        }
    }]

    web_client = WebClient(token=SLACK_OAUTH_TOKEN)
    web_client.chat_postMessage(channel=channel_id, blocks=blocks)


def handler(event, context):
    print(json.dumps(event))

    signature_verifier = SignatureVerifier(signing_secret=SLACK_SIGNING_SECRET)
    if not signature_verifier.is_valid_request(body=urlencode(event['body']), headers=event['headers']):
        print('invalid request...')
        return {
            'statusCode': 403,
            'body': json.dumps({})
        }

    user_id = event['body']['user_id']
    channel_id = event['body']['channel_id']
    statement = event['body']['text']

    pyccho(user_id=user_id, channel_id=channel_id, statement=statement)

    return {
        'statusCode': 200,
        'body': json.dumps({})
    }
