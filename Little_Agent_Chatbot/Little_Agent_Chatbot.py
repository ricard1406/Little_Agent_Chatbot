"""
Little Agent Chatbot is a simple yet powerful local AI assistant that runs entirely on your machine.
Built for learning and experimentation, it combines the power of open-source LLMs with advanced
retrieval-augmented generation (RAG) to create an intelligent chatbot that can work with your
personal documents and provide real-time information.
"""
VERSION="0.1.02"
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.agents import tool
import datetime
import requests
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain_text_splitters import RecursiveCharacterTextSplitter
import gradio as gr

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Chroma folder
CHROMA_PATH = "chroma_db"
# RAG documents folder
DATA_PATH = "data/"
PDF_FILENAME = "Candidates and Scores List - Test Data - compact.pdf"

LLM = "qwen3:1.7b"
### LLM = "qwen3:4b"
### LLM = "granite3.3:2b"
### LLM = "llama3.2:3b"

"""
Fetches current weather data for a given city from OpenWeatherMap.

Args:
    api_key (str): Your OpenWeatherMap API key.
    city_name (str): The name of the city for which to retrieve weather data.

Returns:
    dict: A dictionary containing weather data if successful, None otherwise.
"""
def get_weather_data(api_key, city_name):

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric"  # You can change to "imperial" for Fahrenheit
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        weather_data = response.json()
        return weather_data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred: {req_err}")
    except ValueError as json_err:
        print(f"Error decoding JSON response: {json_err}")
    return None


"""
    Displays relevant weather information from the fetched data,
    and returns it as a single string.

    Args:
        weather_data (dict): The dictionary containing weather data.

    Returns:
        str: A single string containing the formatted weather information,
             or an error message if data could not be retrieved.
"""
def display_weather(weather_data):

    if weather_data:
        city = weather_data.get("name")
        country = weather_data.get("sys", {}).get("country")
        main_weather = weather_data.get("weather", [])[0].get("description").capitalize() if weather_data.get(
            "weather") else "N/A"
        temperature = weather_data.get("main", {}).get("temp")
        feels_like = weather_data.get("main", {}).get("feels_like")
        humidity = weather_data.get("main", {}).get("humidity")
        wind_speed = weather_data.get("wind", {}).get("speed")

        # Combine all the data into a single string
        weather_string = (
            f"--- Weather in {city}, {country} ---\n"
            f"Description: {main_weather}\n"
            f"Temperature: {temperature}°C\n"
            f"Feels like: {feels_like}°C\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} m/s"
        )
        ######print(weather_string) # Still print for console output
        return weather_string
    else:
        error_message = "Could not retrieve weather data."
        ######print(error_message) # Still print for console output
        return error_message


def get_weather_tool(Location):
    # Get API key from environment variable
    api_key = os.getenv('OPENWEATHER_API_KEY')
    
    # Check if the API key exists
    if not api_key:
        raise ValueError("OpenWeatherMap API key not found. Please set the OPENWEATHER_API_KEY environment variable.")
    
    weather = get_weather_data(api_key, Location)
    weather_info_string = display_weather(weather)
    return weather_info_string


"""
    Performs basic arithmetic operations (ADD, SUB, MUL, DIV) on two numbers
    provided as strings.

    Args:
        OPERATION (str): The operation to perform ('ADD', 'SUB', 'MUL', 'DIV').
        NUM_ONE (str): The first number as a string.
        NUM_TWO (str): The second number as a string.

    Returns:
        str: The result of the operation as a string, or an error message as a string.
"""

def get_Calc(OPERATION, NUM_ONE, NUM_TWO):

    try:
        # Convert string inputs to floating-point numbers for calculation
        num1_float = float(NUM_ONE)
        num2_float = float(NUM_TWO)
    except ValueError:
        return "Error: NUM_ONE and NUM_TWO must be valid numbers."

    result = None
    if OPERATION == "ADD":
        result = num1_float + num2_float
    elif OPERATION == "SUB":
        result = num1_float - num2_float
    elif OPERATION == "MUL":
        result = num1_float * num2_float
    elif OPERATION == "DIV":
        if num2_float == 0:
            return "Error: Division by zero is not allowed."
        result = num1_float / num2_float
    else:
        return "Error: Invalid operation. Please use 'ADD', 'SUB', 'MUL', or 'DIV'."

    # Convert the numerical result back to a string
    return str(result)


#########################################################
# AGENTS TOOL DECLARATION
#########################################################

