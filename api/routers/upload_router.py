import asyncio
import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from utils.subscription_manager import FileUploader
from utils.aws_services import AWSS3
import os

router = APIRouter()
fileUploader = FileUploader()

logger = logging.getLogger(__name__)

@router.post("/upload", operation_id="upload")
async def upload(file: list[UploadFile] = File(...)):
    """
    Upload a file on S3

    """
    try:
        # Upload the file on S3
        response = fileUploader.pass_file_to_upload("raw_documents", file)
        return response

    except Exception as e:
        # Catch any other errors
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    