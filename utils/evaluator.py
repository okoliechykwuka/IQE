# evaluator.py


from langchain_core.tools import tool
from assets.prompts import (dick_specific_prompt, shackilton_specific_prompt, sam_specific_prompt, arches_specific_prompt, 
                     wiggins_specific_prompt, action_specific_prompt, decisive_specific_prompt,
                     addie_specific_prompt, behavior_specific_prompt, mager_specific_prompt,
                     CRITIQUE_PROMPT)

from typing import List
from abc import abstractmethod, ABC
import streamlit as st
import os
from pathlib import Path
from llama_index.core import (
    VectorStoreIndex,  PromptTemplate as LLamaPromptTemplate, SimpleDirectoryReader)
from llama_index.core import PromptHelper
from utils.utility import get_relative_path

# def load_chromadb(collection_name: str, db_path:str, resources: List[str]):
#     chromadb_config = ChromaDbConfig(collection_name=collection_name, dir=db_path, host='localhost')
#     chromadb = ChromaDB(config=chromadb_config)
#     app = App(db=chromadb)
#     for resource in resources:
#         app.add(resource)
#     print("loaded")


framework = 'design'
class Evaluator(ABC):
    def __init__(self,prompt, sprompt, content, framework_name):

        prompt_helper = PromptHelper(
        context_window=120000,  # Adjust based on your model's context window
        num_output=256,
        chunk_overlap_ratio=0.1,
        chunk_size_limit=None
)
        self.framework_name = framework_name
        self.base_prompt = prompt
        self.sliding_prompt = sprompt
        # self.partial_evaluations = []
        self.final_evaluation = None
        data_path = get_relative_path(f"data/{framework_name}")
        self.content = content
        if not Path(data_path).exists():
            raise ValueError("Resources Not Found")
        
        documents = SimpleDirectoryReader(data_path).load_data()
        index = VectorStoreIndex.from_documents(documents,  prompt_helper=prompt_helper)
        self.app = index.as_query_engine(response_mode='compact')

            
    # @abstractmethod
    def set_critique(self, N=5):
        self.N = N
    # @abstractmethod
    # def evaluate_sliding(self, content):
    #     pass

    def sliding_window(self, content):
        if content['content_type'] == 'pdf':
            page_count=10
            text = content['raw_text']
            # Split the text into paragraphs
            paragraphs = text.strip().split('<p>')[1:]
            total_paragraphs = len(paragraphs)
            
        else:
            page_count = 20
            text = content['raw_text']
            # Split the transcript into different timestamps
            paragraphs = text.strip().split('<timestamp:')[1:]
            total_paragraphs = len(paragraphs)

        # Calculate stride dynamically to maintain one-paragraph overlap
        stride = page_count - 1
        
        for i in range(0, total_paragraphs, stride):
            # Create chunks with minimal overlap
            yield '\n\n'.join(paragraphs[i:i + page_count])
            
            # Break if we reach the end to avoid unnecessary small chunks
            if i + page_count >= total_paragraphs:
                break

    def evaluate_sliding(self, model_name):
        context_summary = ""
        for chunk in self.sliding_window(self.content):
            content_eval_tmpl_str = LLamaPromptTemplate(self.sliding_prompt).partial_format(content=chunk, N=self.N, previous_summary=context_summary)
            self.app.update_prompts(
                {"response_synthesizer:refine_template": content_eval_tmpl_str, 'response_synthesizer:text_qa_template':content_eval_tmpl_str}
            )
            context_summary = self.app.query(model_name)
        # all_sum.append(context_summary)
        return context_summary





class DesignEvaluator(Evaluator):
    def __init__(self, prompt, sprompt, content):
        super().__init__(prompt, sprompt, content, framework_name='design')

    
    def set_critique(self, critique_level):
        self.N = critique_level 
    
    def eval_dick(self):
        """Evaluates the content with the Dick and Carey Instructional Design Model"""
        
        name: str = "Dick and Carey Instructional Design Model"
        evaluation_result = self.app.query(name)
        return evaluation_result
        
    
    def eval_sam(self):
        """Evaluates the content with the SAM (Successive Approximation Model)"""
        
        name: str = "SAM (Successive Approximation Model)"
        
        evaluation_result = self.app.query(name)
        return evaluation_result

    def eval_shackilton(self):
        """Evaluates the content with the Shackleton 5Di Model (Nick Shackleton)"""

        name: str = "Shackilton 5Di Model"
        
        evaluation_result = self.app.query(name)
        return evaluation_result

    def eval_arches(self):
        """Evaluates the content with the Learning Arches and Learning Spaces (Kaospilot)""" 
        
        name: str = "Learning Arches and Learning Spaces (Kaospilot)"

        evaluation_result = self.app.query(name)
        return evaluation_result 
    

    def eval_design(self, slide=False):

        if slide:
            return {'Dick': self.evaluate_sliding("Dick and Carey Instructional Design Model"),
                'SAM': self.evaluate_sliding("SAM (Successive Approximation Model)"),
                'Shackilton': self.evaluate_sliding("Shackilton 5Di Model"),
                'Arches': self.evaluate_sliding("Learning Arches and Learning Spaces (Kaospilot)")
                }
        else:
            content_eval_tmpl_str = LLamaPromptTemplate(self.base_prompt).partial_format(content=self.content, N=self.N)
            self.app.update_prompts(
                    {"response_synthesizer:refine_template": content_eval_tmpl_str, 'response_synthesizer:text_qa_template':content_eval_tmpl_str}
                )
            return {'Dick': self.eval_dick(),
                    'SAM': self.eval_sam(),
                    'Shackilton': self.eval_shackilton(),
                    'Arches': self.eval_arches()
                    }
    
    def evaluate_sliding(self, model_name):
        return super().evaluate_sliding(model_name)


