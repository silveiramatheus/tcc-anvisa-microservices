from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import os
from typing import List
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(
    title="Anvisa Medications API",
    description="API para acessar dados de medicamentos da Anvisa",
    version="1.0.0"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
@app.get("/medications")
def get_medicamentos(limit: int = 100, db: Session = Depends(get_db)):
    """
    Retorna uma lista de medicamentos da tabela de validados.
    """
    try:
        query = text("SELECT * FROM public.medicamentos_anvisa_validados LIMIT :limit")
        result = db.execute(query, {"limit": limit})
        
        rows = [dict(row) for row in result.mappings()]
        
        return rows
    except Exception as e:
        print(f"Erro detalhado: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao acessar o banco: {str(e)}")
    
@app.get("/medications/{substance}")
def search_by_substance(substance: str, db: Session = Depends(get_db)):
    """
    Busca medicamentos por substância.
    """
    try:
        query = text('SELECT * FROM medicamentos_anvisa_validados WHERE substance ILIKE :subst')
        result = db.execute(query, {"subst": f"%{substance}%"})
        rows = [dict(row) for row in result.mappings()]
        
        if not rows:
            raise HTTPException(status_code=404, detail="Substância não encontrada")
            
        return rows
    except Exception as e:
        print(f"Erro na busca: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")