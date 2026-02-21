from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from . import schemas, database, crud

app = FastAPI(
    title="Anvisa Medications Analytics API",
    description="API para acessar dados de medicamentos da Anvisa/CMED",
    version="2.0.0"
)

get_db = database.get_db
    
@app.get("/medications", response_model=List[schemas.MedicationResponse])
def list_medications(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Busca por nome do produto ou substância"),
    laboratory: Optional[str] = Query(None, description="Filtrar por nome do laboratório"),
    stripe: Optional[str] = Query(None, description="Filtrar por tarja (ex: Vermelha)"),
    db: Session = Depends(get_db)
):
    """
    Lista medicamentos com paginação e filtros.
    """
    try:
        medications = crud.get_medications(
            db=db, 
            skip=skip, 
            limit=limit, 
            search=search, 
            laboratory=laboratory, 
            stripe=stripe
        )
        return medications

    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno no servidor de dados.")

@app.get("/medications/{ggrem}", response_model=schemas.MedicationResponse)
def get_medication_by_ggrem(ggrem: int, db: Session = Depends(get_db)):
    """
    Busca um medicamento específico pelo código único GGREM.
    """
    medication = crud.get_medication_by_ggrem(db=db, ggrem=ggrem)

    if not medication:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    
    return medication