from flask import render_template, redirect, request, flash, session, url_for, jsonify, send_from_directory
from config import app, db, admin_password
from forms import RegistrationForm, LoginForm, AddProduct, EditProduct
from models import Product, Category, User, Cart, Like
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import exc
import os

app.config.from_object('config')

@app.route('/')
def index():
    top_liked_products = db.session.query(
        Product, db.func.count(Like.id).label('likes')
    ).join(Like).group_by(Product.id).order_by(db.desc('likes')).limit(3).all()

    return render_template('index.html', top_liked_products=top_liked_products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email is already registered!', 'danger')
            return render_template('register.html', form=form)
        if form.role.data == 'admin':
            if form.password.data != admin_password:
                flash('Invalid admin password!', 'danger')
                return render_template('register.html', form=form)
            else:
                user = User(username=form.username.data, email=form.email.data, role=form.role.data)
                user.set_password(form.password.data)
                db.session.add(user)
                db.session.commit()
                flash('Admin registration was successful!', 'success')
                login_user(user)
                return redirect(url_for('index'))        
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration was successful!', 'success')
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
            
            if user is None:
                flash('Invalid username, email, or password', category='danger')
                return render_template("login.html", form=form)
            
            if form.password.data == admin_password:
                if user.role != 'admin':
                    flash('Invalid admin credentials', category='danger')
                    return render_template("login.html", form=form)
                login_user(user)
                flash('Successfully logged in as admin', category='success')
                return redirect(url_for('index'))
            elif user.check_password(form.password.data):
                login_user(user)
                flash('Successfully logged in', category='success')
                return redirect(url_for('index'))
            
            flash('Invalid username, email, or password', category='danger')
        except Exception as e:
            app.logger.error(f"Login error: {e}")
            flash('An error occurred during login. Please try again.', 'danger')
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/shop')
def shop():
    query = request.args.get('q')
    if query:
        products = Product.query.filter(Product.name.contains(query)).all()
    else:
        products = Product.query.all()

    if current_user.is_authenticated:
        liked_products = {like.product_id for like in current_user.likes}
    else:
        liked_products = set()

    return render_template('shop.html', products=products, liked_products=liked_products)

@app.route("/category/<int:category_id>")
def category(category_id):
    current_category = Category.query.get_or_404(category_id)
    products = current_category.product_id
    return render_template("shop.html", products=products)

@app.route('/details/<int:id>')
def details(id):
    product = Product.query.get_or_404(id)
    return render_template("details.html", product=product)

@app.route("/charity")
def charity():
    return render_template("charity.html")

@app.route("/about-us")
def about_us():
    return render_template("about.html")

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=1)
        db.session.add(cart_item)
    db.session.commit()
    flash('Item added to cart', category='success')
    return redirect(request.referrer)

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        if product_id:
            cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
            if cart_item:
                cart_item.quantity += 1
                flash('Item quantity updated', category='success')
            else:
                new_cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=1)
                db.session.add(new_cart_item)
                flash('Item added to cart', category='success')
            db.session.commit()
        else:
            flash('Invalid product ID', category='error')
        return redirect(url_for('cart'))

    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total_cart_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_cart_price=total_cart_price)

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart', category='success')
    else:
        flash('Item not found in cart', category='danger')
    return redirect(url_for('cart'))

@app.route('/like_product', methods=['POST'])
def like_product():
    product_id = request.json.get('product_id')
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    like = Like.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({"message": "Product unliked", "liked": False})
    else:
        new_like = Like(user_id=current_user.id, product_id=product_id)
        db.session.add(new_like)
        db.session.commit()
        return jsonify({"message": "Product liked", "liked": True})


@app.route("/addproduct", methods=["GET", "POST"])
def add_product():
    form = AddProduct()
    if form.validate_on_submit():
        file = form.file.data
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Ensure correct path
            file.save(file_path)

        category_id = form.category.data
        category = Category.query.get(category_id)

        if not category:
            flash("Invalid category selected. Please select a valid category.", category="danger")
            return redirect(url_for('add_product'))

        product = Product(
            name=form.name.data,
            price=form.price.data,
            file='/static/' + filename,  # Use relative path
            category=category
        )

        db.session.add(product)
        db.session.commit()
        flash("You successfully added the product", category="success")
        return redirect("/shop")

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", category="danger")

    return render_template("addproduct.html", form=form)

@app.route("/uploadfile", methods=["GET", "POST"])
def upload_file():
    form = AddProduct()
    if form.validate_on_submit():
        file = form.file.data
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Ensure correct path
            file.save(file_path)

            obj = Product(
                name=form.name.data,
                price=form.price.data,
                file='/static/' + filename  # Use relative path
            )

            db.session.add(obj)
            db.session.commit()
            flash("You successfully added the product", category="success")
            return redirect("/")
    if form.errors:
        flash("You didn't add the product properly", category="danger")
    return render_template("addproduct.html", form=form)

@app.route("/delete/<int:id>")
def delete_product(id):
    product = Product.query.get(id)
    if product:
        try:
            db.session.delete(product)
            db.session.commit()
        except exc.IntegrityError as e:
            db.session.rollback()
            return f"Failed to delete product: {str(e)}\n  (probably someone has it in cart)"
    return redirect(url_for('shop'))

@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = EditProduct(obj=product)  # Populate form with existing product data

    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        category_id = form.category.data
        product.category = Category.query.get(category_id)

        if form.file.data:
            file = form.file.data
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.file = '/static/' + filename  # Assuming 'static' is your static files directory

        db.session.commit()
        flash("Product successfully updated", category="success")
        return redirect(url_for('shop'))  # Redirect to shop page after editing

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", category="danger")

    return render_template('editproduct.html', form=form, product=product)

if __name__ == "__main__":
    app.run(debug=True)
