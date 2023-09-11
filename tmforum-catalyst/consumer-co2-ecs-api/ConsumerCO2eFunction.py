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

#connect to anthropic model
sf_secret_id = "anthropic"
response = client.get_secret_value(SecretId=sf_secret_id)
#ANTHROPIC_API_KEY = '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'
llm = ChatAnthropic(temperature=0, anthropic_api_key=ANTHROPIC_API_KEY, max_tokens_to_sample = 512)

## connect to snowflake
### snowflake variables
sf_account_id = "ELPHBMX.TMFCATALYST"
client = boto3.client('secretsmanager')
sf_secret_id = "snowflake_credentials"
response = client.get_secret_value(SecretId=sf_secret_id)
secrets_credentials = json.loads(response['SecretString'])
sf_password = secrets_credentials['password']
sf_username = secrets_credentials['username']
dwh = "dev_wh"
db = "carbon_optimization"
schema = "PUBLIC"
table = "CELL_TELEMETRY_V4"
#sf_password = "Test@123456"
#sf_username = "RAJAY"

##  Create the snowflake connection string
connection_string = f"snowflake://{sf_username}:{sf_password}@{sf_account_id}/{db}/{schema}?warehouse={dwh}"

##  Create the snowflake  SQLAlchemy engine
engine_snowflake = create_engine(connection_string, echo=False)
dbsnowflake = SQLDatabase(engine_snowflake)

#retrieve and parse glue catalog
def parse_catalog():
    #Connect to Glue catalog
    #get metadata of redshift serverless tables
    columns_str=''
    
    #define glue cient
    glue_client = boto3.client('glue')
    
    for db in gdc:
        response = glue_client.get_tables(DatabaseName =db)
        for tables in response['TableList']:
            classification = tables['Parameters']['classification']
            for columns in tables['StorageDescriptor']['Columns']:
                    dbname,tblname,colname=tables['DatabaseName'],tables['Name'],columns['Name']
                    columns_str=columns_str+f'\n{classification}|{dbname}|{tblname}|{colname}'     
      
    #API
    ## Append the metadata of the API to the unified glue data catalog
    columns_str=columns_str+'\n '
    return columns_str
gdc = ['snowflake-carbon-optimization']
glue_catalog = parse_catalog()

#display a few lines from the catalog
print('\n'.join(glue_catalog.splitlines()[-20:]) )