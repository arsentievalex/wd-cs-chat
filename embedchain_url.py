import os
from embedchain import App
from embedchain.config import BaseLlmConfig
import streamlit as st


urls = ["https://www.workday.com/en-us/customer-stories/i-p/kainos-taming-growth-challenges-workday-financials.html",
        "https://www.workday.com/en-us/customer-stories/q-z/veolia-streamlined-process-expenses-improves-efficiencies.html",
        "https://www.workday.com/en-us/customer-stories/i-p/life-time-empowers-frontline-workers.html",
        "https://www.workday.com/en-us/customer-stories/a-h/chess-hr-tools-and-talent-enhance-capacity-student-support.html",
        "https://www.workday.com/en-us/customer-stories/i-p/loandepot-at-home-with-all-the-data.html",
        "https://www.workday.com/en-us/customer-stories/i-p/life-care-services-budgeting-health-check-delivers-results.html",
        "https://www.workday.com/en-us/customer-stories/a-h/coventry-building-uk-payroll-simpler-efficient-effective.html",
        ]

st.set_page_config(page_title="Chat with WD website",  layout="centered",
                   initial_sidebar_state="auto", menu_items=None)

st.header("Chat with Workday website")
st.subheader("This chatbot is trained on selected Workday's customer stories. Ask me anything about Workday products and customer stories.")

with st.expander('See more'):
    """
    The chatbot was trained on the following web pages:
    - [Kainos: Taming Growth Challenges with Workday Financials](https://www.workday.com/en-us/customer-stories/i-p/kainos-taming-growth-challenges-workday-financials.html)
    - [Veolia: Streamlined Process for Expenses, Improves Efficiencies](https://www.workday.com/en-us/customer-stories/q-z/veolia-streamlined-process-expenses-improves-efficiencies.html)
    - [Life Time: Empowers Frontline Workers](https://www.workday.com/en-us/customer-stories/i-p/life-time-empowers-frontline-workers.html)
    - [Chess HR: Tools and Talent Enhance Capacity for Student Support](https://www.workday.com/en-us/customer-stories/a-h/chess-hr-tools-and-talent-enhance-capacity-student-support.html)
    - [loanDepot: At Home with All the Data](https://www.workday.com/en-us/customer-stories/i-p/loandepot-at-home-with-all-the-data.html)
    - [Life Care Services: Budgeting Health Check Delivers Results](https://www.workday.com/en-us/customer-stories/i-p/life-care-services-budgeting-health-check-delivers-results.html)
    - [Coventry Building: UK Payroll Simpler, Efficient, Effective](https://www.workday.com/en-us/customer-stories/a-h/coventry-building-uk-payroll-simpler-efficient-effective.html)
    
    Sample questions to ask:
    - Which Workday customer previously used SAP and multiple separate systems for financial reporting?
    - I'm looking for a customers that grew via M&A internationally and is using Workday Financial Management.
    - I'm looking for the quantified benefit of using Workday Expenses
    - I'm looking for a customer that is using Workday to manage their workforce and has a large number of employees.
    """

# Create a bot instance
os.environ["OPENAI_API_KEY"] = st.secrets["openai_credentials"]["API_KEY"]

@st.cache_resource(show_spinner=False)
def load_data(urls):
    bot = App.from_config(config_path="openai.yaml")

    # Embed online resources
    for url in urls:
        bot.add(url)

    return bot


def get_sources(citations):
    unique_urls = set()

    for item in citations:
        for element in item:
            if isinstance(element, dict) and 'url' in element:
                unique_urls.add(element['url'])

    return list(unique_urls)


bot = load_data(urls)
query_config = BaseLlmConfig(number_documents=1)

############################################

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question!"}]


if prompt := st.chat_input("Your question"):  # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages:  # Display the prior chat messages
    # if role is user
    if message["role"] == "user":
        with st.chat_message(message["role"]):
            st.write(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message(message["role"], avatar='https://logo.clearbit.com/workday.com'):
            st.write(message["content"])


# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar='https://logo.clearbit.com/workday.com'):
        with st.spinner("Thinking..."):
            response, citations = bot.chat(prompt, citations=True, config=query_config)

            sources = get_sources(citations)
            #italicized_sources = [f"*{source}*" for source in sources]

            full_response = response + "\n\n**Source**:\n" + f"*{sources[0]}*"

            st.write(full_response)

            message = {"role": "assistant", "content": full_response}
            st.session_state.messages.append(message)  # Add response to message history
