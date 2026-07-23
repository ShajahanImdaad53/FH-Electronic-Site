from flask import Flask, render_template
from config import Config
from models import db, Product
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    if not os.path.exists("instance"):
        os.makedirs("instance")
    db.create_all()

    if Product.query.count() == 0:
        demo_products = [
            Product(name="Baseus Charger", price=2500, image="images/p1.jpg"),
            Product(name="Baseus Cable", price=1200, image="images/p2.jpg"),
            Product(name="Baseus Power Bank", price=8500, image="images/p3.jpg"),
        ]
        db.session.add_all(demo_products)
        db.session.commit()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/shop")
def shop():
    from flask import request
    search_query = request.args.get('q', '')
    if search_query:
        products = Product.query.filter(Product.name.ilike(f'%{search_query}%')).all()
    else:
        products = Product.query.all()
    return render_template("shop.html", products=products, search_query=search_query)

@app.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product.html", product=product)

@app.route("/cart")
def cart():
    return render_template("cart.html")

if __name__ == "__main__":
    app.run(debug=True)
