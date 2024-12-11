from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import CharacterTextSplitter

from assets.evalresources import name_map

def summarize_resources(docs, model_name):
    prompt = """System Prompt:
        You are an expert in content evaluation. Your task is to summarize the context tailoring the summary in a way that one can easily apply the model 
        Present a concise summary in the below format

        - Overview of the core principles and phylosophy of {model_name}
        - The key factors to consider when using the model [Bullet Points]
        - Include any/all steps to take to systematically evaluate a learning content with the model (If applicable) [Points/Numbered]

        
            """
    

    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000, chunk_overlap=0
    )
    split_docs = text_splitter.split_documents(docs)
    # print(f"Generated {len(split_docs)} documents.")
    summary_prompt = PromptTemplate.from_template(prompt).partial(model_name=model_name)
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")
    summary_chain = load_summarize_chain(llm, chain_type='refine')
    summary_chain.initial_llm_chain.prompt = summary_prompt
    summary = summary_chain.invoke(split_docs)

    return summary['output_text']


def fetch_resources(framework, links):
    # Directory to save the text files
    Path("data").mkdir(exist_ok=True)
    data_path = Path(f'data/{framework}')

    data_path.mkdir(exist_ok=True)
    # Fetch and save content for each model
    for model_name, urls in links.items():
      
        if Path(os.path.join(data_path, f"{model_name}.txt")).exists():
            # print("Skipping Model")
            continue
        documents = []
        for url in urls:
            try:
                loader = WebBaseLoader(url)
                documents.extend(loader.load())
            except Exception as e:
                # print(f"Error fetching content from {url}: {e}")
                pass

        resource_content = summarize_resources(documents, name_map[model_name])

        # Write combined content to a single text file
        with open(data_path / f"{model_name}.txt", "w", encoding="utf-8") as fp:
            fp.write(resource_content)
        # print(f"Saved content for {model_name} to {model_name}.txt")

# fetch_resources('performance', performance_links)



import os
import sys
from pathlib import Path

def get_project_root() -> Path:
    """
    Find the absolute path to the project's root directory.
    This works regardless of the current working directory or how the script is run.
    
    Returns:
        Path: Absolute path to the project's root directory
    """
    # Get the absolute path of the current script
    current_script = Path(__file__).resolve()
    
    # Navigate up the directory tree to find the project root
    # Modify this logic if your project has a specific root marker
    project_root = Path(os.getcwd())
    
    return project_root

def get_relative_path(relative_path: str) -> Path:
    """
    Construct a path relative to the project root.
    
    Args:
        relative_path (str): Path relative to the project root
    
    Returns:
        Path: Absolute path to the specified file/directory
    """
    project_root = get_project_root()
    return project_root / relative_path