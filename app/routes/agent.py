from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.models import Case, deserialize_case, get_db, serialize_case
from app.services.llm import LLMService
from .cases import get_case_or_404

router = APIRouter(prefix="/tax-agent", tags=["tax-agent"])
llm_service = LLMService()


@router.post("/{case_id}", response_model=schemas.AgentResponse)
def handle_agent_message(case_id: str, request: schemas.AgentMessageRequest, db: Session = Depends(get_db)):
    case_record: Case = get_case_or_404(case_id, db)
    case_file = schemas.CaseFile(**deserialize_case(case_record.data))

    response = llm_service.generate_agent_reply(message=request.message, case_file=case_file)

    # Validate updated case file and persist
    try:
        updated_case = schemas.CaseFile(**response.updated_case_file.dict())
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Invalid case file from agent") from exc

    case_record.data = serialize_case(updated_case.dict())
    db.commit()

    return schemas.AgentResponse(reply=response.reply, updated_case_file=updated_case)
