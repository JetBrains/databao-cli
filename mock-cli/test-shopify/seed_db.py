"""
Generate realistic Shopify-like data and seed it into shopify.duckdb.
Tables created: orders, order_lines, order_discount_codes, customers,
                products, product_variants, inventory_levels,
                refunds, transactions
"""
import random
import string
from datetime import datetime, timedelta
from pathlib import Path

import duckdb

SEED = 42
random.seed(SEED)

DB_PATH = Path(__file__).parent / "shopify.duckdb"


def rand_date(start: datetime, end: datetime) -> datetime:
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))


def rand_email(first: str, last: str) -> str:
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"]
    return f"{first.lower()}.{last.lower()}{random.randint(1,99)}@{random.choice(domains)}"


# ── constants ────────────────────────────────────────────────────────────────

START = datetime(2023, 1, 1)
END   = datetime(2024, 12, 31)

FIRST_NAMES = ["Emma","Liam","Olivia","Noah","Ava","Oliver","Sophia","Elijah",
               "Isabella","James","Mia","Aiden","Charlotte","Lucas","Amelia",
               "Mason","Harper","Logan","Evelyn","Ethan","Abigail","Jackson",
               "Emily","Sebastian","Elizabeth","Carter","Chloe","Owen","Sofia"]

LAST_NAMES  = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller",
               "Davis","Wilson","Taylor","Anderson","Thomas","Jackson","White",
               "Harris","Martin","Thompson","Young","Robinson","Lewis","Lee"]

PRODUCT_TYPES = ["Apparel", "Accessories", "Footwear", "Home & Garden", "Electronics", "Beauty"]
VENDORS       = ["Nike", "Adidas", "Zara", "H&M", "ASOS", "Gucci", "Prada", "Uniqlo"]
GATEWAYS      = ["stripe", "paypal", "shopify_payments", "amazon_pay"]
FINANCIAL_STATUSES     = ["paid", "paid", "paid", "paid", "refunded", "pending"]
FULFILLMENT_STATUSES   = ["fulfilled", "fulfilled", "unfulfilled", "partial", None]
DISCOUNT_CODES = ["SUMMER20", "WELCOME10", "FLASH50", "VIP15", "SALE30",
                  "NEW25", "LOYAL5", "HOLIDAY20", "BACK2SCHOOL", "CYBER15"]


# ── generate data ─────────────────────────────────────────────────────────────

def make_customers(n=500):
    rows = []
    for i in range(1, n + 1):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        created = rand_date(START, END)
        rows.append((
            i, rand_email(fn, ln), fn, ln,
            created, 0, 0.0, random.choice([True, False])
        ))
    return rows


def make_products(n=80):
    adjectives = ["Classic","Premium","Slim","Bold","Urban","Vintage","Modern","Luxe"]
    nouns      = ["Tee","Jacket","Sneaker","Bag","Watch","Cap","Hoodie","Shorts","Dress","Belt"]
    rows = []
    for i in range(1, n + 1):
        title = f"{random.choice(adjectives)} {random.choice(nouns)}"
        created = rand_date(START, END - timedelta(days=90))
        rows.append((
            i, title,
            random.choice(VENDORS),
            random.choice(PRODUCT_TYPES),
            created,
            random.choice(["active", "active", "active", "archived", "draft"]),
            ",".join(random.sample(["sale","new","trending","bestseller","clearance"], k=random.randint(1,3)))
        ))
    return rows


def make_product_variants(products):
    sizes   = ["XS","S","M","L","XL","XXL"]
    colors  = ["Black","White","Navy","Red","Green","Grey"]
    rows = []
    vid = 1
    for pid, *_ in products:
        n_variants = random.randint(1, 6)
        for _ in range(n_variants):
            title = f"{random.choice(sizes)} / {random.choice(colors)}"
            sku = "SKU-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            price = round(random.uniform(15, 350), 2)
            rows.append((vid, pid, title, price, sku, random.randint(0, 200), round(random.uniform(0.1, 2.5), 2)))
            vid += 1
    return rows


def make_inventory_levels(variants):
    rows = []
    location_ids = [1, 2, 3]
    for vid, *rest in variants:
        for loc in random.sample(location_ids, k=random.randint(1, 3)):
            rows.append((vid, loc, random.randint(0, 150), datetime.now()))
    return rows


def make_orders_and_lines(customers, variants, products, n=2000):
    prod_map    = {p[0]: p for p in products}
    variant_map = {v[0]: v for v in variants}

    orders, order_lines, order_discount_codes = [], [], []
    refunds, transactions = [], []

    oid, olid, rid, tid = 1, 1, 1, 1

    # update customer stats inline
    cust_orders = {c[0]: [] for c in customers}

    for _ in range(n):
        cust = random.choice(customers)
        cid  = cust[0]
        created = rand_date(START, END)

        fin_status  = random.choice(FINANCIAL_STATUSES)
        ful_status  = random.choice(FULFILLMENT_STATUSES)
        currency    = "USD"
        gateway     = random.choice(GATEWAYS)

        # pick 1-5 variants for this order
        n_lines   = random.randint(1, 5)
        picked    = random.sample(variants, k=n_lines)
        subtotal  = sum(v[3] * random.randint(1, 3) for v in picked)
        shipping  = round(random.uniform(0, 15), 2)
        total     = round(subtotal + shipping, 2)

        orders.append((
            oid, cid, created, round(total, 2), round(subtotal, 2),
            fin_status, ful_status, currency, cust[1]
        ))
        cust_orders[cid].append((total, created))

        for v in picked:
            qty   = random.randint(1, 3)
            price = v[3]
            pid   = v[1]
            olid_val = olid
            order_lines.append((olid, oid, pid, v[0], qty, price,
                                 prod_map[pid][1], v[4]))
            olid += 1

        # discount code (30% chance)
        if random.random() < 0.3:
            order_discount_codes.append((oid, random.choice(DISCOUNT_CODES)))

        # refund (if refunded)
        if fin_status == "refunded":
            refunds.append((rid, oid, created + timedelta(days=random.randint(1, 14)),
                            "Customer request", random.choice([True, False])))
            rid += 1

        # transaction
        if fin_status in ("paid", "refunded"):
            transactions.append((tid, oid, total, currency, "sale", "success", gateway, created))
            tid += 1
            if fin_status == "refunded":
                transactions.append((tid, oid, total, currency, "refund", "success", gateway,
                                      created + timedelta(days=random.randint(1, 14))))
                tid += 1

        oid += 1

    # patch customer orders_count / total_spent
    updated_customers = []
    for c in customers:
        history = cust_orders[c[0]]
        orders_count = len(history)
        total_spent  = round(sum(h[0] for h in history), 2)
        updated_customers.append(c[:5] + (orders_count, total_spent) + c[7:])

    return updated_customers, orders, order_lines, order_discount_codes, refunds, transactions


