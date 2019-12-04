from __future__ import print_function    # (at top of module)
import sys
import time
import datetime
from botocore.vendored import requests

#from props.default import *

import lib.obp
obp = lib.obp

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

def confirm_intent(intent_name, slots, message):
    return {
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': {
                'contentType': 'PlainText',
                'content': message
            } 
        }
    }

def elicit_slot(intent_name, slots, slot_to_elicit):
    return {
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
        }
    }

def welcome(intent_request):
    now = datetime.datetime.now()
    print(now.year, now.month, now.day, now.hour, now.minute, now.second)
    curHr = now.hour
    if curHr < 12:
        message = 'good morning'
    elif curHr < 18:
        message = 'good afternoon'
    else:
        message = 'good evening'
    print(message)
    return elicit_intent(message)

# Validating the account number 
def validate_account(slot_value):
    accounts=[]
    value = slot_value
    count = 0
    our_bank =obp.getBanks()
    for i in our_bank:
        #print(i['id'])
        priv_acc=obp.getPrivateAccounts(i['id'])
        #print(len(our_bank),len(priv_acc))
        for j in obp.getPrivateAccounts(i['id']):
            accounts.append(j['id'])
    if value is not None and value.lower() not in accounts:
        return "invalid"
    else:
        return "valid"
# Validate counter party name
def validate_counterparty(account,name):
    cpnames=[]
    our_bank =obp.getBanks()
    for i in our_bank:
        for j in obp.getPrivateAccounts(i['id']):
          if (j['id']==account):
            cp=obp.getCounterparties(i['id'],j['id'])
            for k in cp:
              cpnames.append(k['name'])
    if name is not None and name.lower() not in cpnames:
        return "invalid"
    else:
        return "valid"
    
#Fulfilled state
def close(intent_request,message):
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
#getting the balance of given account number
def check_balance(intent_request):
    account = intent_request['currentIntent']['slots']['account']
    print (account)
    source = intent_request['invocationSource']
    if source == 'DialogCodeHook':
      slots = intent_request['currentIntent']['slots']
      intent_name = intent_request['currentIntent']['name']
      if (account == None):
        return elicit_slot(intent_name,slots,'account')
      print (account)
      validation_result = validate_account(account)
      if validation_result == 'valid':
        our_bank =obp.getBanks()
        for i in our_bank:
          for j in obp.getPrivateAccounts(i['id']):
            if (j['id']==account):
                bank = i['id']
                our_account = obp.getAccount(bank,account)
                balance = our_account['balance']['amount']
                print (balance)
                message = "Your account balance is $"+ balance
                mess = message + 10*" "+ "\n Would you like to know anything?"
                #return close(intent_request,message)
                return elicit_intent(mess)
      else:
          message = "Invalid Account Number"
          return close(intent_request,message)
#listing the accounts which are owned by user
def listAccounts(intent_request):
    accounts=[]
    new_slot = intent_request['currentIntent']['slots']
    our_bank =obp.getBanks()
    for i in our_bank:
        #print(i['id'])
        priv_acc=obp.getPrivateAccounts(i['id'])
        #print(len(our_bank),len(priv_acc))
        for j in obp.getPrivateAccounts(i['id']):
            accounts.append(j['id'])
    data = '\n'.join(accounts)
    print (data)
    message = "your account numbers are : \n" + data
    content =  message + "\n\nWould you like to know anything?"
    #mess = {'mystring': 'Line 1\nLine 2'}
    print (content)
    #return close(intent_request, message)
    #return confirm_intent( 'Balance', new_slot, content)
    return elicit_intent(content)
#getting the counter parties names
def cplist(intent_request):
    cpnames=[]
    account = intent_request['currentIntent']['slots']['account']
    our_bank =obp.getBanks()
    m=validate_account(account)
    if m == 'valid':
      for i in our_bank:
        for j in obp.getPrivateAccounts(i['id']):
          if (j['id']==account):
            cp=obp.getCounterparties(i['id'],j['id'])
            for k in cp:
              cpnames.append(k['name'])
      print (cpnames)
      if (len(cpnames)==0):
        message = "you dont have any counter parties"
        return close(intent_request, message)
      else:
        data = "\n".join(cpnames)
        message = "your counterparties are:"+ data
        content = message + "\n Would you like to know anything?"
        #return close(intent_request, message)
        return elicit_intent(content)
    else:
        message = "Invalid Account Number"
        return close(intent_request,message)
        
