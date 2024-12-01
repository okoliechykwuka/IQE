import os
from embedchain import App
from openai import OpenAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json

load_dotenv()

class FileProcessor:
    def __init__(self):
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        os.environ["DEEPGRAM_API_KEY"] = os.getenv("DEEPGRAM_API_KEY")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
        # Initialize the EmbedChain application
        self.app = App()

    # Function to add a PDF file
    def load_pdf(self, file_path):
        from langchain_community.document_loaders import PyMuPDFLoader

        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
        
        return docs

        # self.app.add(file_path, data_type='pdf_file')

    # Function to add a YouTube video
    # def add_youtube_video(self, video_url):
    #     self.app.add(video_url, data_type='youtube_video')

    # Function to add audio files (assuming the audio files are in a supported format)
    def add_audio(self, audio_path):

        audio_file = open(audio_path, "rb")
        transcript = self.client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["word"]
            )

        # Converting the string into JSON
        json_data = json.dumps({"text": transcript.text}, indent=4)

        self.app.add(json_data)
        
        return json_data

    # Function to query the application
    def query(self, question):
        response = self.app.query(question)
        return response
    
    def summarize_layer(self, docs):
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_text_splitters import CharacterTextSplitter
        from langchain.chains.combine_documents import create_stuff_documents_chain

        # Define prompt
        prompt = ChatPromptTemplate.from_messages(
            [("system", "Write a concise summary of the following:\\n\\n{context}")]
        )
        
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=2000, chunk_overlap=200
        )
        split_docs = text_splitter.split_documents(docs)
        print(f"Generated {len(split_docs)} documents.")
        
        # Instantiate chain
        chain = create_stuff_documents_chain(self.llm, prompt)
        
        # Invoke chain
        result = chain.invoke({"context": split_docs})
        
        return result


if __name__ == "__main__":
    file_processor = FileProcessor()
    
    # Add a PDF file
    file_processor.add_audio("files/Recording.m4a")

    

        