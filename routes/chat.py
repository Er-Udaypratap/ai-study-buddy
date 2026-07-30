from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.ai_service import get_ai_response

router = APIRouter()


class ChatRequest(BaseModel):
    mode: str  # "education" | "constitution" | "english"
    message: str
    history: list = []  # previous messages: [{"role": "user"/"model", "parts": ["text"]}]


class ChatResponse(BaseModel):
    reply: str
    mode: str


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    if req.mode not in ["education", "constitution", "english"]:
        raise HTTPException(status_code=400, detail="Invalid mode")

    context = ""
    if req.mode == "constitution":
        # TODO: yahan RAG retrieval call karo (pgvector se matching articles laao)
        # context = retrieve_constitution_context(req.message)
        pass

    try:
        reply = get_ai_response(
            mode=req.mode,
            user_message=req.message,
            chat_history=req.history,
            context=context,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

    return ChatResponse(reply=reply, mode=req.mode)