def transactions(intent_request):
    transactions_list=[]
    account = intent_request['currentIntent']['slots']['account']
    our_bank =obp.getBanks()
    check_account=validate_account(account)
    if check_account == 'valid':
      for i in our_bank:
        for j in obp.getPrivateAccounts(i['id']):
          if (j['id']==account):
            details=obp.getTransactions(i['id'],j['id'])
            for n in details:
              transactions_list.append(('Time:', n['details']['completed'],'name:',n['other_account']['holder']['name'],'amount:',n['details']['value']['amount']))
      if (len(transactions_list)>0):
        data = " \n".join(transactions_list[0])
        message = "your last transaction details are:"+data
        content = message + "\n Would you like to know anything?"
        #return close(intent_request, message)
        return elicit_intent(content)
      else:
        message = "you dont have any transactions"
        return close(intent_request, message) 
    else:
        message = "Invalid Account number"
        return close(intent_request, message) 
def transfer(intent_request):
    account = intent_request['currentIntent']['slots']['account']
    cpname = intent_request['currentIntent']['slots']['name']
    amount = intent_request['currentIntent']['slots']['amount']
    account_check=validate_account(account)
    if account_check=='valid':
      our_bank =obp.getBanks()
      for i in our_bank:
        for j in obp.getPrivateAccounts(i['id']):
          if (j['id']==account):
              bank = i['id']
              our_account = obp.getAccount(bank,account)
              balance = our_account['balance']['amount']
              if float(amount)>float(balance):
                message = "insufficient balance"
                return close(intent_request, message) 
      cp_check = validate_counterparty(account,cpname)
      if cp_check == 'valid':
        obp.setPaymentDetails('USD',str(amount))
        cp=obp.getCounterparties('cb.44.us.cb',account)
        cpid = ""
        for j in cp:
          if (j['name']==cpname):
            cpid = j['counterparty_id']
        obp.createTransactionRequestV210('cb.44.us.cb',str(account),'COUNTERPARTY','cb.44.us.cb','19630908',cpid,'cb.44.us.cb')
        message = "Your transaction is successful"
        content = message + "\n Would you like to know anything?"
        #return close(intent_request, message)
        return elicit_intent(content)
      else:
          message = "Invalid Counterparty name"
          return close(intent_request, message)
    else:
        message = "Invalid Account number"
        return close(intent_request, message)


#    Handling Agent response based on the sourcetype
def Agent(intent_request):
    source_type = intent_request['requestAttributes']
    if source_type == None:
       message = "Please call 8333766219 to reachout to the agent"
       return close(intent_request, message)
    else:
       message = "We are transfering your call "
       return close(intent_request, message)
#def check_bankid(intent_request, bank_id):
#    message = "Your bank id:"+ bank_id
#    return close(intent_request,message)
def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']
    if intent_name == 'Welcome':
	    return welcome(intent_request)
    elif intent_name == 'Balance':
        return check_balance(intent_request)
    elif intent_name == 'listAccountsIntent':
        return listAccounts(intent_request)
    elif intent_name == 'ListCPsIntent':
        return cplist(intent_request)
    elif intent_name == 'ListTransactionsIntent':
        return transactions(intent_request)
    elif intent_name == 'TransferIntent':
        return transfer(intent_request)
    elif intent_name == 'CallAgent':
        return Agent(intent_request)
    
def lambda_handler(event, context):
   obp.setBaseUrl("https://citizensbank.openbankproject.com/")
   obp.setApiVersion("v4.0.0")

   # Login and set authorized token
   obp.login("michaelj","Infosys@123","a2kettx3t1hrnjeeswiptjgkkxy4prr4lo21wmrv")
   user = obp.getCurrentUser()
   print("Log stream name:", context.log_stream_name)
   print("Log group name:",  context.log_group_name)
   print("Request ID:",context.aws_request_id)
   print("invoked_function_arn ", context.invoked_function_arn )
   print("Event: ", event)
   print("Context: ", context)
   return dispatch(event)
   
  
