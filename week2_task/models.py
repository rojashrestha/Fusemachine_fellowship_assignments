from sqlalchemy import Column, Integer, String, Numeric, Date, SmallInteger, ForeignKey, Text
from database import Base

class Customer(Base):
    __tablename__ = "customers"
    customerNumber = Column(Integer, primary_key=True, index=True)
    customerName = Column(String(50))
    contactLastName = Column(String(50))
    contactFirstName = Column(String(50))
    phone = Column(String(50))
    addressLine1 = Column(String(50))
    addressLine2 = Column(String(50), nullable=True)
    city = Column(String(50))
    state = Column(String(50), nullable=True)
    postalCode = Column(String(15), nullable=True)
    country = Column(String(50))
    salesRepEmployeeNumber = Column(Integer, nullable=True)
    creditLimit = Column(Numeric(10,2), nullable=True)

class Order(Base):
    __tablename__ = "orders"
    orderNumber = Column(Integer, primary_key=True)
    orderDate = Column(Date)
    requiredDate = Column(Date)
    shippedDate = Column(Date, nullable=True)
    status = Column(String(15))
    comments = Column(Text, nullable=True)
    customerNumber = Column(Integer)

class Product(Base):
    __tablename__ = "products"
    productCode = Column(String(15), primary_key=True)
    productName = Column(String(70))
    productLine = Column(String(50))
    productScale = Column(String(10))
    productVendor = Column(String(50))
    productDescription = Column(Text)
    quantityInStock = Column(Integer)
    buyPrice = Column(Numeric(10,2))
    MSRP = Column(Numeric(10,2))

class Employee(Base):
    __tablename__ = "employees"
    employeeNumber = Column(Integer, primary_key=True)
    lastName = Column(String(50))
    firstName = Column(String(50))
    extension = Column(String(10))
    email = Column(String(100))
    officeCode = Column(String(10))
    reportsTo = Column(Integer, nullable=True)
    jobTitle = Column(String(50))

class Office(Base):
    __tablename__ = "offices"
    officeCode = Column(String(10), primary_key=True)
    city = Column(String(50))
    phone = Column(String(50))
    addressLine1 = Column(String(50))
    addressLine2 = Column(String(50), nullable=True)
    state = Column(String(50), nullable=True)
    country = Column(String(50))
    postalCode = Column(String(15))
    territory = Column(String(10))

class Payment(Base):
    __tablename__ = "payments"
    customerNumber = Column(Integer, primary_key=True)
    checkNumber = Column(String(50), primary_key=True)
    paymentDate = Column(Date)
    amount = Column(Numeric(10,2))

class OrderDetail(Base):
    __tablename__ = "orderdetails"
    orderNumber = Column(Integer, primary_key=True)
    productCode = Column(String(15), primary_key=True)
    quantityOrdered = Column(Integer)
    priceEach = Column(Numeric(10,2))
    orderLineNumber = Column(SmallInteger)

class ProductLine(Base):
    __tablename__ = "productlines"
    productLine = Column(String(50), primary_key=True)
    textDescription = Column(String(4000), nullable=True)
    htmlDescription = Column(Text, nullable=True)
    image = Column(String(100), nullable=True)  # or BYTEA but String works