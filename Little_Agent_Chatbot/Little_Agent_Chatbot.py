"""
Little Agent Chatbot is a simple yet powerful local AI assistant that runs entirely on your machine.
Built for learning and experimentation, it combines the power of open-source LLMs with advanced
retrieval-augmented generation (RAG) to create an intelligent chatbot that can work with your
personal documents and provide real-time information.

Now supports dual provider mode:
  - Local Ollama LLM  (default, no API key needed)
  - Anthropic Claude  (requires ANTHROPIC_API_KEY in .env or --api-key flag)

Updated to LangGraph
"""
VERSION = "0.5.1"

import os
import sys
import argparse
import datetime
import requests

from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
# ─── NEW: LangGraph replaces AgentExecutor + hub + create_tool_calling_agent ───
from langgraph.prebuilt import create_react_agent
# ────────────────────────────────────────────────────────────────────────────────

import gradio as gr
#----------------------------------------------#
# IMPORTANT NOTE:
# uncomment when use SQL mariadb function
#import mariadb


# =================================================================
# CONSTANTS
# =================================================================

CHROMA_PATH   = "chroma_db"
DATA_PATH     = "data/"
PDF_FILENAME  = "Candidates and Scores List - Test Data - compact.pdf"

DEFAULT_OLLAMA_MODEL  = "qwen3:1.7b"
DEFAULT_CLAUDE_MODEL  = "claude-sonnet-4-5"


# =================================================================
# LLM FACTORY
# =================================================================

def get_llm(provider: str, api_key: str = None, model: str = None, temperature: float = 0):
    """
    Return a LangChain chat model based on the chosen provider.

    Providers
    ---------
    "ollama"    — local Ollama (no key needed)
    "anthropic" — Anthropic Claude (requires api_key)
    """
    if provider == "anthropic":
        if not api_key:
            raise ValueError(
                "An Anthropic API key is required for provider='anthropic'.\n"
                "Add ANTHROPIC_API_KEY to your .env file or pass --api-key sk-ant-..."
            )
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError(
                "langchain-anthropic is not installed.\n"
                "Run:  pip install langchain-anthropic"
            )
        resolved_model = model or DEFAULT_CLAUDE_MODEL
        print(f"[LLM Factory] Using Anthropic Claude — model: {resolved_model}")
        return ChatAnthropic(
            model=resolved_model,
            temperature=temperature,
            api_key=api_key
        )

    else:  # default: ollama
        resolved_model = model or DEFAULT_OLLAMA_MODEL
        print(f"[LLM Factory] Using local Ollama — model: {resolved_model}")
        return ChatOllama(model=resolved_model, temperature=temperature)


# =================================================================
# WEATHER FUNCTIONS
# =================================================================

def get_weather_data(api_key, city_name):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_name, "appid": api_key, "units": "metric"}
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
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


def display_weather(weather_data):
    if weather_data:
        city         = weather_data.get("name")
        country      = weather_data.get("sys", {}).get("country")
        main_weather = weather_data.get("weather", [])[0].get("description").capitalize() if weather_data.get("weather") else "N/A"
        temperature  = weather_data.get("main", {}).get("temp")
        feels_like   = weather_data.get("main", {}).get("feels_like")
        humidity     = weather_data.get("main", {}).get("humidity")
        wind_speed   = weather_data.get("wind", {}).get("speed")
        return (
            f"--- Weather in {city}, {country} ---\n"
            f"Description: {main_weather}\n"
            f"Temperature: {temperature}°C\n"
            f"Feels like: {feels_like}°C\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} m/s"
        )
    return "Could not retrieve weather data."


def get_weather_tool(Location):
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        raise ValueError("OpenWeatherMap API key not found. Please set OPENWEATHER_API_KEY in your .env.")
    weather = get_weather_data(api_key, Location)
    return display_weather(weather)


# =================================================================
# CALC FUNCTION
# =================================================================

def get_Calc(OPERATION, NUM_ONE, NUM_TWO):
    try:
        num1_float = float(NUM_ONE)
        num2_float = float(NUM_TWO)
    except ValueError:
        return "Error: NUM_ONE and NUM_TWO must be valid numbers."

    if OPERATION == "ADD":   result = num1_float + num2_float
    elif OPERATION == "SUB": result = num1_float - num2_float
    elif OPERATION == "MUL": result = num1_float * num2_float
    elif OPERATION == "DIV":
        if num2_float == 0:
            return "Error: Division by zero is not allowed."
        result = num1_float / num2_float
    else:
        return "Error: Invalid operation. Please use 'ADD', 'SUB', 'MUL', or 'DIV'."
    return str(result)


# =================================================================
# MARIADB FUNCTIONS
# =================================================================

