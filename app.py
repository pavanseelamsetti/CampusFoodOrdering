from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = "campus-bites-secret-key"


# =========================
# FOOD MENU
# =========================

FOODS = [
    {
        "id": 1,
        "name": "Veg Burger",
        "category": "Fast Food",
        "price": 80,
        "emoji": "🍔",
        "rating": 4.5,
        "desc": "Crispy vegetable patty with fresh lettuce and special sauce."
    },
    {
        "id": 2,
        "name": "Chicken Biryani",
        "category": "Meals",
        "price": 140,
        "emoji": "🍛",
        "rating": 4.7,
        "desc": "Aromatic basmati rice with spicy chicken and raita."
    },
    {
        "id": 3,
        "name": "Veg Pizza",
        "category": "Fast Food",
        "price": 120,
        "emoji": "🍕",
        "rating": 4.6,
        "desc": "Cheesy pizza topped with fresh vegetables."
    },
    {
        "id": 4,
        "name": "Masala Dosa",
        "category": "Breakfast",
        "price": 70,
        "emoji": "🥞",
        "rating": 4.4,
        "desc": "Crispy dosa served with potato masala and chutney."
    },
    {
        "id": 5,
        "name": "Noodles",
        "category": "Fast Food",
        "price": 100,
        "emoji": "🍜",
        "rating": 4.4,
        "desc": "Hot wok-tossed noodles with vegetables."
    },
    {
        "id": 6,
        "name": "Cold Coffee",
        "category": "Drinks",
        "price": 60,
        "emoji": "🥤",
        "rating": 4.5,
        "desc": "Chilled creamy coffee for a refreshing break."
    },
    {
        "id": 7,
        "name": "Samosa",
        "category": "Snacks",
        "price": 30,
        "emoji": "🥟",
        "rating": 4.3,
        "desc": "Golden crispy samosa with spicy potato filling."
    },
    {
        "id": 8,
        "name": "Paneer Roll",
        "category": "Snacks",
        "price": 90,
        "emoji": "🌯",
        "rating": 4.5,
        "desc": "Soft roll packed with spicy paneer and vegetables."
    }
]


# =========================
# CART
# =========================

def get_cart():

    return session.get("cart", {})


def get_cart_items():

    cart = get_cart()

    items = []
    total = 0

    for food_id, quantity in cart.items():

        food = next(
            (food for food in FOODS if food["id"] == int(food_id)),
            None
        )

        if food:

            item = food.copy()

            item["quantity"] = quantity

            item["subtotal"] = (
                food["price"] * quantity
            )

            total += item["subtotal"]

            items.append(item)

    return items, total


# =========================
# GLOBAL CART INFORMATION
# =========================

@app.context_processor
def cart_information():

    items, total = get_cart_items()

    cart_count = sum(
        item["quantity"]
        for item in items
    )

    return {
        "cart_count": cart_count,
        "cart_total": total
    }


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():

    category = request.args.get(
        "category",
        "All"
    )

    search = request.args.get(
        "q",
        ""
    ).strip().lower()

    foods = FOODS

    if category != "All":

        foods = [
            food for food in foods
            if food["category"] == category
        ]

    if search:

        foods = [
            food for food in foods
            if search in food["name"].lower()
            or search in food["category"].lower()
        ]

    categories = [
        "All",
        "Meals",
        "Fast Food",
        "Breakfast",
        "Snacks",
        "Drinks"
    ]

    return render_template(
        "index.html",
        foods=foods,
        categories=categories,
        selected=category,
        search=search
    )


# =========================
# ADD FOOD TO CART
# =========================

@app.route("/add/<int:food_id>", methods=["POST"])
def add_to_cart(food_id):

    food_exists = any(
        food["id"] == food_id
        for food in FOODS
    )

    if not food_exists:

        return redirect(
            url_for("home")
        )

    cart = get_cart()

    food_id = str(food_id)

    cart[food_id] = cart.get(
        food_id,
        0
    ) + 1

    session["cart"] = cart

    return redirect(
        request.referrer or
        url_for("home")
    )


# =========================
# CART PAGE
# =========================

@app.route("/cart")
def cart():

    items, total = get_cart_items()

    discount = 20 if total >= 200 else 0

    final_total = max(
        0,
        total - discount
    )

    return render_template(
        "cart.html",
        items=items,
        total=total,
        discount=discount,
        final_total=final_total
    )


# =========================
# UPDATE CART
# =========================

@app.route("/cart/update", methods=["POST"])
def update_cart():

    cart = get_cart()

    for food_id in list(cart.keys()):

        quantity = request.form.get(
            f"quantity_{food_id}",
            0
        )

        try:
            quantity = int(quantity)

        except ValueError:
            quantity = 0

        if quantity <= 0:

            cart.pop(
                food_id,
                None
            )

        else:

            cart[food_id] = min(
                quantity,
                20
            )

    session["cart"] = cart

    return redirect(
        url_for("cart")
    )


# =========================
# CLEAR CART
# =========================

@app.route("/cart/clear", methods=["POST"])
def clear_cart():

    session["cart"] = {}

    return redirect(
        url_for("cart")
    )


# =========================
# CHECKOUT
# =========================

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    items, total = get_cart_items()

    if not items:

        return redirect(
            url_for("home")
        )

    discount = 20 if total >= 200 else 0

    final_total = max(
        0,
        total - discount
    )

    if request.method == "POST":

        student_name = request.form.get(
            "student_name",
            "Student"
        )

        student_id = request.form.get(
            "student_id",
            "N/A"
        )

        pickup_location = request.form.get(
            "pickup_location",
            "Main Canteen Counter"
        )

        payment_method = request.form.get(
            "payment_method",
            "Cash at Counter"
        )

        note = request.form.get(
            "note",
            ""
        )

        order = {

            "id": "CB1025",

            "student_name": student_name,

            "student_id": student_id,

            "pickup_location": pickup_location,

            "payment_method": payment_method,

            "note": note,

            "total": final_total,

            "status": "Preparing",

            "items": items

        }

        session["last_order"] = order

        session["cart"] = {}

        return redirect(
            url_for("track_order")
        )

    return render_template(
        "checkout.html",
        items=items,
        total=total,
        discount=discount,
        final_total=final_total
    )


# =========================
# ORDER TRACKING
# =========================

@app.route("/track")
def track_order():

    order = session.get(
        "last_order"
    )

    if not order:

        return redirect(
            url_for("home")
        )

    return render_template(
        "track.html",
        order=order
    )


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin")
def admin():

    return render_template(
        "admin.html"
    )


# =========================
# FOOD API
# =========================

@app.route("/api/foods")
def food_api():

    return jsonify(
        FOODS
    )


# =========================
# START SERVER
# =========================

if __name__ == "__main__":

    app.run(
        debug=True
    )