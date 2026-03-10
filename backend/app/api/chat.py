from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional, Union, Dict, Any
from app.services.chat_service import ChatService
from app.schemas.chat_api import ChatRequest, ClarificationResponse, ItineraryResponse, ChatSession

router = APIRouter(prefix="/api/chat", tags=["chat"])

# For MVP/authentication dependency placeholder
async def get_current_user_optional():
    return None

@router.post("/", response_model=Union[ClarificationResponse, ItineraryResponse])
async def chat(
    request: ChatRequest,
    current_user: Optional[Any] = Depends(get_current_user_optional)
):
    """
    Process chat message and return response.
    
    Returns clarification questions if info missing,
    or complete itinerary if all info provided.
    """
    service = ChatService()
    
    user_id = current_user.id if current_user else None
    
    response = await service.process_message(
        message=request.message,
        session_id=request.session_id,
        user_id=user_id
    )
    
    if getattr(response, "type", "") == "error":
        raise HTTPException(status_code=400, detail=response.message)
    
    return response

@router.post("/{session_id}/clarify", response_model=Union[ClarificationResponse, ItineraryResponse])
async def submit_clarification(
    session_id: str,
    answers: Dict[str, Any] = Body(...),
    current_user: Optional[Any] = Depends(get_current_user_optional)
):
    """Submit answers to clarification questions"""
    service = ChatService()
    user_id = current_user.id if current_user else None
    
    response = await service.process_clarification(
        session_id=session_id,
        answers=answers,
        user_id=user_id
    )
    
    if getattr(response, "type", "") == "error":
        raise HTTPException(status_code=400, detail=response.message)
        
    return response


@router.post("/{session_id}/generate-itinerary", response_model=ItineraryResponse)
async def generate_itinerary_for_session(
    session_id: str,
    current_user: Optional[Any] = Depends(get_current_user_optional)
):
    """Generate itinerary for an existing complete session intent."""
    service = ChatService()
    user_id = current_user.id if current_user else None

    response = await service.generate_itinerary_for_session(
        session_id=session_id,
        user_id=user_id,
    )

    if getattr(response, "type", "") == "error":
        raise HTTPException(status_code=400, detail=response.message)

    return response

@router.get("/{session_id}", response_model=ChatSession)
async def get_chat_history(
    session_id: str,
    current_user: Optional[Any] = Depends(get_current_user_optional)
):
    """Get chat session history"""
    service = ChatService()
    user_id = current_user.id if current_user else None
    
    session = await service._get_session(session_id)
    if session is None or (not session.current_intent and not session.last_clarification):
        raise HTTPException(status_code=404, detail="Session not found")
        
    return session
