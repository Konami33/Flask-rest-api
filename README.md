# Create a Flask REST API, connect it to MySQL, and deploy the entire setup using Docker

## Step 1: Set Up Flask REST API

1. **Create a project directory**
    ```bash
    mkdir flask_mysql_docker
    cd flask_mysql_docker
    ```

2. **Create a virtual environment and activate it**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Flask and MySQL connector**
    ```bash
    pip install Flask mysql-connector-python
    ```

4. **Create the Flask application**

    Create a file named `app.py` with the following content:
    
    ```python
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
    ```

## Step 2: Set Up MySQL

1. **Create a database initialization script**

    Create a file named `init_db.sql` with the following content:
    ```sql
    CREATE DATABASE IF NOT EXISTS test_db;
    USE test_db;

    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        email VARCHAR(50) NOT NULL
    );
    ```

## Step 3: Set Up Docker

1. **Create a `Dockerfile` for the Flask application**
    ```Dockerfile
    # Use an official Python runtime as a parent image
    FROM python:3.8-slim-buster

    # Set the working directory in the container
    WORKDIR /app

    # Copy the current directory contents into the container at /app
    COPY . /app

    # Install any needed packages specified in requirements.txt
    RUN pip install --no-cache-dir Flask mysql-connector-python

    # Make port 5000 available to the world outside this container
    EXPOSE 5000

    # Define environment variable
    ENV NAME World

    # Run app.py when the container launches
    CMD ["python", "app.py"]
    ```

2. **Create a `docker-compose.yml` file**
    ```yaml
    version: '3.8'

    services:
      db:
        image: mysql:5.7
        restart: always
        environment:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: test_db
        volumes:
          - ./init_db.sql:/docker-entrypoint-initdb.d/init_db.sql
        ports:
          - "3307:3306"

      web:
        build: .
        command: python app.py
        volumes:
          - .:/app
        ports:
          - "5000:5000"
        depends_on:
          - db
    ```

## Step 4: Build and Run the Docker Containers

1. **Build and start the containers**
    ```bash
    docker-compose up --build
    ```

## Step 5: Testing the API

Once the containers are up and running, you can test the API using tools like `curl` or Postman.

1. **Add a new user**
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"name": "John Doe", "email": "john@example.com"}' http://localhost:5000/users
    ```

2. **Get all users**
    ```bash
    curl http://localhost:5000/users
    ```

That's it! You now have a Flask REST API connected to a MySQL database, all running inside Docker containers.