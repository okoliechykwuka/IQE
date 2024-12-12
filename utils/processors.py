# processors.py
import PyPDF2
from typing import Dict, Any, List
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.youtube import TranscriptFormat
from langchain.text_splitter import CharacterTextSplitter
import streamlit as st
import tempfile
import os
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
api_key = st.secrets["OPENAI_API_KEY"]
## Set the API key
client = OpenAI(api_key=api_key)


class BaseProcessor:
    def __init__(self):
        self.text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    def chunk_content(self, text: str) -> List[str]:
        return self.text_splitter.split_text(text)


class PDFProcessor(BaseProcessor):
    def process(self, file) -> Dict[str, Any]:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(file.getvalue())
                tmp_file.seek(0)

                with open(tmp_file.name, "rb") as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    text = ""
                    total_pages = len(reader.pages)
                    st.write(total_pages)
                    progress_bar = st.progress(0)
                    for i, page in enumerate(reader.pages):
                        text += f"<p>Page {i+1}>\n" + page.extract_text() + "\n\n"
                        progress_bar.progress((i + 1) / total_pages)

                    chunks = self.chunk_content(text, chunk_size=50)

                    return {
                        "content_type": "pdf",
                        "raw_text": text,
                        "chunks": chunks,
                        "metadata": {
                            "pages": total_pages,
                            "word_count": len(text.split()),
                        },
                    }
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            # print(f"Error processing PDF: {str(e)}")
            return None
        finally:
            if "tmp_file" in locals():
                os.unlink(tmp_file.name)

    def chunk_content(self, book: str, chunk_size=50) -> List[str]:
        pages = book.split("<p>")[1:]
        chunks = []
        for i in range(1, len(pages), chunk_size):
            chunk = pages[i : i + chunk_size]
            chunks.append(chunk[0])
            if (i + chunk_size) >= len(pages):
                break
        return chunks


class VideoProcessor(BaseProcessor):
    def process(self, url: str) -> Dict[str, Any]:
        try:
            chunk_size_seconds = 120
            loader = YoutubeLoader.from_youtube_url(
                url,
                add_video_info=False,
                transcript_format=TranscriptFormat.CHUNKS,
                chunk_size_seconds=chunk_size_seconds,
            )

            # with st.spinner("Extracting video transcript..."):
            transcripts = loader.load()

            if not transcripts:
                raise ValueError("No transcript available")
            text = ""
            for doc in transcripts:
                text += (
                    f"<timestamp:start_seconds: {doc.metadata['start_seconds']}>\n"
                    + doc.page_content
                    + "\n\n"
                )

            chunks = self.chunk_content(transcripts, window_size=20)

            duration = transcripts[-1].metadata["start_seconds"] + chunk_size_seconds

            return {
                "content_type": "video (transcript)",
                "raw_text": text,
                "chunks": chunks,
                "metadata": {
                    #     "title": transcript[0].metadata.get("title"),
                    "duration": duration,
                    "word_count": len(text.split()),
                },
            }
        except Exception as e:
            st.error(f"Error processing video: {str(e)}")

            return None

    def chunk_content(self, documents, window_size=20):
        if not documents:
            return []

        chunk_size_seconds = 120  # 2 minutes
        chunks = []
        num_documents = len(documents)

        def create_chunk(docs):
            """Helper function to create a chunk from a list of documents"""
            combined_content = " ".join(doc.page_content for doc in docs)

            start_metadata = docs[0].metadata
            end_metadata = docs[-1].metadata

            metadata_str = (
                f"[METADATA] Source: {start_metadata.get('source', 'N/A')} | "
                f"Start Seconds: {start_metadata.get('start_seconds', 'N/A')} | "
                f"End Seconds: {end_metadata.get('start_seconds', 'N/A') + chunk_size_seconds} | "
                f"Start Timestamp: {start_metadata.get('start_timestamp', 'N/A')} | "
                f"End Timestamp: {end_metadata.get('start_timestamp', 'N/A')}"
            )

            return f"{metadata_str}\n\n{combined_content}"

        # If total documents are less than or equal to window_size
        if num_documents <= window_size:
            chunks.append(create_chunk(documents))
            return chunks

        # Sliding window approach
        stride = window_size - 1
        for i in range(0, num_documents - window_size + 1, stride):
            window_docs = documents[i : i + window_size]
            chunks.append(create_chunk(window_docs))

        # Handle remaining documents
        remaining_docs = documents[-(num_documents % stride) :]
        if remaining_docs:
            chunks.append(create_chunk(remaining_docs))

        return chunks


class AudioProcessor(BaseProcessor):
    # def __init__(self):
    #     super().__init__()
    #     self.model = whisper.load_model("base")

    def get_audio_transacript(self, audio_path):
        # audio_path = "audio1.mp3"
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=open(audio_path, "rb"),
        )
        return transcription

    def process(self, file) -> Dict[str, Any]:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
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
                        "duration": len(text.split()) * 0.24,
                        "word_count": len(text.split()),
                    },
                }
        except Exception as e:
            st.error(f"Error processing audio: {str(e)}")
            # print(f"Error processing audio: {str(e)}")
            return None
        finally:
            if "tmp_file" in locals():
                os.unlink(tmp_file.name)


class DummyProcessor(BaseException):
    def process(self, file):
        return {
            "content_type": "Unsupported",
            "raw_text": "",
            "chunks": [],
            "metadata": {"pages": 0, "word_count": 0},
        }