@tool
def get_current_datetime(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Returns the current actual date and the current actual time, formatted according to the provided Python strftime format string.
    Use this tool whenever the user asks for the current date, time, or both.
    Example format strings: '%Y-%m-%d' for date, '%H:%M:%S' for time.
    If no format is specified, defaults to '%Y-%m-%d %H:%M:%S'.
    """
    try:
        return datetime.datetime.now().strftime(format)
    except Exception as e:
        return f"Error formatting date/time: {e}"

@tool
def get_weather(location: str) -> str:
    """
    Returns the current weather for the given location, formatted as string.
    Use this tool whenever the user asks for the current weather.
    Format the location specify  City and State.
    Example : get_weather("London, UK") . You get the current weather in London, UK.
    """
    try:
        return get_weather_tool(location)
    except Exception as e:
        return f"Error formatting weather: {e}"

@tool
def get_local_data_RAG(local_query: str) -> str:
    """
    Returns data from local documents, formatted as String.
    Use this tool whenever the user asks for some data but you don't know anything about it, maybe local document can help you .
    Format the required data as String.
    Example : get_local_data_RAG("when was born Mr. John Smith ?") . You get the birthday of Mr. John Smith.
    """
    try:
        return get_local_document(local_query)
    except Exception as e:
        return f"Error formatting weather: {e}"


@tool
def get_arithmetic_operations(Operation: str, Number_1: str, Number_2: str) -> str:
    """
    Returns the result of arithmetic operations, formatted as String.
    Use this tool whenever the user asks for some arithmetic operations, this tool can help you .
    Format the required data as String.
    Parameters : OPERATION, NUM-ONE, NUM-TWO
    OPERATION allowed are : ADD, SUB, MUL, DIV
    NUM-ONE , NUM-TWO are numbers
    example: get_arithmetic_operations (ADD, 2, 3) : return 5
    example: get_arithmetic_operations (SUB, 2, 3) : return -1
    example: get_arithmetic_operations (MUL, 2, 3) : return 6
    example: get_arithmetic_operations (DIV, 2, 3) : return 0.6666
    """
    try:
        return get_Calc(Operation, Number_1, Number_2)
    except Exception as e:
        return f"Error formatting weather: {e}"

###############################################################################################
"""
LangChain's PyPDFLoader is a document loader designed to load and parse PDF documents into the LangChain Document format. 
It supports various configurations, such as handling password-protected files, extracting images, and defining extraction modes
"""

def load_documents_from_PDF_File():

    pdf_path = os.path.join(DATA_PATH, PDF_FILENAME)
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    return documents

"""
Document splitting is often a crucial preprocessing step for many applications. 
It involves breaking down large texts into smaller, manageable chunks. 
This process offers several benefits, such as ensuring consistent processing of varying document lengths, 
overcoming input size limitations of models, and improving the quality of text representations used in retrieval systems
"""

def split_document_into_smaller_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    splits = text_splitter.split_documents(documents)

    return splits

"""
Ollama embeddings refer to the process of generating vector representations of text using Ollama, 
a platform that allows users to run various AI models locally. 
These embeddings are numerical representations that capture the semantic meaning of text, 
enabling models to understand nuances in language by transforming words or phrases into vectors in a high-dimensional space.
"""

def Ollama_embeddings(model_name="nomic-embed-text"):

    embeddings = OllamaEmbeddings(model=model_name)

    return embeddings

"""
Chroma is an AI-native open-source vector database designed to store and query vector embeddings efficiently.
It allows users to store text documents, embeddings, and metadata, and provides tools for querying these collections 
to find semantically similar results
 """

def Chroma_vector_database(embedding_function, persist_directory=CHROMA_PATH):

    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_function
    )

    return vectorstore

embedding_function = Ollama_embeddings()

def Create_vector_database_Chroma(chunks, embedding_function, persist_directory=CHROMA_PATH):

    Collection = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=persist_directory
    )
    Collection.persist()

    return Collection

"""
list of tools, add here your own tool
"""

tools = [get_current_datetime, get_weather, get_local_data_RAG, get_arithmetic_operations]

def build_rag_chain(vector_store, llm_model_name=LLM, context_window=2048):

    llm = ChatOllama(
        model=llm_model_name,
        temperature=0,
        num_ctx=context_window
    )

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={'k': 3}
    )

    template = """Answer the question based ONLY on the following context:
{context}

Question: {question}
"""
    prompt = ChatPromptTemplate.from_template(template)

    rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )

    return rag_chain

vector_store = Chroma_vector_database(embedding_function)  # Assuming DB is already indexed
rag_chain = build_rag_chain(vector_store)  # Call this later

def query_rag(chain, question):
    """Queries the RAG chain and prints the response."""
    print("\nQuerying RAG chain...")
    print(f"Question: {question}")
    response = chain.invoke(question)
    print("\nResponse:")
    print(response)


def Langchain_Hub_prompt(prompt_hub_name="hwchase17/openai-tools-agent"):

    prompt = hub.pull(prompt_hub_name)

    return prompt


def Langchain_create_agent(llm, tools, prompt):

    agent = create_tool_calling_agent(llm, tools, prompt)

    return agent


def Langchain_ChatOllama(model_name=LLM, temperature=0, context_window=2048):

    llm = ChatOllama(
        model=model_name,
        temperature=temperature
    )

    return llm


def Langchain_AgentExecutor(agent, tools):

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True
    )

    return agent_executor

####################################################################################
#  Main Function
#
####################################################################################
if __name__ == "__main__":

    """
    Load PDF document based on
    LangChain's PyPDFLoader
    """
    documents = load_documents_from_PDF_File()

    """
    Document splitting into smaller, manageable chunks
    """
    chunks = split_document_into_smaller_chunks(documents)

    """
    Ollama embeddings generate vector representations
    """
    embedding_function = Ollama_embeddings()

    """
    Chroma vector database store and query vector embeddings
    """
    vector_database = Create_vector_database_Chroma(chunks, embedding_function)

    """
    The RAG (Retrieval-Augmented Generation) chain is a process that combines the capabilities of large language models (LLMs) 
    with external knowledge sources to generate more accurate and contextually relevant responses. 
    """
    rag_chain = build_rag_chain(vector_database, llm_model_name=LLM)

    # We need to make `get_local_document` use the pre-initialized `rag_chain`
    # One way is to make `get_local_document` a nested function or pass `rag_chain` to it.
    # For simplicity in Gradio, we'll ensure `get_local_data_RAG` calls the global `rag_chain`.
    # (Note: In a more complex app, you might use classes or functools.partial to bind these.)
    _global_rag_chain = rag_chain  # Storing it globally or passing it explicitly


    def get_local_document(local_query):
        print(f"\nQuerying RAG chain with: {local_query}")
        response = _global_rag_chain.invoke(local_query)
        return response

    ChatOllama = Langchain_ChatOllama(model_name=LLM)

    Hub_prompt = Langchain_Hub_prompt()

    agent = Langchain_create_agent(ChatOllama, tools, Hub_prompt)

    agent_executor = Langchain_AgentExecutor(agent, tools)

    # Gradio Chat Function
    # This function will be called every time the user sends a message.
    # 'history' will contain the previous messages as a list of [user_message, bot_response] pairs.
    # def chat_with_agent(message: str, history: List[List[str]]) -> str:

# Import your agent and any other necessary libraries
# from your_agent_setup_file import agent_executor # Example import

def clean_agent_response(agent_output_string):
    """
    Cleans the raw output from the LLM agent by removing the <think> block.

    Args:
        agent_output_string (str): The 'output' string from the agent's response dictionary.

    Returns:
        str: The cleaned, human-readable response.
    """
    # Check if the <think> block exists in the output
    if "</think>" in agent_output_string:
        # Split the string at the end of the think block and take the second part
        clean_output = agent_output_string.split("</think>", 1)[1]
    else:
        # If there's no think block, return the original string
        clean_output = agent_output_string

    # Use strip() to remove any leading/trailing whitespace from the final output
    return clean_output.strip()

def chat_with_agent(message, history):
    """
    This function takes a user's message and chat history,
    gets a response from the LangChain agent, extracts the
    clean output, and returns it.
    """
    try:
        # 1. Get the full dictionary response from your agent
        #    (The exact method might be .invoke, .run, .call, etc.)
        agent_response = agent_executor.invoke({"input": message})

        # Extract the 'output' string
        raw_output = agent_response['output']

        # Clean it using the function we created
        clean_output = clean_agent_response(raw_output)

        # Return the clean text to be displayed in Gradio
        return clean_output

    except Exception as e:
        # It's good practice to handle potential errors
        print(f"An error occurred: {e}")
        return "Sorry, I encountered an error while processing your request."

# Create the Gradio ChatInterface
# The `fn` parameter takes your chat function.
# `title` and `description` are optional.
# `theme` can be adjusted for aesthetic preferences (e.g., "soft", "huggingface", "monochrome").
# `live=True` makes the output update as you type, good for streaming (though our current demo doesn't stream).
# `submit_btn` and `stop_btn` can be customized.
# `examples` provide quick input buttons for users.

demo = gr.ChatInterface(
    fn=chat_with_agent,
    type='messages',
    title="Ollama Local LLM Agent Chatbot",
    description="Chat with your local Ollama LLM and AI agents.",
    examples=[
        "What is the current date and time?",
        "What is the weather in London, UK?",
        "Calculate 15 * 3 + 7",
        "Check if you find Dianne Bridgewater in our List of Candidates; if you find her write a document for her convocation in our main office, check the weather in her address if it's good the convocation date is in two days from current date, otherwise the convocation date is Monday of next week from current date"
    ],
    # chatbot=gr.Chatbot(height=400),  # Adjust chatbot display height
    textbox=gr.Textbox(placeholder="Ask your agent a question...", scale=7),  # Input textbox
    theme=gr.themes.Soft(),  # A relatively light and simple theme
    # retry_btn=None, # Remove retry button for simplicity if not needed
    # undo_btn=None, # Remove undo button for simplicity if not needed
)

# Launch the Gradio app
# `share=False` means it won't create a public link (good for local testing).
# `debug=True` provides more verbose output in your terminal.
# `server_name="0.0.0.0"` makes it accessible from other devices on your local network (if firewalls allow).
# `server_port` allows you to specify a port if 7860 is busy.
print(f"\nLittle_Agent_Chatbot Version: {VERSION} <> LLM {LLM}")
demo.launch(share=False, debug=True)



