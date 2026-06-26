from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.chat_service import ChatService
from app.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Process a chat message and return a response.
    """
    chat_service = ChatService(db)
    answer = chat_service.process_message(request.message)
    return ChatResponse(answer=answer)
