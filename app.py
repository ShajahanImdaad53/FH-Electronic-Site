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
    category_filter = request.args.get('category', '')
    
    query = Product.query
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))
    if category_filter:
        query = query.filter(Product.category == category_filter)
        
    products = query.all()
    
    # Get all unique categories for the filter buttons
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template("shop.html", products=products, search_query=search_query, categories=categories, active_category=category_filter)

@app.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product.html", product=product)

@app.route("/cart")
def cart():
    return render_template("cart.html")

if __name__ == "__main__":
    app.run(debug=True)
