from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="db",  # service name defined in docker-compose.yml
        port=3306,  # MySQL service port
        user="root",
        password="root",
        database="test_db"
    )

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

@app.route('/users', methods=['POST'])
def add_user():
    new_user = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, email) VALUES (%s, %s)',
                   (new_user['name'], new_user['email']))
    conn.commit()
    cursor.close()
    conn.close()
    return '', 201

if __name__ == '__main__':
    app.run(host='0.0.0.0')
