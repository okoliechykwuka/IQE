# app.py
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import openai
import streamlit as st
from io import BytesIO
from markdown_pdf import MarkdownPdf, Section
import os
from utils.processors import PDFProcessor, VideoProcessor, AudioProcessor, DummyProcessor
from utils.evaluator import DesignEvaluator, TransferEvaluator, PerformanceEvaluator, load_chromadb
from utils.workflow import summarizer, workflow_builder, evaluation_summarizer
from assets.prompts import SYSTEM_PROMPT, DESIGN_BASE_PROMPT, TRANSFER_BASE_PROMPT, PERFORMANCE_BASE_PROMPT
from assets.evalresources import transfer_resources, design_resources, performance_resources

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
st.session_state['report_status']  = False


import uuid

def generate_unique_id():
    """
    Generates a unique ID using UUID4.
    
    Returns:
        str: A unique ID in string format.
    """
    return str(uuid.uuid4())


if not 'thread_id' in st.session_state:
    st.session_state['thread_id'] = generate_unique_id()
# Configure a user thread
config = {'configurable':{'thread_id':st.session_state['thread_id']}}
graph = workflow_builder()
# st.session_state['content_summary'] = None
class CourseEvaluatorApp:
    def __init__(self):
        self.setup_streamlit()
        self.initialize_processors()
        
        
    def setup_streamlit(self):
        st.set_page_config(
            page_title="Instructional Quality Prototype", 
            layout="centered"
        )
        
    def initialize_processors(self):
        self.pdf_processor = PDFProcessor()
        self.video_processor = VideoProcessor()
        self.audio_processor = AudioProcessor()
        self.dummy_processor = DummyProcessor()


        
    def process_file(self, file):
        file_name = file.name
        file_ext = os.path.splitext(file_name)[-1].lower()
        if file_ext == ".pdf":
            st.write("PDF File detected")
            content = self.pdf_processor.process(file)
        elif file_ext in [".mp3", ".wav"]:
            st.write("Audio deteted")
            content = self.audio_processor.process(file)
        else:
            st.error("Unsupported file type")
            content = self.dummy_processor.process(file)

        return content
    
    def router(self, state):
        message = state['messages'][-1]
        if hasattr(message, 'tool_calls') and len(message.tool_calls) > 0:
            available_tools = ['gen_scope', 'design_frameworks', 'transer_work_frameworks', 'perform_man_frameworks', 
                               'synthesize_evalaution_summary', 'generate_downloadable_report', 'request_content']
            outbound_msgs = []
            for tool_call in message.tool_calls:
                if tool_call['name'] not in available_tools:
                    raise ValueError(f"Model Called a Tool {tool_call['name']} That is not implement")
                
                if tool_call['name'] == 'design_frameworks':
                    design = st.session_state['design_evaluator']
                    ## Call the preliminary review chain
                    with st.spinner("Evaluating Design Frameworks"):
                        critique = tool_call['args']
                        design.set_critique(**critique)
                        design_eval = design.eval_design()

                        outbound_msgs.append(ToolMessage(
                            content= str(design_eval),
                            name=tool_call['name'],
                            tool_call_id=tool_call['id']
                        ))

                elif tool_call['name'] == 'transer_work_frameworks':
                    transfer = st.session_state['transfer_evaluator']
                    with st.spinner("Evaluating Transfer Frameworks"):
                        
                        critique = tool_call['args']
                        transfer.set_critique(**critique)
                        tranaser_eval = transfer.eval_transfer() 
                        outbound_msgs.append(ToolMessage(
                            content= str(tranaser_eval), 
                            name=tool_call['name'],
                            tool_call_id=tool_call['id']
                        ))
                 
                elif tool_call['name'] == 'perform_man_frameworks':
                    performance = st.session_state['performance_evaluator']
                    with st.spinner("Evaluation Perform Man Frameworks"):
                        critique = tool_call['args']
                        performance.set_critique(**critique)
                        performance_eval = performance.eval_performance() 
                        outbound_msgs.append(ToolMessage(
                            content= str(performance_eval), 
                            name=tool_call['name'],
                            tool_call_id=tool_call['id']
                        ))

                elif tool_call['name'] == 'synthesize_evalaution_summary':
                    print("Running summary TOOL")
                    with st.spinner("Running Evaluation Summary Synthesizer"):
                        eval_summary = evaluation_summarizer(state)
                        # st.markdown(eval_summary['summary'])
                        outbound_msgs.append(ToolMessage(
                            content=eval_summary['summary'],
                            name=tool_call['name'],
                            tool_call_id=tool_call['id']
                        ))

                elif tool_call['name'] == 'generate_downloadable_report':
                    print("Generating Report")
                    report_statements = tool_call['args']
                    st.session_state['report_status']  = True
                    report = self.save_to_pdf(**report_statements)
                    st.session_state['report'] = report
                    message = f"report saved"
                    
                    outbound_msgs.append(ToolMessage(
                         content=message,
                         name=tool_call['name'],
                         tool_call_id=tool_call['id']
                    ))

                elif tool_call['name'] == 'gen_scope':
                    print("Generating Scope")
                    # st.session_state["content_summary"] = None
                    additions = tool_call['args']['info']
                    summary = summarizer(st.session_state.get('content',''))

                    st.session_state["content_summary"] = summary
                    outbound_msgs.append(ToolMessage(
                         content=summary['summary'],
                         name=tool_call['name'],
                         tool_call_id=tool_call['id']
                    ))

                elif tool_call['name'] == 'request_content':
                    outbound_msgs.append(ToolMessage(
                         content="Uploaded",
                         name=tool_call['name'],
                         tool_call_id=tool_call['id']
                    ))

                else:
                    message = "No result found. Invalid tool  or tool not implemented"
                    outbound_msgs.append(ToolMessage(
                        content=message,
                        name=tool_call['name'],
                        tool_call_id=tool_call['id']

                    ))
            return outbound_msgs
        else:
            return False
    
    def save_to_pdf(self, report_statements):
        """
        Save raw string content to a PDF file.

        Args:
            text (str): The string content to save to the PDF.
            filename (str): The name of the output PDF file (e.g., 'report.pdf').

        Returns:
            bool
        """

        pdf = MarkdownPdf(toc_level=1)
        pdf.add_section(Section(report_statements))
        # Use an in-memory buffer
        pdf_buffer = BytesIO()
        pdf_buffer.seek(0)
        pdf.save(pdf_buffer)
        # st.download_button("Download Evaluation PDF", data=pdf_buffer, file_name="Evaluation_Summary_Report.pdf", mime="application/pdf")

        return pdf_buffer
    
    # Sidebar: File Upload
    def main(self):
        st.sidebar.title("Upload Your Course Materials")
        uploaded_file = st.sidebar.file_uploader("Upload your course materials:", type=["pdf", "mp3", "mp4"])
        youtube_url = st.sidebar.text_input("Or provide a YouTube URL")

        # Sidebar: Instructions
        st.sidebar.title("Instructions")
        st.sidebar.markdown(
            """
            ### How to Use:
            1. **Attach Course Files**: 
            - Upload the course files you want evaluated (PDFs, YouTube links, or audio files).
            - If you provided a YouTube link , click Enter to apply
            2. **Summary and Confirmation**: 
                - I will verify the course structure and categories, and confirm the level of critique you prefer.
            3. **Critque Level**
                - Provide a critique level: (0 - 10)
            4. **Evaluation Frameworks**: 
               - I will evaluate your course using various proven frameworks.
            5. **Summarized Results**: 
              - At the end, you will receive a summary with ratings and actionable insights.
            6. ** Suggestions**:
              - Based on the evaluation, I will provide actionable insights and suggestions
            7. **Downlaodable Report**:
              - You can download the report for further analysis or sharing.
            
            **Note**: The system may ocassionally jump a step, if you need to go through that step, you can remind the model to go back to the step
            """
        )
        # Custom CSS to modify sidebar and page layout
        st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                background-color: #f0f2f6;
                width: 250px;
            }
            .main-title {
                text-align: center;
                font-size: 2.5em;
                color: #2c3e50;
                margin-bottom: 30px;
            }
            </style>
        """, unsafe_allow_html=True)

        # Title at the top of the page
        st.markdown('<h1 class="main-title">Instructional Quality Prototype (IQA)</h1>', unsafe_allow_html=True)

        if "content_summary" not in st.session_state:
            st.markdown(
                """
                Welcome to the Instructional Quality Prototype.  I am your virtual IQP guide or co-researcher and I’ll be walking you through a variety of steps to evaluate your course.  
                This process includes a number of  steps. I will keep you informed along the way. You can ask me to repeat a step.
                You can also guide me and build on my ideas, with me or separately. You are in the driver’s seat; I am just your tool. 
                """
            )

        else:
            with st.columns(1)[0]:
                st.markdown(
                """
               

                """
            )


        # Step 3.1: Confirmation Page
        if 'content' not in st.session_state:
            if uploaded_file:
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                content = self.process_file(uploaded_file)

            elif youtube_url:
                if "youtube.com" not in youtube_url and "youtu.be" not in youtube_url:
                    st.error("Invalid YouTube URL. Please provide a valid link.")
                else:
                    with st.spinner("Extracting transcript from YouTube..."):
                        content = self.video_processor.process(youtube_url)
                        st.success("YouTube content successfully extracted!")
            else:
                st.sidebar.info("Please upload your course materials here or Provide a YouTube link to your course")
                st.stop()
        
            st.session_state['content'] = content

            if len(st.session_state['content']['raw_text']) >= 900000:
                st.warning("Content is Large for system to process")
        else:
            if not uploaded_file:
                del st.session_state['content']


        if 'design_evaluator' not in st.session_state:
            with st.spinner("Building Evaluator Models"):
                design = DesignEvaluator(collection_name='design_framework', db_path="./db", prompt=DESIGN_BASE_PROMPT, content=content)
                st.session_state['design_evaluator'] = design
        if 'performance_evaluator' not in st.session_state:
            st.session_state['performance_evaluator'] = PerformanceEvaluator(collection_name='performance_framework', db_path="./db", prompt=PERFORMANCE_BASE_PROMPT, content=content)

        if 'transfer_evaluator' not in st.session_state:
            st.session_state['transfer_evaluator'] = TransferEvaluator(collection_name='transfer_framework', db_path="./db", prompt=TRANSFER_BASE_PROMPT, content=content)
            

        if "content_summary" in st.session_state:
            # print("GOT HERE")
            st.subheader("Extracted Content Summary")
               
        else:
            
            with st.spinner("Detecting Content Scope"):
                summary = summarizer(st.session_state['content'])
                st.session_state["content_summary"] = summary
                st.subheader("Extracted Content Summary")
                

                ## Make the agent aware of the summary
                snapshot = graph.get_state(config)
                
                if 'messages' not in snapshot.values:
                    snapshot.values['messages'] = []
                    snapshot.values['messages'].append((SystemMessage(content=SYSTEM_PROMPT)))
                    snapshot.values['messages'].append((AIMessage(content=summary['summary'])))
                    # Update the graph state
                    new_messages =  snapshot.values
                    graph.update_state(config, new_messages)

        snapshot = graph.get_state(config)
        # st.write(snapshot)
        
       
        for message in snapshot.values['messages']:
            if isinstance(message, HumanMessage):
                st.chat_message('human').write(message.content)
            elif isinstance(message, AIMessage):
                st.chat_message('ai').write(message.content)

        
        if user_input:= st.chat_input():
            st.chat_message('human').write(user_input)
           
            res = graph.invoke({'messages':[user_input]}, config)
            
            st.chat_message('ai').write(res['messages'][-1].content)
            
            while True:
                snapshot = graph.get_state(config)
                pre_result = self.router(snapshot.values)
                if pre_result:
                    snapshot.values['messages'] += pre_result
                    updated_state = snapshot.values
                    graph.update_state(config, updated_state)
                    res = graph.invoke({'proceed':True}, config)
                    # eval_summary = list(filter(lambda msg: msg.name == 'synthesize_evalaution_summary', snapshot.values['messages']))

                    # if st.session_state['report_status'] and eval_summary:
                    #     eval_content = eval_summary[0].content
                    #     st.chat_message('ai').write(eval_content)
                    # else:
                    st.chat_message('ai').write(res['messages'][-1].content)
                
                else:
                    break
        if st.session_state['report_status']:
            # snapshot = graph.get_state(config)
            try:
                content = list(filter(lambda msg: msg.name == 'synthesize_evalaution_summary', snapshot.values['messages']))[0].content
                report_buffer = self.save_to_pdf(content)
                st.download_button("Download Evaluation PDF", data=report_buffer, file_name="Evaluation_Summary_Report.pdf", mime="application/pdf")
            except IndexError:
                st.download_button("Download Evaluation PDF", data=st.session_state['report'], file_name="Evaluation_Summary_Report.pdf", mime="application/pdf")
            st.session_state['report_status']  = False

                
if __name__ == "__main__":
    app = CourseEvaluatorApp()
    if not (os.path.exists("./IQE/db/chroma.sqlite3") or os.path.exists("./db/chroma.sqlite3")):
        print("Setting Evaluation Knowledge Base")
        load_chromadb(collection_name="design_framework", db_path="./db", resources=design_resources)
        load_chromadb(collection_name="transfer_framework", db_path="./db", resources=transfer_resources)
        load_chromadb(collection_name="performance_framework", db_path="./db", resources=performance_resources)
    else:
        print("Knowledge Base Detected")
    # app.setup_streamlit()
    try:
        app.main()
    except openai.BadRequestError as err:
        if err.status_code == 400:
            st.error("Oops! System Could not process the content\n The content you provided is too large or the model ran out memory space")
