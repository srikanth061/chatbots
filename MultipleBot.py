import time
import streamlit as st
import requests
from datetime import datetime,timedelta,timezone
from dotenv import load_dotenv
import os
import sqlite3
from streamlit_feedback import streamlit_feedback
from streamlit_local_storage import LocalStorage
import uuid
import snowflake.connector as sn
import streamlit as st
from streamlit_js_eval import streamlit_js_eval
from nanoid import generate
    



load_dotenv()
Query_url_NPS = os.getenv("QUERY_URL_NPS")
Query_url_TAX = os.getenv("QUERY_URL_TAX")
Query_url_INVESTOPEDIA = os.getenv("QUERY_URL_INVESTOPEDIA")

def respond_to_salutations(question,option):
    greetings = ["hi", "hello", "hey"]
    thanks = ["thanks", "thank you"]

    if question.lower() in greetings:
        return "Hello! How can I assist you today?"
    elif question.lower() in thanks:
        return "You're welcome! If you have any other questions, feel free to ask."
    else:
        return send_query(question,option)
    
def send_query(query,option):
    data = {"query": query}
    resp = requests.post(Query_url_NPS if option == "NPS" else Query_url_TAX if option == "Tax" else Query_url_INVESTOPEDIA,json = data)
    return resp.json().get("body")


def display_chats(chats,option):
    for index,chat in enumerate(getattr(chats, f"{option.lower()}_history", [])):
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"], unsafe_allow_html=True)
            st.markdown(f"<span style='font-size: smaller;'>{chat['time']}</span>", unsafe_allow_html=True)
       
        if getattr(chats, f"{option.lower()}_history")[index]["role"]=="assistant":
            c1,c2=st.columns([1,15])
            with c1:
                st.button("👍",key=index,on_click=reactions,args=(1,chat,option,"from_displaychats"))
            with c2:
                st.button("👎",key=index+1,on_click=reactions,args=(0,chat,option,"from_displaychats"))
def reactions(reaction,chats,option,flag):
    # db = rf"chatbotDb.db"
    # conn = sqlite3.connect(db)
    # cursor = conn.cursor()
    conn=sn.connect(
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        role=os.getenv("ROLE"),
        schema=os.getenv("SCHEMA"),
        account=os.getenv("ACCOUNT"),
        database=os.getenv("DATABASE")
    )    
    cursor = conn.cursor()
    if flag == "from_chatbot":
        query = "UPDATE logs SET reaction = %s WHERE TO_VARCHAR(timestamp) = %s"
        parameters = (reaction, getattr(chats, f'{option.lower()}_history')[-1]['ist_time'])
        cursor.execute(query, parameters)

    elif flag == "from_displaychats":
        query = "UPDATE logs SET reaction = %s WHERE TO_VARCHAR(timestamp) = %s"
        parameters = (reaction, str(chats['ist_time']))
        cursor.execute(query, parameters)
        # getattr(chats,f'{option.lower()}_history')["reaction"] = reaction

    
    conn.commit()

