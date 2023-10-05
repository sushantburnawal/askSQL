__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from vanna.local import LocalContext_OpenAI
from utils import *
import streamlit as st
import hashlib

@st.cache_data(show_spinner="Generating SQL query ...")
def ask_question(question):
    # try:
    sql = vn.ask(question=question, print_results=False)[0]
    return sql
    # except Exception:
    #     st.warning("OpenAI API timeout!!",icon="🚨" )
                
    

@st.cache_data(show_spinner="Running SQL query ...")
def run_sql(sql,question,auto_train):
    df=None
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
        
        if len(df.index)>0 and auto_train:
            vn.add_question_sql(question=question,sql=sql)
            print("Training Data added successfully")
        
    else:
        pass

    return df


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
def make_hashes(password):
    	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False
# DB Management
import sqlite3 
conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data

def set_question(question):
    st.session_state["my_question"] = question

st.set_page_config(layout="wide")
st.title("askSQL📃🔬")

menu = ["Home","Login"]
choice = st.sidebar.selectbox("Menu",menu)

if choice == "Home":
    st.subheader("Home Screen")
    st.write('Go log in yourself !!')
    

elif choice == "Login":
    

    username = st.sidebar.text_input("User Name")
    password = st.sidebar.text_input("Password",type='password')
    if st.sidebar.checkbox("Login"):
        # if password == '12345':
        create_usertable()
        hashed_pswd = make_hashes(password)

        result = login_user(username,check_hashes(password,hashed_pswd))
        if result:
            api_key = st.sidebar.text_input("OpenAI API Key:")
            if st.sidebar.checkbox("Check my OpenAI key"):
                if is_openai_api_key_valid(api_key):
                    vn = LocalContext_OpenAI({"api_key": api_key})
                    st.sidebar.checkbox("Show SQL", value=True, key="show_sql")
                    st.sidebar.button("Rerun", on_click=setup_session_state, use_container_width=True)

                    st.sidebar.write(st.session_state)
                    
                    st.subheader("You have logged in !!")
                    
                    assistant_message_suggested = st.chat_message("assistant", avatar="chatbot.png")           
                    my_question = st.session_state.get("my_question", default=None)
                    if my_question is None:
                        my_question = st.chat_input("Ask me a question about your data",)
                        
                    if my_question:
                        st.session_state["my_question"] = my_question
                        user_message = st.chat_message("user")
                        user_message.write(f"{my_question}")
                        
                        sql = ask_question(question=my_question)
                    
                        if sql:
                            if st.session_state.get("show_sql", True):
                                assistant_message_sql = st.chat_message(
                                    "assistant", avatar="chatbot.png"
                                )
                                assistant_message_sql.code(sql, language="sql", line_numbers=True)
                            # user_message_sql_check = st.chat_message("user")
                            # user_message_sql_check.write(f"Are you happy with the generated SQL code?")
                            # with user_message_sql_check:
                            #     happy_sql = st.radio(
                            #         "Happy",
                            #         options=["", "yes", "no"],
                            #         key="radio_sql",
                            #         index=0,
                            #     )
                            # if happy_sql == "no":
                            #     st.warning("Please fix the generated SQL code.")
                            #     sql_response = st.chat_input("Write your SQL query",)
                            #     user_message_sql_rewrite = st.chat_message("user")
                            #     user_message_sql_rewrite.code(sql_response, language="sql", line_numbers=True)
                            #     #sql_response = code_editor(sql, lang="sql")
                            #     fixed_sql_query = sql_response
                            #     print(fixed_sql_query)
                            #     if fixed_sql_query != "" and fixed_sql_query is not None:
                            #         try:
                            #             df = run_sql(sql=fixed_sql_query)
                            #         except:
                            #             st.warning("Check your SQL query, there is something wronng !!")
                            #             df = None
                            #     else:
                            #         df = None
                            # elif happy_sql == "yes":
                            #     try:
                            df = run_sql(sql=sql,question=my_question,auto_train=False)
                            
                            if df is not None:
                                st.session_state["df"] = df
                                
                            if st.session_state.get("df") is not None:
                                if st.session_state.get("show_table", True):
                                    df = st.session_state.get("df")
                                    assistant_message_table = st.chat_message(
                                        "assistant",
                                        avatar="chatbot.png",
                                    )
                                    if len(df) > 10:
                                        assistant_message_table.text("First 10 rows of data")
                                        assistant_message_table.dataframe(df.head(10))
                                    else:
                                        assistant_message_table.dataframe(df)
                                        
                            #st.session_state["my_question"] = my_question
                            st.chat_input(placeholder="Click Rerun to ask another question",disabled=True)
                            
                        else:
                            assistant_message_error = st.chat_message("assistant", avatar="chatbot.png")
                            assistant_message_error.error("I wasn't able to generate SQL for that question")
                else: 
                    st.warning("Invalid API Key",icon="⚠️")    
        else:
            st.warning("Incorrect Username/Password")





# elif choice == "SignUp":
#     st.subheader("Create New Account")
#     new_user = st.text_input("Username")
#     new_password = st.text_input("Password",type='password')

#     if st.button("Signup"):
#         create_usertable()
#         add_userdata(new_user,make_hashes(new_password))
#         st.success("You have successfully created a valid Account")
#         st.info("Go to Login Menu to login")


