import time
import streamlit as st
import requests
from datetime import datetime,timedelta,timezone
from dotenv import load_dotenv
import os


load_dotenv()

# Query_url = os.getenv("QUERY_URL")
Query_url_NPS = os.getenv("QUERY_URL_NPS")
Query_url_TAX = os.getenv("QUERY_URL_TAX")
Query_url_INVESTOPEDIA = os.getenv("QUERY_URL_INVESTOPEDIA")


def send_query(query,option):
    data = {"query": query}
    resp = requests.post(Query_url_NPS if option == "NPS" else Query_url_TAX if option == "Tax" else Query_url_INVESTOPEDIA,json = data)
    # return resp if option == "NPS" else resp.json().get("body")
    return resp.json().get("body")


def display_chats(chats,option):
    for chat in getattr(chats, f"{option.lower()}_history", []):
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"], unsafe_allow_html=True)
            st.markdown(f"<span style='font-size: smaller;'>{chat['time']}</span>", unsafe_allow_html=True)
    
def chatbot():
    st.sidebar.title("Chat Bots")
    option = st.sidebar.radio("", ["NPS", "Tax", "Investopedia"])
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
    # if "nps_history" not in chats:
    #     chats.nps_history = []
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
            # chats.nps_history.append({"role":"user","content":user_query,"time":current_time})
            getattr(chats, f"{option.lower()}_history").append({"role": "user", "content": user_query, "time": current_time})
        with st.chat_message("assistant"):
            type_message = st.empty()
            type_message.write("typing...")
            message_placeholder = st.empty()
            full_response = ""
            response=send_query(user_query,option)
            type_message.empty() 
            cleaned_response = response.replace("\\n", "<br>").replace("\n", "").replace('"',"")
            # cleaned_response = response.text.replace("\\n", "<br>").replace("\n", "").replace('"',"") if option == "NPS" else  response.replace("\\n", "<br>").replace("\n", "").replace('"',"")
            for i in cleaned_response:
                full_response+=i
                time.sleep(0.002)
                message_placeholder.markdown(full_response+" ",unsafe_allow_html=True)
            message_placeholder.markdown(full_response,unsafe_allow_html=True)
            st.markdown(f"<span style='font-size: smaller;'>{current_time}</span>", unsafe_allow_html=True)
            # chats.nps_history.append({"role":"assistant","content":cleaned_response,"time":current_time})
            getattr(chats, f"{option.lower()}_history").append({"role": "assistant", "content": cleaned_response, "time": current_time})
chatbot()
