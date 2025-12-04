from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.models import Case, deserialize_case, get_db, serialize_case

router = APIRouter(prefix="/case", tags=["cases"])


def get_case_or_404(case_id: str, db: Session) -> Case:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


@router.post("", response_model=schemas.CaseFile, status_code=status.HTTP_201_CREATED)
def create_case(request: schemas.CaseCreateRequest, db: Session = Depends(get_db)):
    case_file = schemas.CaseFile(
        metadata=schemas.Metadata(client_id=request.client_id, tax_year=request.tax_year),
        taxpayer=schemas.Taxpayer(
            primary=schemas.Person(
                first_name=request.primary_first_name,
                last_name=request.primary_last_name,
            ),
            filing_status=request.filing_status,
        ),
    )
    case_record = Case(id=case_file.metadata.id, data=serialize_case(case_file.dict()))
    db.add(case_record)
    db.commit()
    return case_file


@router.get("/{case_id}", response_model=schemas.CaseFile)
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = get_case_or_404(case_id, db)
    return schemas.CaseFile(**deserialize_case(case.data))


@router.put("/{case_id}", response_model=schemas.CaseFile)
def update_case(case_id: str, request: schemas.CaseUpdateRequest, db: Session = Depends(get_db)):
    case = get_case_or_404(case_id, db)
    if request.case_file.metadata.id != case_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Metadata id must match case id",
        )
    case.data = serialize_case(request.case_file.dict())
    db.commit()
    return request.case_file


@router.patch("/{case_id}", response_model=schemas.CaseFile)
def patch_case(case_id: str, request: schemas.CasePartialUpdateRequest, db: Session = Depends(get_db)):
    case = get_case_or_404(case_id, db)
    stored = schemas.CaseFile(**deserialize_case(case.data))
    patched_dict = stored.dict()
    patched_dict.update(request.patch)
    try:
        patched_case = schemas.CaseFile(**patched_dict)
    except Exception as exc:  # Validation errors propagate to HTTP 422 automatically when raised
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    case.data = serialize_case(patched_case.dict())
    db.commit()
    return patched_case
