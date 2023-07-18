from datetime import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

    data = [
        {
            "type": "Director",
            "permissions": ["post:product", "patch:product", "get:product", "delete:product", 
                            "get:salesrecord", "get:productsales", "get:staff", "post:staff"]
        },
        {
            "type": "Manager",
            "permissions": ["get:product", "get:salesrecord", "get:productsales", "post:staff"]
        },
        {
            "type": "Worker",
            "permissions": ["get:product", "get:salesrecord", "get:productsales"]
        }
    ]


    for d in data:
        role = Roles(type=d["type"], permissions=d["permissions"])
        role.insert()

class Roles(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = db.Column(db.String())
    permissions = db.Column(db.ARRAY(db.String()))

    def insert(self):
        db.session.add(self)
        db.session.commit()


    def format(self):
        return {
            'id': self.id,
            'type': self.type,
            'permissions': [permission for permission in self.permissions]
        }

class Staffs(db.Model):
    __tablename__ = "staffs"
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(50), nullable=False, unique=True)
    gender = db.Column(db.String(10), nullable=False)
    role = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    token = db.Column(db.String(), nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def reverse(self):
        db.session.rollback()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'role': self.role,
            'token': self.token
        }

class Products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    quantity_available = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(10), nullable=False, default="units")
    product_sales = db.relationship('Product_sales', backref='products', lazy=True)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def reverse(self):
        db.session.rollback()    

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'quantity_available': self.quantity_available,
            'unit': self.unit
        }


class Sales_record(db.Model):
    __tablename__ = "sales_record"
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_name = db.Column(db.String(100), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.today())
    product_sales = db.relationship('Product_sales', backref='sales_record', lazy=True)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def reverse(self):
        db.session.rollback()

    def format(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'total_price': self.total_price,
            'date': self.date
        }


class Product_sales(db.Model):
    __tablename__ = "product_sales"
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('products.id'))
    product_name = db.Column(db.String(100), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    quantity_bought = db.Column(db.Float, nullable=False)
    record_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('sales_record.id'))

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def reverse(self):
        db.session.rollback()

    def format(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_price': self.product_price,
            'quantity_bought': self.quantity_bought,
            'record_id': self.record_id
        }