def query_mariadb(query: str, db_config: dict) -> str:
    conn = None
    try:
        conn = mariadb.connect(**db_config)
        cur  = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        if not rows:
            return "Query executed successfully, but returned no results."
        return "\n".join([", ".join(map(str, row)) for row in rows])
    except mariadb.Error as e:
        print(f"Error connecting to or querying MariaDB: {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()


def Get_SQL(query: str) -> str:
    db_config = {
        'user':     os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host':     '127.0.0.1',
        'port':     3306,
        'database': 'MYSTORE'
    }
    print("\n--- Running Query ---")
    return query_mariadb(query, db_config)


def execute_mariadb(statement: str, db_config: dict) -> str:
    conn = None
    try:
        conn = mariadb.connect(**db_config)
        cur  = conn.cursor()
        cur.execute(statement)
        conn.commit()
        return "Statement executed successfully."
    except mariadb.Error as e:
        if conn:
            conn.rollback()
        print(f"Error executing statement in MariaDB: {e}")
        return f"Error: {e}"
    finally:
        if conn:
            conn.close()


def Update_SQL(statement: str) -> str:
    db_config = {
        'user':     os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host':     '127.0.0.1',
        'port':     3306,
        'database': 'MYSTORE'
    }
    return execute_mariadb(statement, db_config)


# =================================================================
# TOOL DECLARATIONS
# =================================================================

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
    Use this tool whenever the user asks for some data but you don't know anything about it, maybe local document can help you.
    Format the required data as String.
    Example : get_local_data_RAG("when was born Mr. John Smith ?") . You get the birthday of Mr. John Smith.
    """
    try:
        return get_local_document(local_query)
    except Exception as e:
        return f"Error formatting RAG data: {e}"


@tool
def get_arithmetic_operations(Operation: str, Number_1: str, Number_2: str) -> str:
    """
    Returns the result of arithmetic operations, formatted as String.
    Use this tool whenever the user asks for some arithmetic operations, this tool can help you.
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
        return f"Error formatting calc: {e}"


@tool
def get_SQL_response(SQL_statement: str) -> str:
    """
    Returns the result of SQL statement formatted as String.
    Use this tool whenever the user asks for data from his warehouse.
    Format the required data as SQL statement.
    Allowed tables : FRUITS ; VEGGIE
    Allowed items : ITEM, QUANTITY
    Look at the examples below.
    SELECT ITEM, QUANTITY FROM FRUITS
    SELECT ITEM, QUANTITY FROM VEGGIE
    """
    try:
        return Get_SQL(SQL_statement)
    except Exception as e:
        return f"Error formatting SQL: {e}"


@tool
def put_SQL_insert(SQL_statement: str) -> str:
    """
    Update some SQL table.
    Use this tool whenever the user asks to update some data in his warehouse.
    Format the required update as SQL statement.
    Allowed tables : FRUITS ; VEGGIE
    Allowed items : QUANTITY
    Look at the example below.
    UPDATE FRUITS SET QUANTITY=4 WHERE ITEM='ORANGE';
    """
    try:
        return Update_SQL(SQL_statement)
    except Exception as e:
        return f"Error formatting SQL: {e}"


tools = [get_current_datetime, get_weather, get_local_data_RAG,
         get_arithmetic_operations, get_SQL_response, put_SQL_insert]


# =================================================================
# DOCUMENT / RAG HELPERS
# =================================================================

def load_documents_from_PDF_File():
    pdf_path = os.path.join(DATA_PATH, PDF_FILENAME)
    loader   = PyPDFLoader(pdf_path)
    return loader.load()


def split_document_into_smaller_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def Ollama_embeddings(model_name="nomic-embed-text"):
    return OllamaEmbeddings(model=model_name)


def Chroma_vector_database(embedding_function, persist_directory=CHROMA_PATH):
    return Chroma(persist_directory=persist_directory, embedding_function=embedding_function)


def Create_vector_database_Chroma(chunks, embedding_function, persist_directory=CHROMA_PATH):
    return Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=persist_directory
    )


def build_rag_chain(vector_store, llm):
    """Build the RAG chain with an injected LLM instance."""
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={'k': 3})

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


# =================================================================
# AGENT HELPERS  ← updated for LangGraph
# =================================================================

def build_agent(llm, tools):
    """
    Build a LangGraph ReAct agent.
    Replaces:  hub.pull() + create_tool_calling_agent() + AgentExecutor()
    """
    return create_react_agent(llm, tools)


def run_agent(executor, user_input):
    """Invoke the agent and print its final answer."""
    print("\nInvoking agent...")
    print(f"Input: {user_input}")
    # LangGraph returns {"messages": [...]};  last message is the AI reply
    response     = executor.invoke({"messages": [("human", user_input)]})
    final_answer = response["messages"][-1].content
    print("\nAgent Response:")
    print(final_answer)


# =================================================================
# GRADIO HELPERS
# =================================================================

