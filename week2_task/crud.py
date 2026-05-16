from sqlalchemy.orm import Session
from models import Customer
from models import Customer, Order, Product, Employee, Office, Payment, OrderDetail, ProductLine

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Customer).offset(skip).limit(limit).all()

def get_customer_by_id(db: Session, customer_id: int):
    return db.query(Customer).filter(Customer.customerNumber == customer_id).first()



def get_customers_count(db: Session) -> int:
    return db.query(Customer).count()

def get_orders_count(db: Session) -> int:
    return db.query(Order).count()

def get_products_count(db: Session) -> int:
    return db.query(Product).count()

def get_employees_count(db: Session) -> int:
    return db.query(Employee).count()

def get_offices_count(db: Session) -> int:
    return db.query(Office).count()

def get_payments_count(db: Session) -> int:
    return db.query(Payment).count()

def get_orderdetails_count(db: Session) -> int:
    return db.query(OrderDetail).count()

def get_productlines_count(db: Session) -> int:
    return db.query(ProductLine).count()