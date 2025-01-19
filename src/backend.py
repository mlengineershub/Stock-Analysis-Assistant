import finnhub  # type: ignore
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.tools import BaseTool
from typing import Any, Dict, Union, Annotated, Type
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

vectordb = Chroma(persist_directory="data/vdb", embedding_function=OllamaEmbeddings(model="granite-embedding"))
retriever = vectordb.as_retriever()

#==========================Retrieval Grader Agent==========================

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


# Data model
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


# LLM with function call
llm = ChatOllama(model="llama3.2:latest")

structured_llm_grader = llm.with_structured_output(GradeDocuments)

# Prompt
system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
    It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
    ]
)

retrieval_grader = grade_prompt | structured_llm_grader
#==========================Retrieval Generator Agent==========================
# Prompt
prompt = hub.pull("rlm/rag-prompt")



# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Chain
retrieval_chain = prompt | llm | StrOutputParser()

#==========================Finance Tool==========================
FINANCE_API_KEY='cte32t9r01qt478kvedgcte32t9r01qt478kvee0'
# Setup client
finnhub_client = finnhub.Client(api_key=FINANCE_API_KEY)

class FinanceNewsInput(BaseModel):
    """Input for finance news tool."""
    company: str = Field(description="Company ticker symbol")
    start_date: str = Field(description="Start date in YYYY-MM-DD format")
    end_date: str = Field(description="End date in YYYY-MM-DD format")

class FinanceNewsTool(BaseTool):
    # Add type annotations here
    name: str = "get_finance_news"
    description: str = "A tool that fetches finance news from the Finnhub API"
    args_schema: Type[BaseModel] = FinanceNewsInput

    def _run(self, *, company: str, start_date: str, end_date: str) -> str:
        """Implementation of finance news fetching."""
        response = finnhub_client.company_news(company, _from=start_date, to=end_date)
        if not response:
            return "No news available for the specified period."
        return response[0]["summary"]

finance_news_tool = FinanceNewsTool(
    name="get_finance_news",
    description="A tool that fetches finance news from the Finnhub API"
)

#==========================Recommander Agent==========================
recommander_prompt_template = ChatPromptTemplate.from_template("""
You are a recommender system that suggests the best investement move to do based on the latest news of a company.
The goal is to provide a recommendation based on the latest news of the company.
The recommendation should be based on the latest news of the company.
News: {news}
Recommendation: """)

recommander_chain = recommander_prompt_template | llm | StrOutputParser()
#=================================================================================



class State(TypedDict):
    user_question: str
    messages: Annotated[list, add_messages]
    docs: list
    relevant: bool
    news: str


graph_builder = StateGraph(State)


llm = ChatOllama(model="llama3.2:latest")
tools = [finance_news_tool]
llm_with_tools = llm.bind_tools(tools)


def rag_chain_node(state: State):
    # call the retrieval chain
    docs = retriever.get_relevant_documents(state["user_question"])
    generation = retrieval_chain.invoke({"context": format_docs(docs), "question": state["user_question"]})
    return {"messages": [generation], "docs": docs}
    
def grader_node(state: State) -> Dict[str, Any]:
    result = retrieval_grader.invoke({"question": state["user_question"], "document": format_docs(state["docs"])})
    # Handle both possible return types
    grade_result: Union[Dict[Any, Any], GradeDocuments] = result
    if isinstance(grade_result, dict):
        is_relevant = grade_result.get("binary_score", "no") == "yes"
    else:
        is_relevant = grade_result.binary_score == "yes"
    return {"relevant": is_relevant}

def is_relevant(state: State):
    if state["relevant"]:
        return "recommendation"
    else:
        return "search"

def search_node(state: State):
    # Extract company name from question using LLM
    company_prompt = ChatPromptTemplate.from_template(
        "Extract the company name from this question: {question}. Return only the company ticker symbol (e.g., AAPL, MSFT, etc.)"
    )
    company_chain = company_prompt | llm | StrOutputParser()
    company = company_chain.invoke({"question": state["user_question"]})
    
    # Get today's date and 7 days ago for news search
    from datetime import datetime, timedelta
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Get finance news using the tool's run method directly
    news = finance_news_tool._run(
        company=company,
        start_date=start_date,
        end_date=end_date
    )
    return {"news": news}

def recommendation_node(state: State):
    # Use either RAG results or news search results
    if state["relevant"]:
        context = state["messages"][-1]
    else:
        context = state["news"]
    
    recommendation = recommander_chain.invoke({"news": context})
    return {"messages": [recommendation]}

# Add nodes
graph_builder.add_node("rag", rag_chain_node)
graph_builder.add_node("grader", grader_node)
graph_builder.add_node("search", search_node)
graph_builder.add_node("recommendation", recommendation_node)

# Add conditional edges
graph_builder.add_conditional_edges(
    "grader",
    is_relevant,
    {
        "recommendation": "recommendation",
        "search": "search"
    }
)

# Add edges
graph_builder.set_entry_point("rag")
graph_builder.add_edge("rag", "grader")
graph_builder.add_edge("search", "recommendation")
graph_builder.add_edge("recommendation", END)

# Compile graph
graph = graph_builder.compile()

def process_query(query: str, debug: bool = False):
    """Process a user query through the graph.
    
    Args:
        query (str): The user's question
        debug (bool, optional): If True, prints detailed debug information. Defaults to False.
    """
    result = graph.invoke({
        "user_question": query,
        "messages": [],
        "docs": [],
        "relevant": False,
        "news": ""
    })
    
    if debug:
        print("=== Debug Information ===")
        print(f"User Question: {query}")
        print("\nFull State Stack:")
        for key, value in result.items():
            print(f"\n{key}:")
            print(value)
        print("\nFinal Recommendation:")
        print(result["messages"][-1])
        print("=======================")
        
    return result["messages"][-1]