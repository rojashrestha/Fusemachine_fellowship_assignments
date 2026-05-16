from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud
import schemas
import database
import asyncio         

app = FastAPI()


from routers import counts
app.include_router(counts.router)

# Existing customers list and get by id
@app.get("/customers", response_model=list[schemas.CustomerOut])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    customers = crud.get_customers(db, skip=skip, limit=limit)
    return customers

@app.get("/customers/{customer_id}", response_model=schemas.CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(database.get_db)):
    db_customer = crud.get_customer_by_id(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

# 🔥 Concurrency endpoint (Task 3 ko must)
@app.get("/overall_counts")
async def overall_counts(db: Session = Depends(database.get_db)):
    results = await asyncio.gather(
        asyncio.to_thread(crud.get_customers_count, db),
        asyncio.to_thread(crud.get_orders_count, db),
        asyncio.to_thread(crud.get_products_count, db),
        asyncio.to_thread(crud.get_employees_count, db),
        asyncio.to_thread(crud.get_offices_count, db),
        asyncio.to_thread(crud.get_payments_count, db),
        asyncio.to_thread(crud.get_orderdetails_count, db),
        asyncio.to_thread(crud.get_productlines_count, db)
    )
    return {
        "customers": results[0],
        "orders": results[1],
        "products": results[2],
        "employees": results[3],
        "offices": results[4],
        "payments": results[5],
        "orderdetails": results[6],
        "productlines": results[7]
    }