# processors.py
import PyPDF2
from typing import Dict, Any, List
from langchain_community.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import streamlit as st
import tempfile
import os
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
api_key = st.secrets['OPENAI_API_KEY']
## Set the API key
client = OpenAI(api_key=api_key)

class BaseProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def chunk_content(self, text: str) -> List[str]:
        return self.text_splitter.split_text(text)

class PDFProcessor(BaseProcessor):
    def process(self, file) -> Dict[str, Any]:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(file.getvalue())
                tmp_file.seek(0)
                
                with open(tmp_file.name, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    text = ""
                    total_pages = len(reader.pages)
                    st.write(total_pages)
                    progress_bar = st.progress(0)
                    for i, page in enumerate(reader.pages):
                        text += f"<Page {i+1}>\n" + page.extract_text() + "\n\n"
                        progress_bar.progress((i + 1) / total_pages)
                    
                    chunks = self.chunk_content(text)
                    
                    return {
                        "content_type": "pdf",
                        "raw_text": text,
                        "chunks": chunks,
                        "metadata": {
                            "pages": total_pages,
                            "word_count": len(text.split())
                        }
                    }
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            print(f"Error processing PDF: {str(e)}")
            return None
        finally:
            if 'tmp_file' in locals():
                os.unlink(tmp_file.name)

class VideoProcessor(BaseProcessor):
    def process(self, url: str) -> Dict[str, Any]:
        try:
            loader = YoutubeLoader.from_youtube_url(
                url,
                add_video_info=False
            )
            
            # with st.spinner("Extracting video transcript..."):
            transcript = loader.load()
            
            if not transcript:
                raise ValueError("No transcript available")
            
            text = "\n".join([doc.page_content for doc in transcript])
            chunks = self.chunk_content(text)
            
            return {
                "content_type": "video (transcript)",
                "raw_text": text,
                "chunks": chunks,
                "metadata": {
                #     "title": transcript[0].metadata.get("title"),
                #     "duration": transcript[0].metadata.get("duration"),
                    "word_count": len(text.split())
                }
            }
        except Exception as e:
            st.error(f"Error processing video: {str(e)}")
            print(f"Error processing video: {str(e)}")
            return None

class AudioProcessor(BaseProcessor):
    # def __init__(self):
    #     super().__init__()
    #     self.model = whisper.load_model("base")

    def get_audio_transacript(self, audio_path):
        # audio_path = "audio1.mp3"
        transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file= open(audio_path, "rb"),
        )
        return transcription
    

    
    def process(self, file) -> Dict[str, Any]:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_file.write(file.getvalue())
                tmp_file.seek(0)
                
                # with st.spinner("Transcribing audio..."):
                    # result = self.model.transcribe(tmp_file.name)
                # print("Transcribing!!")
                # print(tmp_file.name)
                transcription = self.get_audio_transacript(tmp_file.name)
                text = transcription.text
                chunks = self.chunk_content(text)
                
                return {
                    "content_type": "audio (transcript)",
                    "raw_text": text,
                    "chunks": chunks,
                    "metadata": {
                        # "duration": result.get("duration"),
                        "word_count": len(text.split())
                    }
                }
        except Exception as e:
            st.error(f"Error processing audio: {str(e)}")
            print(f"Error processing audio: {str(e)}")
            return None
        finally:
            if 'tmp_file' in locals():
                os.unlink(tmp_file.name)

class DummyProcessor(BaseException):
    def process(self, file):
        return {
                        "content_type": "Unsupported",
                        "raw_text": "",
                        "chunks": [],
                        "metadata": {
                            "pages": 0,
                            "word_count": 0
                        }
                    }