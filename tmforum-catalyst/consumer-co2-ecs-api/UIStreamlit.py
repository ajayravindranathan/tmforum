import streamlit as st
import json
import sqlalchemy
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL
from langchain.docstore.document import Document
from langchain import PromptTemplate, SagemakerEndpoint, SQLDatabase, LLMChain
from langchain_experimental.sql import SQLDatabaseChain
from langchain.llms.sagemaker_endpoint import LLMContentHandler
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts.prompt import PromptTemplate
from langchain_experimental.sql import SQLDatabaseSequentialChain
from langchain.chains.api.prompt import API_RESPONSE_PROMPT
from langchain.chains import APIChain
from langchain.prompts.prompt import PromptTemplate
from langchain.chat_models import ChatAnthropic
from langchain.chat_models import ChatOpenAI
from langchain.chains.api import open_meteo_docs
from typing import Dict
import sqldbchain
from sqldbchain import SQLDatabaseChain2
from langchain.chat_models import ChatAnthropic as Anthropic
import anthropic
import boto3
import os  # Import the os module for working with environment variables
from pandas import DataFrame

# Get the API key and region from environment variables
client = boto3.client('secretsmanager')
anthropic_secret_id = "anthropic"
response = client.get_secret_value(SecretId=anthropic_secret_id)
secrets_credentials = json.loads(response['SecretString'])
ANTHROPIC_API_KEY = secrets_credentials['ANTHROPIC_API_KEY']
print("ANTHROPIC_API_KEY is:"+ANTHROPIC_API_KEY)
region = "eu-west-1"

# Define your LLM and database connection
llm = Anthropic(temperature=0.001, anthropic_api_key=ANTHROPIC_API_KEY, 
                max_tokens_to_sample=50000, 
                verbose=True)  # Use the region from environment variable

# Create connection to Snowflake
from sqlalchemy import create_engine

# Create connection to Snowflake 
account_identifier = 'cn30094.eu-west-1'
sf_secret_id = "snowflake_credentials"
response = client.get_secret_value(SecretId=sf_secret_id)
secrets_credentials = json.loads(response['SecretString'])
password = secrets_credentials['password']
user = secrets_credentials['username']
database_name = 'CARBON_OPTIMIZATION'
schema_name = 'PUBLIC'
warehouse_name = 'DEV_WH'
role_name = 'ACCOUNTADMIN'
conn_string = f"snowflake://{user}:{password}@{account_identifier}/{database_name}/{schema_name}?warehouse={warehouse_name}&role={role_name}"
engine_snowflake = create_engine(conn_string)
dbsnowflake = SQLDatabase(engine_snowflake)
gdc = ['snowflake-carbon-optimization']

# Define the Streamlit app
def main():
    st.title("Sustainability strategy assistant")
    st.subheader("Powered by Generative AI from AWS")
    
    # Demo Description
    logo_url = './1024px-Amazon_Web_Services_Logo.svg.png'
    st.sidebar.image(logo_url)
    st.sidebar.subheader("Demo Description")
    description = """
    Explore how our Amazon GenAI technology and Snowflake data platform can simplify your sustainability strategy analysis.
    """
    st.sidebar.markdown(description, unsafe_allow_html=True)

    # Template selection sidebar
    st.sidebar.subheader("Data Catalog Selection")
    glue_catalogue = st.sidebar.selectbox("Select a Glue Catalog:", ["snowflake-carbon-optimization", "other_catalog"])  # Add more catalogs if needed

#     # Template editing section
#     st.sidebar.subheader("Prompt Engineering")
#     template = st.sidebar.text_area("Edit Template:", """
#     Given an input question, create a syntactically correct {dialect} query to run.
    
#     Only use the following tables:
#     {table_info}
    
