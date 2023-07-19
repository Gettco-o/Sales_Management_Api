from datetime import datetime
from flask import Blueprint, abort, jsonify, request
from models import db, Roles, Staffs, Products, Sales_record, Product_sales
from werkzeug.security import generate_password_hash, check_password_hash
import sys
from auth import generate_token, load_token, requires_auth

main = Blueprint('main', __name__)

@main.route("/")
def index():
    return "Hello there"

@main.route("/roles")
def get_roles():
    query = Roles.query.all()
    roles = [role.format() for role in query]

    if len(roles)==0:
        abort(404)
    
    return jsonify({
        'success': True,
        'roles': roles
    })

    # TODO - get roles, add roles, update roles by director


@main.route("/staffs")
@requires_auth('get:staff')
def get_staffs(tk):

    try:
        query = Staffs.query.all()
        staffs = [staff.format() for staff in query]

        if len(staffs)==0:
            abort(404)
        
        return jsonify({
            'success': True,
            'staffs': staffs
        })
    except:
        print(sys.exc_info())
        abort(422)

@main.route("/staffs/new", methods=['POST'])
@requires_auth('post:staff')
def new_staff(tk):
    body = request.get_json()

    name = body.get('name')
    gender = body.get('gender')
    role = body.get('role')
    password = body.get('password')

    if name is None or gender is None or role is None or password is None:
        return jsonify({
                'success': False,
                'message': 'Missing fields'
            })
    permission = Roles.query.filter(Roles.type==role).first()
    permission = permission.permissions


    token = generate_token(name=name, role=role, permission=permission)

    try:
        user = Staffs.query.filter_by(name=name).first()
        if user:
            return jsonify({
                'success': False,
                'message': 'user already exists'
            })
        staff = Staffs(name=name, gender=gender, role=role, password=generate_password_hash(password), 
                       token=token.decode('utf-8'))
        staff.insert()

        return jsonify({
            'success': True,
            'created': staff.id,
            'name': staff.name,
            'gender': staff.gender,
            'role': staff.role,
            'token': staff.token
        })

    except:
        print(sys.exc_info())
        abort(422)


@main.route("/staffs/login", methods=['POST'])
def staff_login():
    body = request.get_json()

    name = body.get('name')
    password = body.get('password')

    if name is None or password is None:
        return jsonify({
                'success': False,
                'message': 'Missing Fields'
            })

    try:
        staff = Staffs.query.filter_by(name=name).first()
        
        if not staff or not check_password_hash(staff.password, password):
            return jsonify({
                "success": False,
                "message": "Incorrect details"
            })
        

        user = load_token(staff.token)

        if datetime.strptime(user['expr_time'], "%Y-%m-%d %H:%M:%S") < datetime.now():
            refresh_token(staff.id)
        
        
        return jsonify({
            "success": True,
            "id": staff.id,
            "name": staff.name,
            "gender": staff.gender,
            "role": staff.role,
            "token": staff.token
        })

    except:
        print(sys.exc_info())
        abort(422)

# token refresh
def refresh_token(id):

    try:
        staff = Staffs.query.filter(Staffs.id==id).one_or_none()

        if staff is None:
            abort(404)

        permission = Roles.query.filter(Roles.type==staff.role).first()
        permission = permission.permissions

        token = generate_token(name=staff.name, role=staff.role, permission=permission)

        staff.token = token.decode('utf-8')
        staff.update()

        return jsonify({
            "success": True,
            "id": staff.id,
            "name": staff.name,
            "gender": staff.gender,
            "role": staff.role,
            "token": staff.token
        })
    except:
        print(sys.exc_info())
        staff.reverse()
        abort(400)

@main.route("/staffs/<id>/refresh_token", methods=['PATCH'])
def refresh_staff_token(id):
    try:
        refresh_token(id)
        staff = Staffs.query.filter(Staffs.id==id).one_or_none()

        return jsonify({
            "success": True,
            "id": staff.id,
            "name": staff.name,
            "gender": staff.gender,
            "role": staff.role,
            "token": staff.token
        })
    except:
        print(sys.exc_info())
        abort(422)

@main.route("/products")
@requires_auth('get:product')
def get_products(tk):
    query = Products.query.all()
    products = [product.format() for product in query]

    if len(products)==0:
        abort(404)
    
    return jsonify({
        'success': True,
        'products': products
    })

