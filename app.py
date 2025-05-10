from flask import  Flask, render_template, request, redirect, url_for , session , flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user , login_user
from flask_migrate import Migrate
from werkzeug.security import check_password_hash
from datetime import datetime
import os




app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SECRET_KEY'] = '###'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


migrate = Migrate(app, db)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class LoginHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='login_history', lazy=True)

    def __repr__(self):
        return f'<LoginHistory {self.action} by User {self.user_id} at {self.timestamp}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, nullable=True)
    image_filename = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 

    def __repr__(self):
        return f'<Product {self.name}>'

# class Order(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
#     product = db.relationship('Product', backref='orders', lazy=True)
#     customer_name = db.Column(db.String(150), nullable=False)
#     phone_number = db.Column(db.String(20), nullable=False)
#     address = db.Column(db.Text, nullable=False)
#     quantity = db.Column(db.Integer, nullable=False)
#     price = db.Column(db.Float, nullable=False)
#     shipping_cost = db.Column(db.Integer, default=0)
#     discount = db.Column(db.Float, default=0.0)
#     total_price = db.Column(db.Float, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def __repr__(self):
#         return f'<Order {self.product.name} - {self.customer_name}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    customer_name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    shipping_cost = db.Column(db.Integer, default=0)
    discount = db.Column(db.Float, default=0.0)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # علاقة مع `Product` لجلب اسم المنتج بسهولة
    product = db.relationship('Product', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f'<Order {self.product_id} - {self.customer_name}>'

    
with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


with app.app_context():
    db.create_all()

app.secret_key = 'mohamed_store@3030'  

# Start Store
@app.route('/')
def index():
    products = Product.query.limit(10).all()
    return render_template('store/index.html' , products=products)

@app.route('/product')
def product():
    products = Product.query.all()
    return render_template('store/product.html', products=products)


@app.route('/product_details/<int:product_id>')
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('store/product_details.html', product=product)


@app.route('/purchase_order/<int:product_id>')
def purchase_order(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('store/purchase_order.html', product=product)


@app.route('/checkout')
def checkout():
    return render_template('store/checkout.html')

@app.route('/search', methods=['GET'])
def search_product():
    product_name = request.args.get('product_name')
    if product_name:
        products = Product.query.filter(Product.name.ilike(f"%{product_name}%")).all()
        return render_template('store/search_results.html', products=products)
    else:
        flash('الرجاء إدخال اسم منتج للبحث عنه.', 'danger')
        return redirect(url_for('index'))

#End Store

# Start CRM
@app.route('/crm/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:  
            login_user(user)
            login_history = LoginHistory(user_id=user.id, action="login", timestamp=datetime.utcnow())
            db.session.add(login_history)
            db.session.commit()
            next_page = request.args.get('next')  
            return redirect(next_page or url_for('home'))
        else:
            return "فشل تسجيل الدخول، حاول مرة أخرى."
    
    return render_template('CRM/login/login.html')


@app.route('/crm/logout')
@login_required
def logout():
    login_history = LoginHistory(user_id=current_user.id, action="logout", timestamp=datetime.utcnow())
    db.session.add(login_history)
    db.session.commit()
    
    logout_user()
    return redirect(url_for('login'))


@app.route('/crm/login-history')
@login_required
def login_history():
    history = LoginHistory.query.filter_by(user_id=current_user.id).order_by(LoginHistory.timestamp.desc()).all()
    return render_template('CRM/login/login_history.html', history=history)


@app.route('/crm/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('CRM/login/signup.html', error_message="Passwords do not match!")
        

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('home'))
    return render_template('CRM/login/signup.html')


@app.route('/crm')
@login_required
def home():
    return render_template('CRM/home/index.html')

@app.route('/crm/products/create_products', methods=['GET', 'POST'])
@login_required
def create_products():
    if request.method == 'POST':
        product_name = request.form['productName']
        product_description = request.form['productDescription']
        product_price = request.form['productPrice']
        product_old_price = request.form['productOldPrice']
        product_image = request.files['productImage']
    
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f"{product_name}_{timestamp}_{product_image.filename}"

        product_image.save(os.path.join('./static/products', image_filename))

        new_product = Product(
            name=product_name,
            description=product_description,
            price=product_price,
            old_price=product_old_price if product_old_price else None,
            image_filename=image_filename
        )
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('products')) 

    return render_template('CRM/products/add_products.html')

@app.route('/crm/products/products')
@login_required 
def products():
    products = Product.query.all() 
    return render_template('CRM/products/products.html', products=products)

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':

        product.name = request.form['productName']
        product.description = request.form['productDescription']
        product.price = float(request.form['productPrice'])
        product.old_price = float(request.form['productOldPrice'])


        if 'productImage' in request.files and request.files['productImage'].filename != '':
            product_image = request.files['productImage']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_filename = f"{product.name}_{timestamp}_{product_image.filename}"
            product_image.save(os.path.join('./static/products', image_filename))
            product.image_filename = image_filename  
        
        db.session.commit()
        return redirect(url_for('products')) 
    
    return render_template('CRM/products/edit_products.html', product=product)

@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('products'))  


@app.route('/crm/orders/create_orders', methods=['GET', 'POST'])
@login_required
def create_orders():
    products = Product.query.all()
    
    if request.method == 'POST':
        product_id = int(request.form['productName'])  
        customer_name = request.form['customerName']
        phone_number = request.form['phoneNumber']
        address = request.form['address']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        
        shipping = request.form.get('shipping', '')
        discount = request.form.get('discount', '')

        shipping = int(shipping) if shipping else 0
        discount = float(discount) if discount else 0

        final_price = price * quantity + shipping - discount


        product = Product.query.get(product_id)
        if not product:
            flash("المنتج غير موجود!", "danger")
            return redirect(url_for('orders'))  

        new_order = Order(
            product_id=product.id, 
            customer_name=customer_name,
            phone_number=phone_number,
            address=address,
            quantity=quantity,
            price=price,
            shipping_cost=shipping,
            discount=discount,
            total_price=final_price
        )

        db.session.add(new_order)
        db.session.commit()
        return redirect(url_for('orders'))

    return render_template('CRM/orders/add_orders.html', products=products)


@app.route('/crm/orders/orders', methods=['GET'])
@login_required
def orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()  
    return render_template('CRM/orders/orders.html', orders=orders)  

@app.route('/crm/customer_invoice/<int:order_id>')
@login_required
def customer_invoice(order_id):
    order = Order.query.get(order_id)   

    return render_template('CRM/orders/customer_invoice.html', order=order)


@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        order.product_name = request.form['productName']
        order.customer_name = request.form['customerName']
        order.phone_number = request.form['phoneNumber']
        order.address = request.form['address']
        order.quantity = int(request.form['quantity'])
        order.price = float(request.form['price'])
        order.shipping_cost = float(request.form.get('shipping', 0))
        order.discount = float(request.form.get('discount', 0))
        order.total_price = order.price + order.shipping_cost - order.discount
        db.session.commit()
        return redirect(url_for('orders'))
    return render_template('CRM/orders/edit_order.html', order=order)


@app.route('/delete_order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('orders'))

# End CRM

if __name__ == '__main__':
    app.run(debug=True)
