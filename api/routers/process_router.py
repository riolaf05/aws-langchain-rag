from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from starlette import status
from utils.subscription_manager import SubscriptionManager
from models.serializers import ReceiverSerializer

router = APIRouter()
manager = SubscriptionManager()

@router.get("/healthcheck")
async def health():
    response = JSONResponse(content="OK!", status_code=status.HTTP_200_OK)
    return response


@router.post("/summarization")
async def receive_message(request: ReceiverSerializer):
    
    success = manager.process(**dict(request))

    if success:
        response = JSONResponse(
            content={"message": "Message received!"}, status_code=status.HTTP_200_OK
        )
    else:
        response = JSONResponse(
            content={"message": "ERROR"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response