#     Question: {input}
#     """)

    template =  """
    Given an input question, create a syntactically correct {dialect} query to run.
    
    Only use the columns from the ctc table from the below tables:
    {table_info}
    
    Respond with only one sql query and nothing else.
    
    Example questions and outputs:
    Example 1:
    Question: what is the monthly trend of total co2 emission for all phone model Iphone 14 512GB in the year 2022?
    Answer: SELECT phone_model, EXTRACT(MONTH FROM timestamp) AS month, SUM(co2_emission) AS total_co2 FROM ctc WHERE EXTRACT(YEAR FROM timestamp) = 2022 GROUP BY phone_model, EXTRACT(MONTH FROM timestamp) ORDER BY phone_model, month
    Example 2:
    Question: which are the greenest cell ids in the network?
    Answer: SELECT tower_id, MIN(co2_emission) AS min_co2_emission FROM ctc WHERE green_charge_flag = '1' GROUP BY tower_id ORDER BY min_co2_emission ASC LIMIT 10
    
    Question: {input}
    """

    # User input section
    query = st.text_area("Talk to your digital carbon footprint data:")
    temperature = st.slider("Select temperature:", min_value=0.001, max_value=1.0, step=0.001, value=0.001)

    if st.button("Run Query"):
        if query:
            #st.write("Running the query...")
            response, sql_results = run_query(query, template, temperature)
            # Display the SQL query
            #st.subheader("Query:")
            #st.code(query, language="sql")

            # Display the SQL query results
            st.subheader("SQL Query Results:")
            st.dataframe(sql_results)
            time_cols = ['month', 'day','timestamp']
            groupby_col = next((col for col in time_cols if col in sql_results.columns), None)
            if groupby_col:
                numeric_cols = sql_results.select_dtypes('number').columns.tolist()
                non_time_cols = [col for col in numeric_cols if col != groupby_col]
                for col in non_time_cols:
                  st.bar_chart(sql_results, y = col, x=groupby_col)
            # if 'month' in sql_results.columns or 'timestamp' in sql_results.columns:
            #    groupby_col = 'month' if 'month' in sql_results.columns else 'timestamp'
            #    numeric_cols = sql_results.select_dtypes('number').columns.tolist()
            #    non_time_cols = [col for col in numeric_cols if col != groupby_col]
            #    for col in non_time_cols:
            #       st.bar_chart(sql_results, y = col, x=groupby_col)
            # Display the explanation
            st.subheader("Explanation:")
            st.write(response)
            
        else:
            st.warning("Please enter a query.")

# Define the run_query function
def run_query(query, template, temperature, retries = 3):
    db_chain = make_chain(query, template, temperature)
    for i in range(retries):
        try:
            response = db_chain.run(query)
            sql = get_query_retry(response)
            if sql:
                sql_results = execute_sql_query(sql)  # Execute the SQL query and get the results
            else:
                sql_results = "No sql query found after 3 tries"
            return response, sql_results
        except Exception as e:
            if i == retries - 1:
                raise
            else:
                pass
    

# Define the make_chain function
def make_chain(query, template, temperature):
    PROMPT_sql = PromptTemplate(
        input_variables=["input", "table_info", "dialect"], template=template
    )
    return SQLDatabaseChain2.from_llm(llm, dbsnowflake, prompt=PROMPT_sql, verbose=True)

# Define the execute_sql_query function
def execute_sql_query(query):
    
    result = engine_snowflake.execute(query)
    fetched = result.fetchall()
    return DataFrame(fetched)

def extract_sql(sql: str):
    anchor = '```sql'
    index = sql.find(anchor)
    if index > 0:
        start = index + len(anchor)
        end = sql.find('```', start)
        return sql[start:end]
    else:
        return None

def get_query(text):
  import re
  if '```sql' in text: 
    match = re.search(r'```sql(.*?)```', text, re.DOTALL)
    if match:
      return match.group(1).strip()
  
  elif 'SELECT' in text and ';' in text: 
        match = re.search(r'SELECT(.*?);', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
  else:
    if  'SELECT' in text:
        select_idx = text.index('SELECT')
        return text[select_idx:].strip()
  
  
    
  # If no SQL found, return None
  return None

def get_query_retry(text):
  for i in range(3):
    result = get_query(text)
    if result is not None:
      return result
  return None


      
if __name__ == "__main__":
    main()
