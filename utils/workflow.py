# workflow.py

import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from dotenv import load_dotenv, find_dotenv
from langchain.prompts import PromptTemplate
from typing import Annotated, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from typing import Dict, Any, Annotated
from assets.prompts import SYSTEM_PROMPT, SUMMARY_SYNTHESIS_PROMPT
from utils.evaluator import Tools


load_dotenv(find_dotenv())

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# Define all the chains

def summarizer(content, modifiers=""):
    """Generate comprehensive content summary"""
    additions = f"Additional information from the user: {modifiers}"
    content_text, content_type = content['raw_text'], content['content_type']
    prompt = """System Prompt:
        You are an expert instructional designer analyzing course content.
        Provide a comprehensive summary highlighting:

        Content Summary and Scope Confirmation
        [ Your response summary: Main focus, audience, thesis, Estimated learning duration]​

        Goals / Objectives Summary
        [summary in bullets]

        Summary of Structure
        [summary of main components in bullets]

         
        - Present the summary to the user for confirmation.
        Ask the users some follow up questions like:
        Follow-Up Questions:
            - Did I reasonably capture the intention and goal of your course?
            - Are there specific areas of Instructional Quality you feel I should focus on?
            - Are there any changes you could envision (add, remove, modify…) that could incorporate into my evaluation and response?
        - If the user provides feedback or requests adjustments, refine the summary accordingly.'
         
         Content Type: {content_type}
         Content: "{content}
         """  + (additions if modifiers else "")
    summary_prompt = PromptTemplate.from_template(prompt)
        
    summary_prompt = summary_prompt.partial(content_type=content_type)
    chain = summary_prompt | llm
    summary = chain.invoke(content_text)
    return {'summary': summary.content}



def evaluation_summarizer(state):
    messages = state['messages']
    summary_llm  = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    summary_prompt = PromptTemplate.from_template(SUMMARY_SYNTHESIS_PROMPT)
    summary_chain = summary_prompt | summary_llm
    eval_summary = summary_chain.invoke(messages)
    
    return {"summary":eval_summary.content}






path = "memory.sqlite"

memconn = sqlite3.connect(path, check_same_thread=False)

tools = [Tools.gen_scope, Tools.design_frameworks, Tools.perform_man_frameworks, 
         Tools.transer_work_frameworks, Tools.synthesize_evalaution_summary, Tools.generate_downloadable_report, Tools.request_content]

model = llm.bind_tools(tools)

class CourseEvaluationState(TypedDict):
    messages: Annotated[list, add_messages]
    proceed: bool
    content: Dict[str, Any] 
    content_type: str = ""
    summary: str = ""
    
def agent(state: CourseEvaluationState):
    if isinstance(
            state["messages"][0], SystemMessage
        ):
            pass
    else:
        state["messages"].insert(0, SystemMessage(content=SYSTEM_PROMPT))

    # print("invoking the model")
    res = model.invoke(input=state["messages"])
    return state | {"messages": [res]}

memory = SqliteSaver(memconn)
# memory = MemorySaver()

def workflow_builder():
    graph_builder = StateGraph(CourseEvaluationState)
    graph_builder.add_node('agent', agent)
    graph_builder.add_edge(START, 'agent')
    graph_builder.add_edge('agent', END)
    graph = graph_builder.compile(checkpointer=memory)
    return graph



# define the evaluations

