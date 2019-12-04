import json
import boto3

client = boto3.client('dynamodb')

def elicit_intent(message):
    return {
        'dialogAction': {
            'type': 'ElicitIntent',
            'message': {
                'contentType': 'PlainText',
                'content': message
            }
        }
    }

def close(intent_request, message):
  response = {
    'dialogAction': {
      'type': 'Close',
      'fulfillmentState': 'Fulfilled',
      "message": {
        "contentType": "PlainText",
        "content": message
      }
    }
  }
  return response
def check_details(intent_request):
    SSNumber = intent_request['currentIntent']['slots']['SSNumber']

    if '1234' == str(SSNumber):
        message = 'Your account is verified'
        return close(intent_request, message)
    else :
        message = 'The Number is Invalid. Would you like to talk to an Agent'
        return elicit_intent(message)

def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']
    if intent_name == 'CustomerVerification':
      return check_details(intent_request)
def lambda_handler(event, context):
    return dispatch(event)