def chatbot():
    st.sidebar.title("Chat Bots")
    option = st.sidebar.radio("", ["NPS", "Tax", "Investopedia"])
    if st.sidebar.button("LOGOUT"):
        LocalStorage().deleteItem("logs")
        st.session_state.clear() 
        # streamlit_js_eval(js_expressions="parent.window.location.reload()")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    header = st.container()
    if option == "NPS":
        header.title("Chatbot NPS")
    elif option == "Tax":
        header.title("Chatbot Tax")
    elif option == "Investopedia":
        header.title("Chatbot Investopedia")

    header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

    st.markdown(
        """
    <style>
        div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
            position: fixed;
            top: 2.875rem;
            background-color: white;
            z-index: 999;
            width:100%
        }
        # .fixed-header {
        #     border-bottom: 1px solid black;
        # }
    </style>
        """,
        unsafe_allow_html=True
    )
    
    chats = st.session_state

    for bot in ["nps", "tax", "investopedia"]:
        if f"{bot}_history" not in chats:
            setattr(chats, f"{bot}_history", [])

    user_query = st.chat_input("Enter your question here...")
    display_chats(chats,option)
    if user_query != None:
        UTC_time = datetime.now(timezone.utc)
        IST_offset = timedelta(hours=5, minutes=30)
        IST_time = UTC_time + IST_offset
        current_time = IST_time.strftime("%H:%M")
        with st.chat_message("user"):
            st.markdown(user_query)
            st.markdown(f"<span style='font-size: smaller;'>{current_time}</span>", unsafe_allow_html=True)
            getattr(chats, f"{option.lower()}_history").append({"role": "user", "content": user_query, "time": current_time,"ist_time": IST_time})
        with st.chat_message("assistant"):
            type_message = st.empty()
            type_message.write("typing...")
            message_placeholder = st.empty()
            full_response = ""
            response=respond_to_salutations(user_query,option)
            type_message.empty() 
            cleaned_response = response.replace("\\n", "<br>").replace("\n", "").replace('"',"")
            response_for_db = response.replace("\\n", "").replace("\n", "").replace('"',"")
            for i in cleaned_response:
                full_response+=i
                time.sleep(0.002)
                message_placeholder.markdown(full_response+" ",unsafe_allow_html=True)
            message_placeholder.markdown(full_response,unsafe_allow_html=True)
            st.markdown(f"<span style='font-size: smaller;'>{current_time}</span>", unsafe_allow_html=True)
            getattr(chats, f"{option.lower()}_history").append({"role": "assistant", "content": cleaned_response, "time": current_time,"ist_time": IST_time})
        c1,c2 = st.columns([1,15])
        with c1:
            st.button("👍",on_click=reactions, args=(1,chats,option,"from_chatbot"))
        with c2:
            st.button("👎",on_click=reactions, args=(0,chats,option,"from_chatbot"))
        # message_id = str(uuid.uuid4())
        
        # user = LocalStorage().getItem("logs").get("logs")[1]
        time.sleep(3)
        conn=sn.connect(
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        role=os.getenv("ROLE"),
        schema=os.getenv("SCHEMA"),
        account=os.getenv("ACCOUNT"),
        database=os.getenv("DATABASE")
        ) 
        cursor = conn.cursor()
        
        cursor.execute(f"INSERT INTO logs (email, question, answer, timestamp,session_id) VALUES (%s,%s,%s,%s,%s)",(st.session_state["user_email"], user_query,response_for_db,IST_time,st.session_state["session_id"]))
        # cursor.execute(f"INSERT INTO logs (email, question, answer, timestamp) VALUES (%s,%s,%s,%s)",(user, user_query,response_for_db,IST_time))
        # cursor.execute(f"INSERT INTO logs (email, question, answer, timestamp) VALUES (?,?,?)",("test1", user_query,response_for_db,IST_time))
        # cursor.execute("SELECT MAX(id) FROM logs")
        # last_row_id = cursor.fetchone()[0]
        # print("Last inserted ID:", last_row_id)
        # print(last_row_id,"kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
        # getattr(chats,f"{option.lower()}_history")[-1]["message_id"] = last_row_id



def LoggedIn_Clicked(userName, password):
    conn=sn.connect(
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    role=os.getenv("ROLE"),
    schema=os.getenv("SCHEMA"),
    account=os.getenv("ACCOUNT"),
    database=os.getenv("DATABASE")
)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE email = %s AND password = %s",(userName,password))
    USER = cursor.fetchone()
    conn.close()
    if USER:
        if userName == USER[1] and password == USER[2]:
            localS = LocalStorage()
            # localS.setItem(itemKey="session",itemValue=str(uuid.uuid4()))
            session_id = str(uuid.uuid4())
            # session_id = generate(size=10)
            # print(session_id,"////////////////////")
            localS.setItem(itemKey="logs",itemValue=[session_id,USER[1]])
            
            # if "user_email" not in st.session_state:
            #     st.session_state["user_email"]=USER[1]
            # if "user_id" not in st.session_state:
            #     st.session_state["user_id"]=USER[0]
            st.session_state['loggedIn'] = True
        else:
            st.session_state['loggedIn'] = False
            st.error("Invalid user name or password")
    else:
        st.error("user does't exist")


def show_login_page():
    userName = st.text_input (label="Email", value="", placeholder="Enter your user name")
    password = st.text_input (label="Password", value="",placeholder="Enter password", type="password")
    st.button ("Login", on_click=LoggedIn_Clicked, args= (userName, password))

# get_token = LocalStorage().getItem("logs").get("logs")
# LocalStorage().setItem(itemKey="email",itemValue="srikanth")
# get_token = LocalStorage().getAll()
# print(get_token)
# time.sleep(0.5)
# if get_token and get_token["storage"] and get_token["storage"]["value"] == "logged":
    # chatbot()
# else:
    # show_login_page()
# if get_token and get_token[0]:
#     chatbot()
# else:
#     # show_login_page()

get_token = LocalStorage().getItem("logs")
if "user_email" not in st.session_state:
    if get_token and get_token["storage"] and len(get_token["storage"]["value"])!=0:
        st.session_state["user_email"]=get_token["storage"]["value"][1]
if "session_id" not in st.session_state:
    if get_token and get_token["storage"] and len(get_token["storage"]["value"])!=0:
        st.session_state["session_id"]=get_token["storage"]["value"][0]
if get_token and get_token["storage"] and len(get_token["storage"]["value"])!=0:
    chatbot()
else:
    show_login_page()

    
