from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="db",  # service name defined in docker-compose.yml or K8s service name
        port=3306,  # MySQL service port
        user="root",
        password="root",
        database="test_db"
    )

@app.route('/users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        return jsonify(users)
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        if user:
            return jsonify(user)
        else:
            return jsonify({"error": "User not found"}), 404
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/users', methods=['POST'])
def add_user():
    new_user = request.get_json()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, email) VALUES (%s, %s)',
                       (new_user['name'], new_user['email']))
        conn.commit()
        return jsonify({"id": cursor.lastrowid}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    update_user = request.get_json()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET name = %s, email = %s WHERE id = %s',
                       (update_user['name'], update_user['email'], user_id))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User updated successfully"})
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User deleted successfully"})
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
