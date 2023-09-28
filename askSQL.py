__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from vanna.local import LocalContext_OpenAI
from utils import *
import streamlit as st
import streamlit_authenticator as stauth
import pickle
from pathlib import Path


def ask_question(question,auto_train):
    try:
        sql = vn.ask(question=question, print_results=False)[0]
    except Exception:
        st.warning("OpenAI API timeout!!",icon="🚨" )
        
        
    print(sql)
    try:
        df = run_sql_sql_server(sql)
    except Exception as e:
        print(e)
        #Invalid line of questioning 
        e2 = str(e)
        error = "Invalid column name"
        if error in e2:
            strIndex = int(e2.index(error)) + len(error)
            endIndex = int(e2.find('.'))
            columnError = e2[strIndex:endIndex]
            st.warning("The term " + columnError + "does not exist in the database" ,icon="🚨")
        else :
            #Any other database related error due to querying
            st.warning("Could not execute your SQL query",icon="🚨")
    if df is not None:
        st.dataframe(df)
        if len(df.index)>0 and auto_train:
            vn.add_question_sql(question=question,sql=sql)
            print("Training Data added successfully")
    else:
        st.write("There are no records for your SQL query in the database")


# --- USER AUTHENTICATION ---
# names = ["Flatworld Solutions"]
# usernames = ["flatworldsolutions"]

# # load hashed passwords
# file_path = Path(__file__).parent / "hashed_pw.pkl"
# with file_path.open("rb") as file:
#     hashed_passwords = pickle.load(file)

# credentials = {
#         "usernames":{
#             usernames[0]:{
#                 "name":names[0],
#                 "password":hashed_passwords[0]
#                 }       
#             }
#         }

# authenticator = stauth.Authenticate(credentials,"askSQL_dashboard","abcdefg",cookie_expiry_days=30)

# name, authentication_status, username = authenticator.login("Login", "main")

# if authentication_status == False:
#     st.error("Username/password is incorrect")

# if authentication_status == None:
#     st.warning("Please enter your username and password")

# if authentication_status:
    
    # authenticator.logout("Logout", "sidebar")
    # st.sidebar.title(f"Welcome {name}")

st.title("askSQL📃🔬")
api_key = st.text_input("OpenAI API Key:")
question_input = st.text_input("Ask a Question on the Database:")
if st.button("Submit Question"):
    
    #question_input = st.text_input("Ask a Question on the Database:")
    if is_openai_api_key_valid(api_key):
        vn = LocalContext_OpenAI({"api_key": api_key})
        if question_input!="":
            
            with st.spinner("Searching. Please hold..."):

                try:
                    ask_question(question=question_input,auto_train=False)
                except Exception as e:
                    print(e)
        else:
            st.warning("Question cannot be empty",icon="⚠️")
    else :
        st.warning("Invalid API Key",icon="⚠️")

