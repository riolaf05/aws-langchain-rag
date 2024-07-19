import asyncio
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from utils.subscription_manager import FileUploader
from utils.aws_services import AWSS3
from utils.database_managers import QDrantDBManager
from utils.embedding import EmbeddingFunction
from utils.text_processing import TextSplitter
from utils.language_models import LangChainAI
from utils.speech_to_text import SpeechToText
import base64
import openai
from uuid import uuid4
import json
from pathlib import Path
import shutil
import os

router = APIRouter()
fileUploader = FileUploader()
stt = SpeechToText('transcribe')
embedding = EmbeddingFunction('fast-bgeEmbedding').embedder
text_splitter = TextSplitter(
    chunk_size=2000, 
    chunk_overlap=20
)


QDRANT_URL=os.getenv('QDRANT_URL')
COLLECTION_NAME="riassume-pdf"
logger = logging.getLogger(__name__)
qdrantClient = QDrantDBManager(
    url=QDRANT_URL,
    port=6333,
    collection_name=COLLECTION_NAME,
    vector_size=768,
    embedding=embedding,
    record_manager_url="sqlite:///record_manager_cache.sql"
)
retriever = qdrantClient.vector_store.as_retriever()

@router.post("/embed_riassume_pdf", operation_id="embed_riassume_pdf")
async def upload(file: UploadFile = File(...)):
    """
    Extract text from an audio file, embed the text on the Vector DB and upload it on S3

    """
    print(file.content_type)
    if file.content_type != 'application/pdf':
        # Log the error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Non permesso!")
    
    else:
        try:
            destination= Path(os.path.join("/tmp", file.filename))
            print(destination)
            print(file.filename)

            with destination.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            #stt
            text = stt.transcribe(destination)

            #embed
            chunked_documents = text_splitter.fixed_split(text)
            #TODO ADD METADATATA
            qdrantClient.index_documents(chunked_documents)
            
            #clean
            os.remove(destination)
        
            # Upload the file on S3
            # response = fileUploader.pass_file_to_upload("raw_documents", file)

            return {
                "filename": file.filename,
                "content": text
            }
            
        except Exception as e:
            # Catch any other errors
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred: "+str(e))
    
        

    