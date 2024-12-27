from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"

ADMIN_USERNAME = "gttadmin"
ADMIN_PASSWORD = "admin123"

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db_connection()
        table_exists = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='products';"
        ).fetchone()
        if not table_exists:
            with open('schema.sql', 'r') as f:
                db.executescript(f.read())
            db.commit()

            products = [
                {"name": "Gaming PC Pro", "price": 1200, "category": "PCs", "image": "images/pc1.webp"},
                {"name": "Office PC", "price": 800, "category": "PCs", "image": "images/pc22.webp"},
                {"name": "Budget Gaming PC", "price": 600, "category": "PCs", "image": "images/pc3.webp"},
            ]

            for product in products:
                db.execute(
                    "INSERT INTO products (name, price, category, image) VALUES (?, ?, ?, ?)",
                    (product["name"], product["price"], product["category"], product["image"])
                )
            db.commit()
            print("Default products added.")
        else:
            print("Database already initialized.")

def setup():
    init_db()

setup()

@app.route("/")
def home():
    conn = get_db_connection()
    category = request.args.get("category")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    query = "SELECT * FROM products WHERE 1=1"
    params = []
#Product.query.all()
    if category:
        query += " AND category = ?"
        params.append(category)
    if min_price is not None:
        query += " AND price >= ?"
        params.append(min_price)
    if max_price is not None:
        query += " AND price <= ?"
        params.append(max_price)
    query+= " ORDER BY price Desc;"
    print(query)

    products = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("index.html", products=products)

@app.route("/product/<int:product_id>", methods=["GET", "POST"])
def product(product_id):
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        if "comment" in request.form:
            comment = request.form.get("comment")
            username = session.get("username", "Guest")
            conn.execute("INSERT INTO comments (product_id, username, text) VALUES (?, ?, ?)",
                         (product_id, username, comment))
            conn.commit()
            flash("Comment added!", "success")
        else:
            session.setdefault("cart", []).append(dict(product))
            session.modified = True
            flash(f"{product['name']} has been added to your cart.", "success")
            return redirect(url_for("cart"))

    comments = conn.execute("SELECT * FROM comments WHERE product_id = ?", (product_id,)).fetchall()
    conn.close()
    return render_template("product.html", product=product, comments=comments)

@app.route("/cart", methods=["GET", "POST"])
def cart():
    if request.method == "POST":
        if "checkout" in request.form:
            if session.get("cart"):
                session.pop("cart", None)
                flash("Thank you for your purchase!", "success")
            else:
                flash("Your cart is empty.", "danger")

        elif "remove" in request.form:
            product_id = int(request.form.get("remove"))
            session["cart"] = [item for item in session["cart"] if item["id"] != product_id]
            session.modified = True
            flash("Item removed from cart.", "success")

    return render_template("cart.html", cart=session.get("cart", []))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["username"] = username
            flash("Welcome Admin!", "success")
            return redirect(url_for("admin_panel"))
        elif user and user["password"] == password:
            session["username"] = username
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user:
            flash("Username already exists.", "danger")
        else:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("cart", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if session.get("username") != ADMIN_USERNAME:
        flash("Access denied!", "danger")
        return redirect(url_for("home"))

    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()

    if request.method == "POST":
        if "add_product" in request.form:
            name = request.form.get("name")
            price = request.form.get("price")
            category = request.form.get("category")
            image = request.form.get("image")

            if not image.startswith("images/"):
                image = f"images/{image}"

            conn.execute("INSERT INTO products (name, price, category, image) VALUES (?, ?, ?, ?)",
                         (name, price, category, image))
            conn.commit()
            flash("Product added successfully!", "success")
        elif "delete_product" in request.form:
            product_id = request.form.get("delete_product")
            conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            flash("Product deleted successfully!", "success")
    conn.close()
    return render_template("admin.html", products=products)

@app.route("/upload", methods=["POST"])
def upload_image():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('admin_panel'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('admin_panel'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash("Image uploaded successfully!", "success")
    else:
        flash("Invalid file type.", "danger")

    return redirect(url_for('admin_panel'))

@app.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if session.get("username") != ADMIN_USERNAME:
        flash("Access denied!", "danger")
        return redirect(url_for("home"))

    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()

    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for("admin_panel"))

    if request.method == "POST":
        name = request.form.get("name")
        price = request.form.get("price")
        category = request.form.get("category")
        image = request.form.get("image")

        conn.execute(
            "UPDATE products SET name = ?, price = ?, category = ?, image = ? WHERE id = ?",
            (name, price, category, image, product_id),
        )
        conn.commit()
        conn.close()
        flash("Product updated successfully!", "success")
        return redirect(url_for("admin_panel"))

    conn.close()
    return render_template("edit_product.html", product=product)

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/checkout", methods=["POST"])
def checkout():
    full_name = request.form.get("full_name")
    address = request.form.get("address")
    card_number = request.form.get("card_number")
    expiration_date = request.form.get("expiration_date")
    cvv = request.form.get("cvv")

    if session.get("cart"):
        session.pop("cart", None)
        flash(f"Thank you for your purchase, {full_name}!", "success")
        return redirect(url_for("home"))
    else:
        flash("Your cart is empty.", "danger")
        return redirect(url_for("cart"))

if __name__ == "__main__":
    app.run(debug=True)
