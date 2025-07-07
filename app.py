from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# 🔷 GET all transactions
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    conn = get_db_connection()
    rows = conn.execute(
        'SELECT * FROM transactions ORDER BY date DESC'
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


# 🔷 POST a new transaction
@app.route('/api/transaction', methods=['POST'])
def add_transaction():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON received"}), 400

        required = ['type', 'amount', 'category', 'date']
        if not all(k in data for k in required):
            return jsonify({"error": "Missing fields"}), 400

        conn = get_db_connection()
        conn.execute(
            '''
            INSERT INTO transactions (type, amount, category, date, note)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                data['type'],
                data['amount'],
                data['category'],
                data['date'],
                data.get('note', '')
            )
        )
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Error adding transaction:", str(e))
        return jsonify({"error": "Failed to add transaction"}), 500


# 🔷 DELETE a transaction
@app.route('/api/transaction/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    try:
        conn = get_db_connection()
        conn.execute(
            'DELETE FROM transactions WHERE id = ?',
            (id,)
        )
        conn.commit()
        conn.close()
        return jsonify({'status': 'deleted'})
    except Exception as e:
        print("Error deleting transaction:", str(e))
        return jsonify({"error": "Failed to delete"}), 500


# 🔷 Initialize DB
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            note TEXT
        )
    ''')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    print("✅ Initializing database and starting server...")
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
