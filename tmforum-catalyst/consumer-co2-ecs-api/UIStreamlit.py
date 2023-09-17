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
    st.title("Digital Carbon Footprint Assistant")
    
    
    # Demo Description
    st.sidebar.subheader("Demo Description")
    description = """
    Explore how our advanced data platform and Generative AI can simplify your sustainability strategy analysis and network optimiization.
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

    template = """
    Given an input question, create a syntactically correct {dialect} query to run.
    
    Only use the table "ctc"
    
    Question: {input}
    """

    # User input section
    query = st.text_area("Talk to your carbon footpriint data:")
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
            # Display the explanation
            st.subheader("Explanation:")
            st.write(response)
            
        else:
            st.warning("Please enter a query.")

# Define the run_query function
def run_query(query, template, temperature):
    db_chain = make_chain(query, template, temperature)
    response = db_chain.run(query)
    sql = extract_sql(response)
    sql_results = execute_sql_query(sql)  # Execute the SQL query and get the results
    return response, sql_results

# Define the make_chain function
def make_chain(query, template, temperature):
    # PROMPT_sql = PromptTemplate(
    #     input_variables=["input", "table_info", "dialect"], template=template
    # )
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


if __name__ == "__main__":
    main()