class TransferEvaluator(Evaluator):
    def __init__(self, prompt, sprompt, content):
        super().__init__(prompt, sprompt, content, framework_name='transfer')

    
    def set_critique(self, critique_level):
        self.N = critique_level 
    

    def eval_action(self):
        """Evaluates the content with the Action Mapping (Cathy Moore)"""
        
        name: str = "Action Mapping (Cathy Moore)"
        
        evaluation_result = self.app.query(name)
        return evaluation_result
        
    
    def eval_decisive(self):
        """Evaluates the content with the The Decisive Dozen (Dr. Will Thalheimer, PhD)"""
        
        name: str = "The Decisive Dozen (Dr. Will Thalheimer, PhD)"

        evaluation_result = self.app.query(name)
        return evaluation_result

    def eval_wiggins(self):
        """Evaluates the content with the Wiggins and McTighe Backwards Design Model (UbD)"""

        name: str = "Wiggins and McTighe Backwards Design Model (UbD)"
        
        evaluation_result = self.app.query(name)
        return evaluation_result

    
    def eval_transfer(self, slide=False):
        if slide:
            return {'Action': self.evaluate_sliding("Action Mapping (Cathy Moore)"),
                'Decisive': self.evaluate_sliding("The Decisive Dozen (Dr. Will Thalheimer, PhD)"),
                'Wiggins': self.evaluate_sliding("Wiggins and McTighe Backwards Design Model (UbD)"),
                }
        
        return {'Action': self.eval_action(),
                'Decisive': self.eval_decisive(),
                'Wiggins': self.eval_wiggins()
                }
    
    def evaluate_sliding(self, model_name):
        return super().evaluate_sliding(model_name)
        
        
    
class PerformanceEvaluator(Evaluator):
    def __init__(self, prompt, sprompt, content):
        super().__init__(prompt, sprompt, content, framework_name='performance')

    
    def set_critique(self, critique_level):
        self.N = critique_level 

    def eval_addie(self):
        """Evaluates the content with the ADDIE Model"""

        name: str = "ADDIE Model"
        
        evaluation_result = self.app.query(name)
        return evaluation_result
        
    
    def eval_behavior(self):
        """Evaluates the content with the Behavior Engineering Model"""
        
        name: str = "Behavior Engineering Model"

        evaluation_result = self.app.query(name)
        return evaluation_result

    def eval_mager(self):
        """Evaluates the content with the  Mager and Pipe Model"""

        name: str = "Mager and Pipe Model"
        
        evaluation_result = self.app.query(name)
        return evaluation_result

    
    def eval_performance(self, slide=False):

        if slide:
            return {'Mager': self.evaluate_sliding("Mager and Pipe Model"),
                'Behaviour': self.evaluate_sliding("Behavior Engineering Model"),
                'Addie': self.evaluate_sliding("ADDIE Model"),
                 }
        
        return {'Addie': self.eval_addie(),
                'Behavior': self.eval_behavior(),
                'Mager': self.eval_mager()
                }
    
    def evaluate_sliding(self, model_name):
        return super().evaluate_sliding(model_name)
    
# Define all tool place holders

class Tools():
    @tool
    def request_content():
        """Use this to take and validate content from the user"""
    @tool
    def gen_scope(info: str):
        """Use this tool whenever you want to generated the content summary and scope or when you need to refine the summary,
        This tool is able to fetch the original content, so it is more suitable to be used for generating the summary of the learning content. The input to this tool is text to use to shift the focus of the summary."""

    @tool
    def design_frameworks(critique_level: int):
        """Use this tool to carry out evalutation using the DESIGN Frameworks. Input to this tool is the critique level"""

    @tool
    def transer_work_frameworks(critique_level: int):
        """Use this tool to carry out evaluation using the TRANSFER/ WORK Frameworks. Input to this tool is the critique level"""

    @tool
    def perform_man_frameworks(critique_level: int):
        """Use this tool to carry out evaluation using the PERFORM/ MAN Frameworks. Input to this tool is the critique level"""
    @tool
    def synthesize_evalaution_summary():
        """Use this tool to carry out Step 5.1, the final summary synthesis of the content evaluations. The tool aggregates content evaluations across the various instructional design frameworks, summarizing scores for key dimensions and models."""

    @tool
    def generate_downloadable_report(report_statements: str):
        """Use this tool to generate the the final evaluation report which the user an download. The input to this tool is a well formated report statements that should be on the report document. This can be extracts from the evaluation summary."""

    