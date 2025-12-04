from __future__ import annotations

from datetime import date
from typing import List, Optional, Literal
import uuid

from pydantic import BaseModel, Field, validator


# Metadata and preparer info
class PreparerInfo(BaseModel):
    firm_name: str = ""
    preparer_name: str = ""
    preparer_id: str = ""


class Metadata(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tax_year: int = Field(default=date.today().year)
    client_id: str
    status: Literal["intake_in_progress", "ready_for_review", "completed"] = "intake_in_progress"
    prepared_by: PreparerInfo = Field(default_factory=PreparerInfo)
    notes: List[str] = Field(default_factory=list)


# Taxpayer information
class Person(BaseModel):
    first_name: str = ""
    last_name: str = ""
    ssn: str = ""
    dob: str = ""
    occupation: str = ""
    phone: str = ""
    email: str = ""


class Spouse(BaseModel):
    exists: bool = False
    first_name: str = ""
    last_name: str = ""
    ssn: str = ""
    dob: str = ""
    occupation: str = ""


class Taxpayer(BaseModel):
    primary: Person
    spouse: Spouse = Field(default_factory=Spouse)
    filing_status: str = ""
    residency_state: str = ""
    other_states: List[str] = Field(default_factory=list)


# Dependents
class Dependent(BaseModel):
    first_name: str = ""
    last_name: str = ""
    ssn: str = ""
    dob: str = ""
    relationship: str = ""
    months_lived_with_taxpayer: int = 0
    is_student: bool = False
    is_disabled: bool = False
    supports_self_more_than_half: bool = False


# Income structures
class W2Income(BaseModel):
    employer_name: str = ""
    wages: float = 0.0
    federal_withholding: float = 0.0
    state: str = ""
    state_withholding: float = 0.0


class InterestIncome(BaseModel):
    payer: str = ""
    amount: float = 0.0


class DividendIncome(BaseModel):
    payer: str = ""
    ordinary_dividends: float = 0.0
    qualified_dividends: float = 0.0


class SelfEmploymentIncome(BaseModel):
    business_name: str = ""
    ein: str = ""
    income: float = 0.0
    expenses: float = 0.0


class RentalIncome(BaseModel):
    property_address: str = ""
    income: float = 0.0
    expenses: float = 0.0


class RetirementIncome(BaseModel):
    payer: str = ""
    amount: float = 0.0
    taxable_amount: float = 0.0


class SocialSecurityIncome(BaseModel):
    amount: float = 0.0
    taxable_amount: float = 0.0


class OtherIncome(BaseModel):
    description: str = ""
    amount: float = 0.0


class Income(BaseModel):
    w2: List[W2Income] = Field(default_factory=list)
    interest_1099int: List[InterestIncome] = Field(default_factory=list)
    dividends_1099div: List[DividendIncome] = Field(default_factory=list)
    brokerage_1099b: List[OtherIncome] = Field(default_factory=list)
    self_employment: List[SelfEmploymentIncome] = Field(default_factory=list)
    rental: List[RentalIncome] = Field(default_factory=list)
    retirement_1099r: List[RetirementIncome] = Field(default_factory=list)
    social_security: List[SocialSecurityIncome] = Field(default_factory=list)
    other_income: List[OtherIncome] = Field(default_factory=list)


# Adjustments
class HSAAdjustments(BaseModel):
    contributions: float = 0.0
    coverage_type: str = ""


class IRAContribution(BaseModel):
    type: str = "traditional"
    amount: float = 0.0
    deductible_amount: Optional[float] = None


class Adjustments(BaseModel):
    student_loan_interest: float = 0.0
    hsa: HSAAdjustments = Field(default_factory=HSAAdjustments)
    ira_contributions: List[IRAContribution] = Field(default_factory=list)
    self_employed_health_insurance: float = 0.0
    other_adjustments: List[OtherIncome] = Field(default_factory=list)


# Deductions and credits
class ScheduleA(BaseModel):
    medical: float = 0.0
    state_and_local_taxes: float = 0.0
    real_estate_taxes: float = 0.0
    mortgage_interest: float = 0.0
    charity_cash: float = 0.0
    charity_non_cash: float = 0.0
    other: List[OtherIncome] = Field(default_factory=list)


class ChildAndDependentCare(BaseModel):
    provider_name: str = ""
    amount: float = 0.0


class EducationCredit(BaseModel):
    student_name: str = ""
    form: str = ""
    qualified_expenses: float = 0.0


class EnergyCredit(BaseModel):
    description: str = ""
    amount: float = 0.0


class DeductionsAndCredits(BaseModel):
    itemize_or_standard: Literal["auto", "standard", "itemize"] = "auto"
    schedule_a: ScheduleA = Field(default_factory=ScheduleA)
    child_and_dependent_care: ChildAndDependentCare = Field(default_factory=ChildAndDependentCare)
    education_credits: List[EducationCredit] = Field(default_factory=list)
    energy_credits: List[EnergyCredit] = Field(default_factory=list)
    other_credits: List[OtherIncome] = Field(default_factory=list)


# Payments and documents
class EstimatedPayment(BaseModel):
    date_paid: str = ""
    amount: float = 0.0


class WithholdingAndPayments(BaseModel):
    federal_withholding_total: float = 0.0
    estimated_payments: List[EstimatedPayment] = Field(default_factory=list)
    applied_prior_year_refund: float = 0.0
    other_payments: List[OtherIncome] = Field(default_factory=list)


class Document(BaseModel):
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_name: str = ""
    type: str = ""
    tax_year: int = Field(default=date.today().year)
    uploaded_by: Literal["client", "preparer"] = "client"
    status: Literal["uploaded", "parsed_pending_review", "confirmed"] = "uploaded"
    tags: List[str] = Field(default_factory=list)


class Issue(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: Literal["missing_document", "clarification", "inconsistency"]
    description: str
    severity: Literal["low", "medium", "high"] = "medium"
    status: Literal["open", "answered", "dismissed"] = "open"


class PreparerReview(BaseModel):
    checklist_completed: bool = False
    red_flags: List[str] = Field(default_factory=list)
    final_comments: str = ""


class CaseFile(BaseModel):
    metadata: Metadata
    taxpayer: Taxpayer
    dependents: List[Dependent] = Field(default_factory=list)
    income: Income = Field(default_factory=Income)
    adjustments: Adjustments = Field(default_factory=Adjustments)
    deductions_and_credits: DeductionsAndCredits = Field(default_factory=DeductionsAndCredits)
    withholding_and_payments: WithholdingAndPayments = Field(default_factory=WithholdingAndPayments)
    documents: List[Document] = Field(default_factory=list)
    issues_and_questions: List[Issue] = Field(default_factory=list)
    preparer_review: PreparerReview = Field(default_factory=PreparerReview)

    @validator("metadata")
    def ensure_id(cls, value: Metadata) -> Metadata:
        if not value.id:
            value.id = str(uuid.uuid4())
        return value


# Request/response schemas
class CaseCreateRequest(BaseModel):
    client_id: str
    tax_year: int
    primary_first_name: str
    primary_last_name: str
    filing_status: str = ""


class CaseUpdateRequest(BaseModel):
    case_file: CaseFile


class CasePartialUpdateRequest(BaseModel):
    patch: dict


class AgentMessageRequest(BaseModel):
    message: str


class AgentResponse(BaseModel):
    reply: str
    updated_case_file: CaseFile
