# routers/counts.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import crud

router = APIRouter()

@router.get("/customers/count")
def customers_count(db: Session = Depends(get_db)):
    count = crud.get_customers_count(db)
    return {"table": "customers", "count": count}

@router.get("/orders/count")
def orders_count(db: Session = Depends(get_db)):
    count = crud.get_orders_count(db)
    return {"table": "orders", "count": count}

@router.get("/products/count")
def products_count(db: Session = Depends(get_db)):
    count = crud.get_products_count(db)
    return {"table": "products", "count": count}

@router.get("/employees/count")
def employees_count(db: Session = Depends(get_db)):
    count = crud.get_employees_count(db)
    return {"table": "employees", "count": count}

@router.get("/offices/count")
def offices_count(db: Session = Depends(get_db)):
    count = crud.get_offices_count(db)
    return {"table": "offices", "count": count}

@router.get("/payments/count")
def payments_count(db: Session = Depends(get_db)):
    count = crud.get_payments_count(db)
    return {"table": "payments", "count": count}

@router.get("/orderdetails/count")
def orderdetails_count(db: Session = Depends(get_db)):
    count = crud.get_orderdetails_count(db)
    return {"table": "orderdetails", "count": count}

@router.get("/productlines/count")
def productlines_count(db: Session = Depends(get_db)):
    count = crud.get_productlines_count(db)
    return {"table": "productlines", "count": count}