import mysql.connector
import qrcode
from MySQLdb import Error
from PIL import Image
from io import BytesIO

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

def fetch_user_details(user_id):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    tables = ['admin', 'personnel', 'user']
    #for table in tables:
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        conn.close()
        return user_data

    #conn.close()
    #return None


def save_vehicle_details(user_id, car_make, car_model, plate_number, car_image_path):
    conn = connect()
    cursor = conn.cursor(dictionary=True)

    # Generate QR code
    qr_data = f"User ID: {user_id}\nCar Make: {car_make}\nCar Model: {car_model}\nPlate Number: {plate_number}"
    qr_code = qrcode.make(qr_data)

    # Convert the QR code image to bytes
    qr_code_bytes = BytesIO()
    qr_code.save(qr_code_bytes)
    qr_code_blob = qr_code_bytes.getvalue()
    try:
        # Convert the vehicle image to bytes
        with open(car_image_path, 'rb') as image_file:
            vehicle_image_blob = image_file.read()

        # Insert data into the vehicles table
        cursor.execute("""
            INSERT INTO vehicle (user_id, make, model, registration_number, vehicle_image, qr_code_image)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, car_make, car_model, plate_number, vehicle_image_blob, qr_code_blob))

        connect().commit()

    except Error as e:
        print(f"Error: {e}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

