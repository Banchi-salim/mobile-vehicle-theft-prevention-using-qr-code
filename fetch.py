import mysql.connector

def connect():
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'secure_gate',
        'raise_on_warnings': True,
    }
    return mysql.connector.connect(**db_config)
def get_user_credentials(username, password):


    conn = connect()
    cursor = conn.cursor(dictionary=True)  # Set dictionary=True to get results as dictionaries

    # Fetch user credentials by checking all tables
    tables = ['admin', 'personnel', 'user']

    for table in tables:
        cursor.execute(f'SELECT name, username, password FROM {table} WHERE username = %s AND password = %s',
                       (username, password))
        user_credentials = cursor.fetchone()

        if user_credentials:
            # Close the connection
            conn.close()
            user_credentials['usertype'] = table

            return user_credentials

    # Close the connection
    conn.close()
    return None

def fetch_user_details(username):
    conn = connect()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM personnel WHERE username=%s", (username,))
    user_data = cursor.fetchone()

    conn.close()

    return user_data

def save_vehicle_details(user_id, car_make, car_model, plate_number, car_image_path):
    conn = connect()
    cursor = conn.cursor()

    # Convert image to binary data
    with open(car_image_path, "rb") as image_file:
        image_binary = image_file.read()

    cursor.execute("""
        INSERT INTO vehicles (user_id, make, model, plate_number, image_data)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, car_make, car_model, plate_number, image_binary))

    conn.commit()
    conn.close()

