from sqlalchemy.orm import Session, joinedload
from typing import Optional
from . import models

def get_medications(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    laboratory: Optional[str] = None,
    stripe: Optional[str] = None,
    pharmaceutical_form: Optional[str] = None,
    concentration: Optional[str] = None
):
    """
    Busca lista de medicamentos com filtros opcionais e paginação.
    Realiza Eager Loading das tabelas de dimensão (Produto e Laboratório).
    """
    query = db.query(models.MedicationFact)
    
    query = query.options(
        joinedload(models.MedicationFact.product),
        joinedload(models.MedicationFact.laboratory)
    )

    if search:
        search_term = f"%{search}%"
        query = query.join(models.Product).filter(
            (models.Product.product_name.ilike(search_term)) |
            (models.Product.substance.ilike(search_term))
        )
    
    if laboratory:
        if 'dim_laboratory' not in str(query.statement): 
            query = query.join(models.Laboratory)
            
        query = query.filter(models.Laboratory.laboratory_name.ilike(f"%{laboratory}%"))
        
    if stripe:
        query = query.filter(models.MedicationFact.stripe.ilike(f"%{stripe}%"))
        
    if pharmaceutical_form:
        query = query.filter(models.MedicationFact.pharmaceutical_form.ilike(f"%{pharmaceutical_form}%"))

    if concentration:
        query = query.filter(models.MedicationFact.concentration.ilike(f"%{concentration}%"))

    query = query.order_by(models.MedicationFact.ggrem_code)

    return query.offset(skip).limit(limit).all()

def get_medication_by_ggrem(db: Session, ggrem: int):
    """
    Busca um medicamento único pelo código GGREM.
    """
    return db.query(models.MedicationFact).options(
        joinedload(models.MedicationFact.product),
        joinedload(models.MedicationFact.laboratory)
    ).filter(models.MedicationFact.ggrem_code == ggrem).first()