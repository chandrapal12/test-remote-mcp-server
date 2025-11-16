from fastmcp import FastMCP
import mysql.connector
import os

mcp = FastMCP("ExpenseTracker")

# Read credentials from env vars
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASS"),
    "database": os.getenv("MYSQL_DB")
}

def get_conn():
    """Create a new MySQL connection."""
    return mysql.connector.connect(**MYSQL_CONFIG)

def init_db():
    """Create expenses table if not exists."""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date VARCHAR(20) NOT NULL,
            amount DOUBLE NOT NULL,
            category VARCHAR(100) NOT NULL,
            subcategory VARCHAR(100),
            note TEXT
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

# Initialize database
init_db()

# ---------- Tools ----------

@mcp.tool()
def add_expense(date, amount, category, subcategory="", note=""):
    """Add a new expense entry."""
    conn = get_conn()
    cur = conn.cursor()

    query = """
        INSERT INTO expenses(date, amount, category, subcategory, note)
        VALUES (%s, %s, %s, %s, %s)
    """

    cur.execute(query, (date, amount, category, subcategory, note))
    conn.commit()

    new_id = cur.lastrowid

    cur.close()
    conn.close()

    return {"status": "ok", "id": new_id}


@mcp.tool()
def list_expenses(start_date, end_date):
    """List expenses in a date range."""
    conn = get_conn()
    cur = conn.cursor()

    query = """
        SELECT id, date, amount, category, subcategory, note
        FROM expenses
        WHERE date BETWEEN %s AND %s
        ORDER BY id ASC
    """

    cur.execute(query, (start_date, end_date))
    rows = cur.fetchall()

    cols = [desc[0] for desc in cur.description]
    result = [dict(zip(cols, row)) for row in rows]

    cur.close()
    conn.close()

    return result


@mcp.tool()
def summarize(start_date, end_date, category=None):
    """Summarize expenses."""
    conn = get_conn()
    cur = conn.cursor()

    query = """
        SELECT category, SUM(amount) AS total_amount
        FROM expenses
        WHERE date BETWEEN %s AND %s
    """

    params = [start_date, end_date]

    if category:
        query += " AND category = %s"
        params.append(category)

    query += " GROUP BY category ORDER BY category ASC"

    cur.execute(query, tuple(params))
    rows = cur.fetchall()

    cols = [desc[0] for desc in cur.description]
    result = [dict(zip(cols, row)) for row in rows]

    cur.close()
    conn.close()

    return result


# ---------- Categories Resource ----------

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    with open("categories.json", "r", encoding="utf-8") as f:
        return f.read()


# ---------- Run MCP Server ----------

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=9000)
