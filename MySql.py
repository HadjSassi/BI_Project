import mysql.connector

def connect_to_mysql(host, username, password, database):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
        else:
            print("Failed to connect to MySQL database")
            return None
    except mysql.connector.Error as e:
        print("Error connecting to MySQL database:", e)
        return None

def close_connection(connection):
    if connection.is_connected():
        connection.close()
        print("Connection to MySQL database closed")

# Utilisation de la fonction connect_to_mysql pour se connecter à la base de données
# connection = connect_to_mysql("localhost", "your_username", "your_password", "your_database")
