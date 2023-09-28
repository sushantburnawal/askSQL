__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from vanna.local import LocalContext_OpenAI
from utils import *
import streamlit as st
import hashlib

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

            st.subheader("You have logged in !!")
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