# ── write to duckdb ───────────────────────────────────────────────────────────

def seed(db_path: Path):
    print(f"Generating data...")
    customers_raw = make_customers(500)
    products      = make_products(80)
    variants      = make_product_variants(products)
    inventory     = make_inventory_levels(variants)
    customers, orders, order_lines, order_discount_codes, refunds, transactions = \
        make_orders_and_lines(customers_raw, variants, products, n=3000)

    print(f"  customers:           {len(customers)}")
    print(f"  products:            {len(products)}")
    print(f"  product_variants:    {len(variants)}")
    print(f"  inventory_levels:    {len(inventory)}")
    print(f"  orders:              {len(orders)}")
    print(f"  order_lines:         {len(order_lines)}")
    print(f"  order_discount_codes:{len(order_discount_codes)}")
    print(f"  refunds:             {len(refunds)}")
    print(f"  transactions:        {len(transactions)}")

    con = duckdb.connect(str(db_path))

    con.execute("DROP TABLE IF EXISTS customers")
    con.execute("""
        CREATE TABLE customers (
            id INTEGER, email VARCHAR, first_name VARCHAR, last_name VARCHAR,
            created_at TIMESTAMP, orders_count INTEGER, total_spent DOUBLE,
            accepts_marketing BOOLEAN
        )
    """)
    con.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?,?,?)", customers)

    con.execute("DROP TABLE IF EXISTS products")
    con.execute("""
        CREATE TABLE products (
            id INTEGER, title VARCHAR, vendor VARCHAR, product_type VARCHAR,
            created_at TIMESTAMP, status VARCHAR, tags VARCHAR
        )
    """)
    con.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?)", products)

    con.execute("DROP TABLE IF EXISTS product_variants")
    con.execute("""
        CREATE TABLE product_variants (
            id INTEGER, product_id INTEGER, title VARCHAR, price DOUBLE,
            sku VARCHAR, inventory_quantity INTEGER, weight DOUBLE
        )
    """)
    con.executemany("INSERT INTO product_variants VALUES (?,?,?,?,?,?,?)", variants)

    con.execute("DROP TABLE IF EXISTS inventory_levels")
    con.execute("""
        CREATE TABLE inventory_levels (
            inventory_item_id INTEGER, location_id INTEGER,
            available INTEGER, updated_at TIMESTAMP
        )
    """)
    con.executemany("INSERT INTO inventory_levels VALUES (?,?,?,?)", inventory)

    con.execute("DROP TABLE IF EXISTS orders")
    con.execute("""
        CREATE TABLE orders (
            id INTEGER, customer_id INTEGER, created_at TIMESTAMP,
            total_price DOUBLE, subtotal_price DOUBLE,
            financial_status VARCHAR, fulfillment_status VARCHAR,
            currency VARCHAR, email VARCHAR
        )
    """)
    con.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?)", orders)

    con.execute("DROP TABLE IF EXISTS order_lines")
    con.execute("""
        CREATE TABLE order_lines (
            id INTEGER, order_id INTEGER, product_id INTEGER, variant_id INTEGER,
            quantity INTEGER, price DOUBLE, title VARCHAR, sku VARCHAR
        )
    """)
    con.executemany("INSERT INTO order_lines VALUES (?,?,?,?,?,?,?,?)", order_lines)

    con.execute("DROP TABLE IF EXISTS order_discount_codes")
    con.execute("""
        CREATE TABLE order_discount_codes (
            order_id INTEGER, code VARCHAR
        )
    """)
    con.executemany("INSERT INTO order_discount_codes VALUES (?,?)", order_discount_codes)

    con.execute("DROP TABLE IF EXISTS refunds")
    con.execute("""
        CREATE TABLE refunds (
            id INTEGER, order_id INTEGER, created_at TIMESTAMP,
            note VARCHAR, restock BOOLEAN
        )
    """)
    con.executemany("INSERT INTO refunds VALUES (?,?,?,?,?)", refunds)

    con.execute("DROP TABLE IF EXISTS transactions")
    con.execute("""
        CREATE TABLE transactions (
            id INTEGER, order_id INTEGER, amount DOUBLE, currency VARCHAR,
            kind VARCHAR, status VARCHAR, gateway VARCHAR, created_at TIMESTAMP
        )
    """)
    con.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?)", transactions)

    con.close()
    print(f"\nDatabase written to {db_path}")


if __name__ == "__main__":
    seed(DB_PATH)
