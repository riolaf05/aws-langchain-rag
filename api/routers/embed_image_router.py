import asyncio
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from utils.subscription_manager import FileUploader
from utils.aws_services import AWSS3
from utils.database_managers import QDrantDBManager
from utils.embedding import EmbeddingFunction
from utils.text_processing import TextSplitter
from utils.language_models import LangChainAI
import base64
import openai
from uuid import uuid4
import json
import os

router = APIRouter()
fileUploader = FileUploader()
embedding = EmbeddingFunction('fast-bgeEmbedding').embedder
text_splitter = TextSplitter(
    chunk_size=2000, 
    chunk_overlap=20
)


QDRANT_URL=os.getenv('QDRANT_URL')
COLLECTION_NAME="images"
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

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def image_summarize(img_base64,prompt):
    ''' 
    Image summary
    Takes in a base64 encoded image and prompt (requesting an image summary)
    Returns a response from the LLM (image summary) 
    '''
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_base64}",
                },
                },
            ],
            }
        ],
        max_tokens=150,
    )
    content = response.choices[0].message.content
    return content

@router.post("/embed_image", operation_id="embed_image")
async def upload(file: UploadFile = File(...)):
    """
    Embed an image on the Vector DB and upload it on S3

    """
    print(file.content_type)
    if file.content_type != 'image/jpeg' | file.content_type != 'image/png':
        # Log the error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Non permesso!")
    
    try:
        data = json.loads(file.file.read())
        base64_image = encode_image(data)
        prompt = "Descrivi l'immagine in dettaglio:"
        summarization = image_summarize(base64_image,prompt)
    
        # Upload the file on S3
        # response = fileUploader.pass_file_to_upload("raw_documents", file)

    except Exception as e:
        # Catch any other errors
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    
    return {
        "filename":file.filename,
        "content":summarization
    }
        

    