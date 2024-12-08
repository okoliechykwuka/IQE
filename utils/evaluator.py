# evaluator.py


from embedchain import App
from embedchain.config import BaseLlmConfig
from embedchain.llm.openai import OpenAILlm
from embedchain.config import ChromaDbConfig
from embedchain.vectordb.chroma import ChromaDB
from embedchain import App
from langchain_core.tools import tool
from assets.prompts import (dick_specific_prompt, shackilton_specific_prompt, sam_specific_prompt, arches_specific_prompt, 
                     wiggins_specific_prompt, action_specific_prompt, decisive_specific_prompt,
                     addie_specific_prompt, behavior_specific_prompt, mager_specific_prompt,
                     CRITIQUE_PROMPT)

from typing import List
from abc import abstractmethod, ABC

import os

def load_chromadb(collection_name: str, db_path:str, resources: List[str]):
    chromadb_config = ChromaDbConfig(collection_name=collection_name, dir=db_path, host='localhost')
    chromadb = ChromaDB(config=chromadb_config)
    app = App(db=chromadb)
    for resource in resources:
        app.add(resource)
    print("loaded")




class Evaluator(ABC):
    def __init__(self, collection_name, db_path, prompt, content):

        self.collection_name = collection_name
        self.db_path = db_path
        self.base_prompt = prompt
        # self.critique = critique
        prompt = self.base_prompt.format(content=content)
      
        base_llm_config = BaseLlmConfig(prompt=prompt)
        evalllm = OpenAILlm(config=base_llm_config)
        chromadb_config = ChromaDbConfig(collection_name=collection_name, dir=db_path, host='localhost')
        chromadb = ChromaDB(config=chromadb_config)
        self.app = App(llm=evalllm, db=chromadb)
        # for resource in resources:
        #     self.app.add(resource)
            
    @abstractmethod
    def set_critique(self):
        pass

class DesignEvaluator(Evaluator):
    def __init__(self, collection_name, db_path, prompt, content):
        super().__init__(collection_name, db_path, prompt, content)

    
    def set_critique(self, critique_level):
        critique = CRITIQUE_PROMPT.format(critique_level=critique_level)
        self.dick_specific_prompt = dick_specific_prompt + "\n" + critique
        self.arches_specific_prompt  = arches_specific_prompt + "\n" + critique
        self.sam_specific_prompt = sam_specific_prompt + "\n" + critique
        self.shackilton_specific_prompt = shackilton_specific_prompt + "\n" + critique

    def eval_dick(self):
        """Evaluates the content with the Dick and Carey Instructional Design Model"""
        
        name: str = "Dick and Carey Instructional Design Model"
        evaluation_result = self.app.query(input_query=self.dick_specific_prompt)
        return evaluation_result
        
    
    def eval_sam(self):
        """Evaluates the content with the SAM (Successive Approximation Model)"""
        
        name: str = "SAM (Successive Approximation Model)"
        
        evaluation_result = self.app.query(input_query=self.sam_specific_prompt)
        return evaluation_result

    def eval_shackilton(self):
        """Evaluates the content with the Shackleton 5Di Model (Nick Shackleton)"""

        name: str = "Shackilton Model"
        
        evaluation_result = self.app.query(input_query=self.shackilton_specific_prompt)
        return evaluation_result

    def eval_arches(self):
        """Evaluates the content with the Learning Arches and Learning Spaces (Kaospilot)""" 
        
        name: str = "Learning Arches and Learning Spaces (Kaospilot)"

        evaluation_result = self.app.query(input_query=self.arches_specific_prompt)
        return evaluation_result 
    
    def eval_design(self):
        return {'Dick': self.eval_dick(),
                'SAM': self.eval_sam(),
                'Shackilton': self.eval_shackilton(),
                'Arches': self.eval_arches()
                }
    


class TransferEvaluator(Evaluator):
    def __init__(self, collection_name, db_path, prompt, content):
        super().__init__(collection_name, db_path, prompt, content)

    
    def set_critique(self, critique_level):
        critique = CRITIQUE_PROMPT.format(critique_level=critique_level)
        self.wiggins_specific_prompt = wiggins_specific_prompt + "\n" + critique
        self.action_specific_prompt  = action_specific_prompt + "\n" + critique
        self.decisive_specific_prompt = decisive_specific_prompt + "\n" + critique
    

    def eval_action(self):
        """Evaluates the content with the Action Mapping (Cathy Moore)"""
        
        
        evaluation_result = self.app.query(input_query=self.action_specific_prompt)
        return evaluation_result
        
    
    def eval_decisive(self):
        """Evaluates the content with the The Decisive Dozen (Dr. Will Thalheimer, PhD)"""
        
        evaluation_result = self.app.query(input_query=self.decisive_specific_prompt)
        return evaluation_result

    def eval_wiggins(self):
        """Evaluates the content with the Wiggins and McTighe Backwards Design Model (UbD)"""

        
        evaluation_result = self.app.query(input_query=self.wiggins_specific_prompt)
        return evaluation_result

    
    def eval_transfer(self):
        return {'Action': self.eval_action(),
                'Decisive': self.eval_decisive(),
                'Wiggins': self.eval_wiggins()
                }
    


class PerformanceEvaluator(Evaluator):
    def __init__(self, collection_name, db_path, prompt, content):
        super().__init__(collection_name, db_path, prompt, content)

    
    def set_critique(self, critique_level):
        critique = CRITIQUE_PROMPT.format(critique_level=critique_level)
        self.addie_specific_prompt = addie_specific_prompt + "\n" + critique
        self.behaior_specific_prompt  = behavior_specific_prompt + "\n" + critique
        self.mager_specific_prompt = mager_specific_prompt + "\n" + critique
    

    def eval_addie(self):
        """Evaluates the content with the ADDIE Model"""
        
        
        evaluation_result = self.app.query(input_query=self.addie_specific_prompt)
        return evaluation_result
        
    
    def eval_behavior(self):
        """Evaluates the content with the Behavior Engineering Model"""
        
        evaluation_result = self.app.query(input_query=self.behaior_specific_prompt)
        return evaluation_result

    def eval_mager(self):
        """Evaluates the content with the  Mager and Pipe Model"""

        
        evaluation_result = self.app.query(input_query=self.mager_specific_prompt)
        return evaluation_result

    
    def eval_performance(self):
        return {'Addie': self.eval_addie(),
                'Behavior': self.eval_behavior(),
                'Mager': self.eval_mager()
                }

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

    