from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Enviar mensagem ao chatbot",
    description="Processa uma mensagem do usuário e retorna uma resposta com base no estoque de produtos.",
)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    chat_service = ChatService(db)
    answer = chat_service.process_message(request.message)
    return ChatResponse(answer=answer)
