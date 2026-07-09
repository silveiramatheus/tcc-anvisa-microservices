from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class LaboratoryBase(BaseModel):
    cnpj: str
    laboratory_name: str

class ProductBase(BaseModel):
    product_name: str
    substance: Optional[str] = None
    therapeutic_class: Optional[str] = None
    product_type: Optional[str] = None

class MedicationResponse(BaseModel):
    ggrem_code: int
    registration_number: Optional[str]
    ean1: Optional[str]
    presentation_details: Optional[str]
    concentration: Optional[str] = None
    pharmaceutical_form: Optional[str] = None
    price_regime: Optional[str]
    stripe: Optional[str]
    updated_at: datetime
    laboratory: LaboratoryBase
    product: ProductBase

    model_config = ConfigDict(from_attributes=True)