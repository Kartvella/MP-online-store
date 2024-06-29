from config import app, db, login_manager
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    file = db.Column(db.String)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    likes = db.relationship('Like', cascade='all, delete-orphan', back_populates='product')

    def __str__(self):
        return f"{self.name}"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    product_id = db.relationship("Product", backref='category', lazy=True)

    def __str__(self):
        return f"{self.name}"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(40), unique=True)
    password_hash = db.Column(db.String(40))
    role = db.Column(db.String)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    user = db.relationship('User', backref=db.backref('cart', lazy=True))
    product = db.relationship('Product', backref=db.backref('cart', lazy=True))

    def __repr__(self):
        return f'<Cart {self.user_id} {self.product_id} {self.quantity}>'

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('likes', lazy=True))
    product = db.relationship('Product', back_populates='likes')

    def __repr__(self):
        return f'<Like {self.user_id} {self.product_id}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        goggles = Category(name="სათვალეები")
        caps = Category(name="ქუდები")
        techsuits = Category(name="ჯამერები")

        db.session.add_all([goggles, caps, techsuits])

        products = [Product( name="MP XCEED",price="100", file="/static/goggle1.jpg", category=goggles),
        Product(name="MP XCEED",price="100", file="/static/goggle2.jpg", category=goggles),
        Product(name="MP XCEED",price="100", file="/static/goggle3.jpg", category=goggles),
        Product(name="MP XCEED",price="100", file="/static/goggle4.jpg", category=goggles),
        Product(name="MP XCEED",price="100", file="/static/goggle5.jpg", category=goggles),
        Product(name="MP XCEED",price="100", file="/static/goggle6.jpg", category=goggles),
        Product(name="MP XCEED",price="100", file="/static/goggle7.jpg", category=goggles),
        Product(name="MP XCEED",price="100", file="/static/goggle8.jpg", category=goggles),
        Product(name="MP cap",price="50", file="/static/MPcap.jpg", category=caps),
        Product(name="MP cap",price="50", file="/static/MPcap2.jpg", category=caps),
        Product(name="MP cap",price="50", file="/static/MPcap3.jpg", category=caps),
        Product(name="MP cap",price="50", file="/static/MPcap4.jpg", category=caps),
        Product(name="MP cap",price="50", file="/static/MPcap5.jpg", category=caps),
        Product(name="MP cap",price="50", file="/static/MPcap6.webp", category=caps),
        Product(name="MP cap",price="50", file="/static/MPcap7.jpg", category=caps),
        Product(name="MP Tech suit",price="200", file="/static/MPsuit.jpg", category=techsuits),
        Product(name="MP Tech suit",price="200", file="/static/MPsuit2.webp", category=techsuits),
        Product(name="MP Tech suit",price="200", file="/static/MPsuit3.webp", category=techsuits),
        Product(name="MP Tech suit",price="200", file="/static/MPsuit4.png", category=techsuits),
        Product(name="MP Tech suit",price="200", file="/static/MPsuit5.jpg", category=techsuits)]

        db.session.add_all(products)
        db.session.commit()