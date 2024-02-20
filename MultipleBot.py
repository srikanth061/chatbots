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
    return resp if option == "NPS" else resp.json().get("body")


def display_chats(chats):
    for chat in chats:
    # col1,col2 = st.columns([4,6])
    # with col2:
        with st.chat_message(name = "user"):
            st.markdown(chat["query"])
            st.markdown(f"<span style='font-size: smaller;'>{chat['time']}</span>", unsafe_allow_html=True)

        # c1,c2 = st.columns([10,0])
        # with c1:
        with st.chat_message(name="assistant"):
            st.markdown(chat['response'],unsafe_allow_html=True)
            st.markdown(f"<span style='font-size: smaller;'>{chat['time']}</span>", unsafe_allow_html=True)

def chatbot():
    st.session_state.sidebar_shown = False
    st.sidebar.title("Chat Bots")
    option = st.sidebar.radio("Select a Bot", ["NPS", "Tax", "Investopedia"])
    if "selected_option" not in st.session_state:
        st.session_state.selected_option = option
    elif st.session_state.selected_option != option:
        st.session_state.selected_option = option
        st.session_state.history = []
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
    if "history" not in chats:
        chats.history = []
    user_query = st.chat_input("Enter your question here...")
    if user_query != None:
        # current_time = datetime.now().strftime("%H:%M")
        UTC_time = datetime.now(timezone.utc)
        IST_offset = timedelta(hours=5, minutes=30)
        IST_time = UTC_time + IST_offset
        current_time = IST_time.strftime("%H:%M")
        response = send_query(user_query,option)
        cleaned_response = response.text.replace("\\n", "<br>").replace("\n", "").replace('"',"") if option == "NPS" else  response.replace("\\n", "<br>").replace("\n", "").replace('"',"")
        chats.history.append({"query": user_query, "response": cleaned_response, "time":current_time})
    
    display_chats(chats.history)

    if len(chats.history)>=10:
        chats.history.pop(0)
        
chatbot()