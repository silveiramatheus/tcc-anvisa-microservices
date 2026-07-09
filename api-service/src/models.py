from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from .database import Base

class Laboratory(Base):
    __tablename__ = "dim_laboratory"
    laboratory_id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(14), unique=True, index=True)
    laboratory_name = Column(String)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)

class Product(Base):
    __tablename__ = "dim_product"
    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String)
    substance = Column(Text)
    therapeutic_class = Column(String)
    product_type = Column(String)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)

class MedicationFact(Base):
    __tablename__ = "fact_medication_presentation"
    presentation_id = Column(Integer, primary_key=True, index=True)
    laboratory_id = Column(Integer, ForeignKey("dim_laboratory.laboratory_id"))
    product_id = Column(Integer, ForeignKey("dim_product.product_id"))
    ggrem_code = Column(BigInteger, unique=True, index=True)
    registration_number = Column(String)
    ean1 = Column(String)
    ean2 = Column(String)
    presentation_details = Column(Text)
    concentration = Column(String)       
    pharmaceutical_form = Column(String)
    price_regime = Column(String)
    stripe = Column(String)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    laboratory = relationship("Laboratory")
    product = relationship("Product")