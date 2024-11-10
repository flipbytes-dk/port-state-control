from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Ship(BaseModel):
    name: Optional[str] = None
    imo_number: Optional[str] = None
    flag: Optional[str] = None
    ship_type: Optional[str] = None
    gross_tonnage: Optional[float] = None
    call_sign: Optional[str] = None
    deadweight: Optional[float] = None
    company: Optional[str] = None
    registered_owner: Optional[str] = None

class Inspector(BaseModel):
    name: Optional[str] = None
    id: Optional[str] = None
    authority: Optional[str] = None
    office: Optional[str] = None
    contact: Optional[str] = None

class Certificate(BaseModel):
    title: Optional[str] = None
    issuing_authority: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None

class Deficiency(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None
    action_taken: Optional[str] = None
    action_code: Optional[str] = None
    deadline: Optional[str] = None
    rectified_date: Optional[str] = None

class InspectionReport(BaseModel):
    ship: Optional[Ship] = Field(default_factory=Ship)
    inspector: Optional[Inspector] = Field(default_factory=Inspector)
    inspection_date: Optional[str] = None
    port_name: Optional[str] = None
    inspection_type: Optional[str] = None
    areas_inspected: List[str] = Field(default_factory=list)
    operational_controls: List[str] = Field(default_factory=list)
    certificates: List[Certificate] = Field(default_factory=list)
    deficiencies: List[Deficiency] = Field(default_factory=list)
    last_port: Optional[str] = None
    next_port: Optional[str] = None
    detained: Optional[bool] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }