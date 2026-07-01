from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "master_sewing_machine_house"

# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect("database.db")
    return conn

# ---------------- CART ----------------

def get_cart():
    if "cart" not in session:
        session["cart"] = {}
    return session["cart"]

# ---------------- HOME ----------------

@app.route("/")
def home():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        image TEXT
)
""")

    search = request.args.get("search", "")
    category = request.args.get("category", "")

    if search:

        cursor.execute(
            "SELECT * FROM products WHERE name LIKE ?",
            ('%' + search + '%',)
        )

    elif category == "machines":

        cursor.execute(
            "SELECT * FROM products WHERE name LIKE '%Machine%'"
        )

    elif category == "spares":

        cursor.execute("""
        SELECT * FROM products
        WHERE name LIKE '%Bobbin%'
        OR name LIKE '%Needle%'
        OR name LIKE '%Presser%'
        OR name LIKE '%Belt%'
        OR name LIKE '%Thread%'
        """)

    elif category == "oil":

        cursor.execute(
            "SELECT * FROM products WHERE name LIKE '%Oil%'"
        )

    elif category == "iron":

        cursor.execute(
            "SELECT * FROM products WHERE name LIKE '%Iron%'"
        )

    else:

        cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    cart = session.get("cart", {})

    if isinstance(cart, list):
        cart = {}
        session["cart"] = cart

    total_items = 0
    total_bill = 0

    for pid, qty in cart.items():

        total_items += qty

        cursor.execute(
            "SELECT price FROM products WHERE id=?",
            (int(pid),)
        )

        row = cursor.fetchone()

        if row:
            total_bill += row[0] * qty

    conn.close()

    return render_template(
        "index.html",
        products=products,
        total_items=total_items,
        total_bill=total_bill
    )

# ---------------- INIT PRODUCTS ----------------

@app.route("/init")
def init():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products")

    items = [
        ("Singer Sewing Machine",12000, "images/singer.jpg"),
        ("Usha Janome Sewing Machine",14500,"images/usha.jpg" ),
        ("Brother Sewing Machine",25000, "images/brother.jpg"),
        ("Jack Industrial Machine",38000,"images/jack.jpg"),
        ("Juki Industrial Machine",42000, "images/juki.jpg"),
        ("Overlock Machine",28000, "images/overlock.jpg"),
        ("Interlock Machine",45000, "images/interlock.jpg"),
        ("Embroidery Machine",65000, "images/embroidery.jpg"),
        ("Bobbin",50, "images/bobbin.jpg"),
        ("Bobbin Case",180, "images/bobbincase.jpg"),
        ("Needle Pack",120, "images/needle.jpg"),
        ("Presser Foot",250,"images/foot.jpg"),
        ("Machine Belt",180, "images/belt.jpg"),
        ("Machine Oil",120, "images/oil.jpg"),
        ("Tailor Scissors",650, "images/scissors.jpg"),
        ("Steam Iron Box",3500, "images/iron.jpg"),
        ("Thread Cone",180, "images/thread.jpg")
    ]

    cursor.executemany(
        "INSERT INTO products(name,price, image) VALUES(?,?,?)",
        items
    )

    conn.commit()
    conn.close()

    return redirect("/")


# ---------------- ADD TO CART ----------------

@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):

    cart = get_cart()

    pid = str(id)

    if pid in cart:
        cart[pid] += 1
    else:
        cart[pid] = 1

    session["cart"] = cart

    return redirect("/")


# ---------------- BUY ----------------

@app.route("/buy/<int:id>")
def buy(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE id=?", (id,))
    product = cursor.fetchone()

    conn.close()

    return render_template("buy.html", product=product)


# ---------------- CART ----------------

@app.route("/cart")
def cart():

    cart = get_cart()

    conn = get_db()
    cursor = conn.cursor()

    cart_products = []
    total_bill = 0
    total_items = 0

    for pid, qty in cart.items():

        cursor.execute(
            "SELECT * FROM products WHERE id=?",
            (int(pid),)
        )

        product = cursor.fetchone()

        if product:

            subtotal = product[2] * qty

            cart_products.append({
                "id": product[0],
                "name": product[1],
                "price": product[2],
                "qty": qty,
                "subtotal": subtotal
            })

            total_bill += subtotal
            total_items += qty

    conn.close()

    return render_template(
        "cart.html",
        cart_products=cart_products,
        total_items=total_items,
        total_bill=total_bill
    )


# ---------------- INCREASE ----------------

@app.route("/increase/<int:id>")
def increase(id):

    cart = get_cart()

    pid = str(id)

    if pid in cart:
        cart[pid] += 1

    session["cart"] = cart

    return redirect("/cart")


# ---------------- DECREASE ----------------

@app.route("/decrease/<int:id>")
def decrease(id):

    cart = get_cart()

    pid = str(id)

    if pid in cart:

        cart[pid] -= 1

        if cart[pid] <= 0:
            del cart[pid]

    session["cart"] = cart

    return redirect("/cart")


# ---------------- REMOVE ----------------

@app.route("/remove/<int:id>")
def remove(id):

    cart = get_cart()

    pid = str(id)

    if pid in cart:
        del cart[pid]

    session["cart"] = cart

    return redirect("/cart")


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
