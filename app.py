from flask import Flask, jsonify, request
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# DB connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="zerotwo",
        database="invoice_management"
    )

# ==================== CUSTOMER ====================

@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.json
    name = data['name']
    email = data.get('email', '')
    phone = data.get('phone', '')
    address = data.get('address', '')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customers (name, email, phone, address)
        VALUES (%s, %s, %s, %s)
    """, (name, email, phone, address))
    conn.commit()
    customer_id = cursor.lastrowid
    conn.close()

    return jsonify({'message': 'Customer added successfully', 'customer_id': customer_id}), 201

# ==================== INVOICE ====================

@app.route('/invoices', methods=['GET'])
def get_all_invoices():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT invoices.invoice_id, invoices.invoice_date, invoices.total_amount,
               customers.name AS customer_name
        FROM invoices
        JOIN customers ON invoices.customer_id = customers.customer_id
        ORDER BY invoices.invoice_date DESC
    """)
    invoices = cursor.fetchall()
    conn.close()
    return jsonify(invoices)

@app.route('/invoices/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT invoices.invoice_id, invoices.invoice_date, invoices.total_amount,
               customers.name AS customer_name, customers.email, customers.phone
        FROM invoices
        JOIN customers ON invoices.customer_id = customers.customer_id
        WHERE invoice_id = %s
    """, (invoice_id,))
    invoice = cursor.fetchone()

    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404

    cursor.execute("""
        SELECT products.name AS product_name, invoice_items.quantity,
               invoice_items.unit_price, invoice_items.total_price
        FROM invoice_items
        JOIN products ON invoice_items.product_id = products.product_id
        WHERE invoice_items.invoice_id = %s
    """, (invoice_id,))
    items = cursor.fetchall()

    conn.close()
    return jsonify({'invoice': invoice, 'items': items})

@app.route('/invoices', methods=['POST'])
def create_invoice():
    data = request.json
    customer_id = data['customer_id']
    items = data['items']
    total_amount = sum(item['quantity'] * item['unit_price'] for item in items)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO invoices (customer_id, total_amount) VALUES (%s, %s)",
                   (customer_id, total_amount))
    invoice_id = cursor.lastrowid

    for item in items:
        cursor.execute("""
            INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price, total_price)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            invoice_id,
            item['product_id'],
            item['quantity'],
            item['unit_price'],
            item['quantity'] * item['unit_price']
        ))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Invoice created', 'invoice_id': invoice_id}), 201

@app.route('/invoices/<int:invoice_id>', methods=['DELETE'])
def delete_invoice(invoice_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM invoice_items WHERE invoice_id = %s", (invoice_id,))
    cursor.execute("DELETE FROM invoices WHERE invoice_id = %s", (invoice_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Invoice deleted successfully'}), 200

@app.route('/invoices/<int:invoice_id>', methods=['PUT'])
def update_invoice(invoice_id):
    data = request.json
    items = data['items']
    total_amount = sum(item['quantity'] * item['unit_price'] for item in items)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Update invoice total
    cursor.execute("UPDATE invoices SET total_amount = %s WHERE invoice_id = %s",
                   (total_amount, invoice_id))

    # Delete old items
    cursor.execute("DELETE FROM invoice_items WHERE invoice_id = %s", (invoice_id,))

    # Insert new items
    for item in items:
        cursor.execute("""
            INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price, total_price)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            invoice_id,
            item['product_id'],
            item['quantity'],
            item['unit_price'],
            item['quantity'] * item['unit_price']
        ))

    conn.commit()
    conn.close()
    return jsonify({'message': 'Invoice updated successfully'}), 200

# ==================== MAIN ====================
if __name__ == '__main__':
    app.run(debug=True)