def clean_agent_response(agent_output_string):
    if "</think>" in agent_output_string:
        clean_output = agent_output_string.split("</think>", 1)[1]
    else:
        clean_output = agent_output_string
    return clean_output.strip()


def chat_with_agent(message, history):
    try:
        # LangGraph invocation — pass message inside "messages" key
        response     = agent_executor.invoke({"messages": [("human", message)]})
        raw_output   = response["messages"][-1].content
        return clean_agent_response(raw_output)
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, I encountered an error while processing your request."


# =================================================================
# CLI ARGUMENT PARSING
# =================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="Little Agent Chatbot — dual provider (Ollama / Claude)",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "mode",
        choices=["graph", "text"],
        help="Interface mode:\n  graph — Gradio web UI\n  text  — terminal chat"
    )
    parser.add_argument(
        "--provider",
        choices=["ollama", "anthropic"],
        default="ollama",
        help=(
            "LLM provider to use:\n"
            "  ollama    — local Ollama model (default, no key needed)\n"
            "  anthropic — Anthropic Claude   (requires --api-key or ANTHROPIC_API_KEY in .env)\n"
        )
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key for Anthropic (overrides ANTHROPIC_API_KEY env var)."
    )
    parser.add_argument(
        "--model",
        default=None,
        help=(
            f"Model name override.\n"
            f"  Ollama default    : {DEFAULT_OLLAMA_MODEL}\n"
            f"  Anthropic default : {DEFAULT_CLAUDE_MODEL}\n"
        )
    )

    return parser.parse_args()


# =================================================================
# MAIN
# =================================================================

if __name__ == "__main__":

    args = parse_args()

    # Resolve API key: CLI flag > .env / environment variable
    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")

    # Resolve display model name for the banner
    if args.provider == "anthropic":
        display_model = args.model or DEFAULT_CLAUDE_MODEL
    else:
        display_model = args.model or DEFAULT_OLLAMA_MODEL

    # ── Build the shared LLM ──────────────────────────────────────
    llm = get_llm(provider=args.provider, api_key=api_key, model=args.model, temperature=0)

    # ── Load & index documents ────────────────────────────────────
    documents          = load_documents_from_PDF_File()
    chunks             = split_document_into_smaller_chunks(documents)
    embedding_function = Ollama_embeddings()

    vector_database = Create_vector_database_Chroma(chunks, embedding_function)
    # To avoid re-indexing each run, comment the line above and use:
    ###vector_database = Chroma_vector_database(embedding_function)

    # ── Build RAG chain with the shared LLM ──────────────────────
    rag_chain = build_rag_chain(vector_database, llm=llm)

    # Global wrapper called by the @tool decorator
    _global_rag_chain = rag_chain
    def get_local_document(local_query):
        print(f"\nQuerying RAG chain with: {local_query}")
        return _global_rag_chain.invoke(local_query)

    # ── Build LangGraph agent ─────────────────────────────────────
    agent_executor = build_agent(llm, tools)

    # ── Banner ────────────────────────────────────────────────────
    print(f"\n{'=' * 55}")
    print(f"  Little Agent Chatbot  —  v{VERSION}")
    print(f"  Provider : {args.provider.upper()}")
    print(f"  Model    : {display_model}")
    print(f"  Mode     : {args.mode.upper()}")
    print(f"{'=' * 55}\n")
    print("Example questions:")
    print("  What's the weather in Sydney now?")
    print("  Is Dianne in our local list of Candidates?")
    print("  Do we have orange in our warehouse?")
    # ── Launch ────────────────────────────────────────────────────
    if args.mode == "graph":
        demo = gr.ChatInterface(
            fn=chat_with_agent,
            title="Little Agent Chatbot",
            description="Chat with your AI agent. Supports weather, arithmetic, SQL warehouse queries, and local document search.",
            examples=[
                "What is the current date and time?",
                "What is the weather in London, UK?",
                "Calculate 15 * 3 + 7",
                "Check if you find Dianne Bridgewater in our List of Candidates; if you find her write a document for her convocation in our main office, check the weather in her address if it's good the convocation date is in two days from current date, otherwise the convocation date is Monday of next week from current date",
                "Do we have orange in our warehouse?",
                "Please increase by 2 apples quantity in our warehouse"
            ],
            textbox=gr.Textbox(placeholder="Ask your agent a question...", scale=7),
        )
        demo.launch(share=False, debug=True)

    elif args.mode == "text":
        print("Type your question and press Enter. Type 'exit' or 'quit' to end the chat.")
        print("-" * 50)
        while True:
            try:
                user_input = input("You: ")
                if user_input.lower() in ["exit", "quit"]:
                    print("\nExiting chat. Goodbye!")
                    break
                run_agent(agent_executor, user_input)
            except (KeyboardInterrupt, EOFError):
                print("\n\nExiting chat. Goodbye!")
                break