@main.route("/products/new", methods=['POST'])
@requires_auth('post:product')
def new_product(tk):
    body = request.get_json()

    name = body.get('name')
    price = body.get('price')
    quantity_available = body.get('quantity_available')
    unit = body.get('unit')

    if name is None or price is None or quantity_available is None or unit is None:
        return jsonify({
            'success': False,
            'message': "Missing Fields"
        })
    
    try:
        item = Products.query.filter_by(name=name).first()
        if item:
            return jsonify({
                'success': False,
                'message': 'Product already exists'
            })
        
        product = Products(name=name, price=float(price), quantity_available=float(quantity_available), unit=unit)
        product.insert()

        return jsonify({
            'success': True,
            'created': product.id,
            'name': product.name,
            'price': product.price,
            'quantity_available': product.quantity_available,
            'unit': product.unit
        })
    except:
        abort(422)
        
@main.route("/products/<id>/update", methods=['PATCH'])
@requires_auth('patch:product')
def update_product(tk, id):
    body = request.get_json()

    try:
        product = Products.query.filter(Products.id==id).one_or_none()

        if product is None:
            abort(404)

        if 'name' in body:
            product.name = body.get('name')

        if 'price' in body:
            product.price = body.get('price')

        if 'quantity_available' in body:
            product.quantity_available = body.get('quantity_available')

        if 'unit' in body:
            product.unit = body.get('unit')

        product.update()

        return jsonify({
            'success': True,
            'product': product.format()
        })
    except:
        abort(400)

@main.route("/products/<id>/delete", methods=['DELETE'])
@requires_auth('delete:product')
def delete_product(tk, id):
    try:
        product = Products.query.filter(Products.id==id).one_or_none()

        if product is None:
            abort(404)
        
        product.delete()

        return jsonify({
            'success': True,
            'deleted': product.name
        })
    except:
        abort(422)

@main.route("/sales-record")
@requires_auth('get:salesrecord')
def get_sales_record(tk):
    query = Sales_record.query.all()
    records = [record.format() for record in query]

    if len(records)==0:
        abort(404)

    details = []

    for r in records:
        query = Product_sales.query.filter(Product_sales.record_id==r['id'])
        detail = [detail.format() for detail in query]

        details.append(detail)
   
    return jsonify({
        'success': True,
        'records': [
            {
                'customer_name': r['customer_name'],
                'total_price': r['total_price'],
                'date': r['date'],
                'products_sale': details[i]
            } for i, r in enumerate(records)
        ] 
    })


@main.route("/sales-record/new", methods=['POST'])
@requires_auth('get:productsales') #get:product sales permission for selling
def insert_sales_record(tk):
    body = request.get_json()

    customer_name = body.get('customer_name')
    total_price = body.get('total_price')
    date = datetime.today()

    if customer_name is None or total_price is None:
        return jsonify({
            'success': False,
            'message': "Missing Fields"
        })
    
    try:
        record = Sales_record(customer_name=customer_name, total_price=float(total_price), date=date)
        
        record.insert()

        products = body.get('products')
        if products is None:
            return jsonify({
                'success': False,
                'message': "Product Details not Supplied"
            })
    
        for p in products:
            try:
                product_sale = Product_sales(product_id=p['id'], product_name=p['name'], product_price=p['price'] , 
                                             quantity_bought=float(p['quantity_bought']), record_id=record.id)
                  
                product_sale.insert()

                # TODO NEXT - update product quantity available when product is bought
                try:
                    product = Products.query.filter(Products.id==product_sale.product_id).first()
                    if product is None:
                        abort(404)
                    print(product)
                    product.quantity_available = product.quantity_available - product_sale.quantity_bought
                    product.update()
                    p["remaining_quantity_available"] = product.quantity_available
                except:
                    print(sys.exc_info())
                    product.reverse()
                    abort(400)
            except:
                print(sys.exc_info())
                product_sale.reverse()
                record.reverse()
                abort(422)
            

        return jsonify({
            'success': True,
            'customer_name': record.customer_name,
            'date': record.date,
            'total_price': record.total_price,
            'products': [{'id': product['id'], 'name': product['name'], 'price': product['price'], 'quantity_bought': product['quantity_bought'], 'remaining_quantity_available': product['remaining_quantity_available']} for product in products]
        })

    except:
        print(sys.exc_info())
        record.reverse()
        abort(422)