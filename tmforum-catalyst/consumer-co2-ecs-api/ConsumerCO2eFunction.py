import json
import boto3

import sqlalchemy
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL

from langchain.docstore.document import Document
from langchain import PromptTemplate,SagemakerEndpoint,SQLDatabase, LLMChain
from langchain.llms.sagemaker_endpoint import LLMContentHandler
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts.prompt import PromptTemplate

from langchain.chains.api.prompt import API_RESPONSE_PROMPT
from langchain.chains import APIChain
from langchain.prompts.prompt import PromptTemplate
from langchain.chat_models import ChatAnthropic
from langchain.chat_models import ChatOpenAI
from langchain.chains.api import open_meteo_docs

from typing import Dict

from langchain_experimental.sql import SQLDatabaseChain
from langchain_experimental.sql.base import SQLDatabaseSequentialChain

def lambda_handler(event, context):
    
    
    #subprompt7 = f"Generate an SQL query to count the number chickens in a table that has chickens as a column"
    
    #print("Anthropic API key is: " + os.environ['ANTHROPIC_API_KEY'])
    
    #call anthropic to generate the offer
    #client = anthropic.Client('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')
    #client = anthropic.Client(os.environ['ANTHROPIC_API_KEY'])
    #anthropic = Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    #api_key=os.environ['ANTHROPIC_API_KEY'],
    #)
    # completion = anthropic.completions.create(
    # model="claude-2",
    # max_tokens_to_sample=1000,
    # temperature = 0,
    # prompt=f"{HUMAN_PROMPT} {subprompt7}\n{AI_PROMPT}",
    # )
    # print(completion.completion)
    ANTHROPIC_API_KEY = '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'
    llm = ChatAnthropic(temperature=0, anthropic_api_key=ANTHROPIC_API_KEY, max_tokens_to_sample = 512)
    

    ## snowflake variables
    sf_account_id = "ELPHBMX.TMFCATALYST"
    #sf_secret_id =<your snowflake credentials secret id>
    dwh = "dev_wh"
    db = "carbon_optimization"
    schema = "PUBLIC"
    table = "CELL_TELEMETRY_V4"
    sf_password = "Test@123456"
    sf_username = "RAJAY"
    ##  Create the snowflake connection string
    connection_string = f"snowflake://{sf_username}:{sf_password}@{sf_account_id}/{db}/{schema}?warehouse={dwh}"
    ##  Create the snowflake  SQLAlchemy engine
    engine_snowflake = create_engine(connection_string, echo=False)
    dbsnowflake = SQLDatabase(engine_snowflake)
    # raw_offer = completion.completion
    # raw_offer_sansfirstline = '\n'.join(raw_offer.split('\n')[1:])
    # offer_names = ["Talk, Surf and Stream Amazon Prime","Talk, Surf and Stream Netflix","Talk, Surf, Roam and Stream Amazon Prime", "Talk, Surf, Roam and Stream Netflix", "Talk, Surf and Roam", "Talk, Surf, Roam and Stream Big", "Keep in touch Basic"]
    
    # #search which offer was chosen and store it in the raw_offer_name variable
    # for offer in offer_names:
    #     if re.search(offer,raw_offer_sansfirstline):
    #         print(f'{offer} found in text!')
    #         raw_offer_name = offer
    #         print("raw_offer_name is:"+raw_offer_name)
    #         break
    #     else: 
    #         print(f'{offer} not found in text.')
        

    # #generate the email body
    # offer_link = 'http://54.235.46.70:8501/?customer_id='+custid
    # offer_call_to_action = 'Please click on this link to chat to our friendly assistant to know more about this offer: '+offer_link
    # offer_prefix = 'Dear '+first_name+','
    # offer_suffix = "Looking out for you,"+"\n"+"AWSome Telecom"
    # offer_body = offer_prefix+"\n"+raw_offer_sansfirstline+"\n\n"+offer_call_to_action+"\n\n"+offer_suffix
    # print("offer_body: "+offer_body)
    
    # try:
        
    #     #store offer
    #     response = table.update_item(
    #     Key={
    #         'customer_id': custid
    #     },
    #     UpdateExpression='SET offer = :new_offer,offer_body = :new_offer_body,to_email_id = :new_to_email_id',
    #     ExpressionAttributeValues={
    #         ':new_offer': raw_offer_name,
    #         ':new_offer_body': offer_body,
    #         ':new_to_email_id': to_email_id
    #     } 
    #     )
        
    #     #send offer
    #     email_client = boto3.client('pinpoint-email')
    #     response = email_client.send_email(
    #     FromEmailAddress='ajrav@amazon.co.uk',
    #     Destination={
    #         'ToAddresses': [
    #             to_email_id,
    #         ]
    #     },
    #     Content={
    #         'Simple': {
    #             'Subject': {
    #                 'Data': 'Your offer from an LLM'
    #             },
    #             'Body': {
    #                 'Text': {
    #                     'Data': offer_body
    #                 }
    #             }
    #         }
    #     }
    #     )
    #     print ("successully sent out a retention offer")
        
    #     #update the customer journey graph by sending a journey event
    #     url = 'https://e6t3g93z27.execute-api.us-east-1.amazonaws.com/dev/journeyevent'
    #     data = {
    #     "cust_id": custid,
    #     "order_id":'12345',
    #     "first_name":first_name,
    #     "offer":raw_offer_name,
    #     "offer_body":offer_body,
    #     "channel_pref":channel,
    #     "event_type":"has_retention_offer"
    #     }
    #     print("journey event api has been called with payload: "+str(data))
    #     headers = {}
    #     response = requests.post(url,headers=headers,json=data)
    #     response_dict = json.loads(response.text)
    #     print("The response from the journey event api is: "+str(response_dict))
    #     # #create an event bridge event signifying that the retention offer has been sent
    #     # event_payload = {
    #     #         'Time': strftime('%Y-%m-%d %H:%M:%S', localtime(time.time())),
    #     #         'Source': 'retention offer lambda',
    #     #         'Resources': [
    #     #             'string',
    #     #         ],
    #     #         'DetailType': 'retention offer event',
    #     #         'Detail': '{"cust_id":'+custid+',"event_type":"has_retention_offer",'+"offer:"+offer+"}",
    #     #         'EventBusName': 'default',
    #     #         'TraceHeader': 'retentionoffer'
    #     #     }
    #     # print("event bridge event payload is: "+ str(event_payload))
    #     # client = boto3.client('events')
    #     # response_evb = client.put_events(
    #     # Entries=[event_payload]
    #     # )
    #     # print()
    #     return {"status":"success"}
    # except Exception as e: 
    #     print(e)
    #     return {"status":"failed"}