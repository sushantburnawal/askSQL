#from vanna.local import LocalContext_OpenAI
import pymssql
import pandas as pd
import time
import random
import requests
import streamlit as st

def is_openai_api_key_valid(api_key):
    """
    Check if an OpenAI API key is valid by making a simple request to the API.

    Args:
        api_key (str): The OpenAI API key to be checked.

    Returns:
        bool: True if the API key is valid, False otherwise.
    """
    # Define the API endpoint you want to test
    api_endpoint = "https://api.openai.com/v1/models"

    # Set up the request headers with the API key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        # Make a GET request to the API
        print(1)
        response = requests.get(api_endpoint, headers=headers)
        print(response)
        print(2)
        # Check the response status code
        if response.status_code == 200:
            return True  # API key is valid
        else:
            return False  # API key is invalid

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False  # An error occurred, assume the key is invalid
    
def connect_to_database(**kwargs):
    for i in range(5):
        try:
            return pymssql.connect(**kwargs)
        except :
            wait_time = (2 ** i) + random.random()
            time.sleep(wait_time)
    raise Exception("Not able to connect to database, even after hitting max retries")

def run_sql_sql_server(sql: str):
    
    conn_sql_server = connect_to_database(host="sqlgpt.database.windows.net",user="sushant@sqlgpt",password="Solarsystem$123",database="sqlgpt")
    df = pd.read_sql(sql, conn_sql_server)
    return df

def setup_session_state():
    st.session_state["my_question"] = None
    st.session_state["df"] = None