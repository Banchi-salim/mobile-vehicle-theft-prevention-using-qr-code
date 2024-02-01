from datetime import datetime, timedelta

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
        cursor.execute(f'SELECT name, username, password, user_id FROM {table} WHERE username = %s AND password = %s',
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
    # for table in tables:
    cursor.execute("SELECT * FROM user WHERE user_id = %s", (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        conn.close()
        return user_data

    # conn.close()
    # return None


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

        conn.commit()

    except Error as e:
        print(f"Error: {e}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# save_vehicle_details(1810310002, "honda", "civic", "ABJ345kuj", "v2.jpg")
def fetch_temp_vehicle_details(registration_number):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """SELECT v.vehicle_id, v.make, v.model, v.registration_number, v.vehicle_image, v.qr_code_image, 
        u.user_id, u.name as user_name FROM vehicle v JOIN user u ON v.user_id = u.user_id WHERE 
        v.registration_number = %S"""
        cursor.execute(query, (registration_number,))
        vehicles = cursor.fetchone()
        print(vehicles)

        # conn.commit()

        return vehicles

    except Error as e:
        print(f"Error: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def fetch_vehicle_details():
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT v.vehicle_id, v.make, v.model, v.registration_number, v.vehicle_image, v.qr_code_image, u.user_id, u.name as user_name 
            FROM vehicle v
            JOIN user u ON v.user_id = u.user_id
        """
        cursor.execute(query)
        vehicles = cursor.fetchall()

        # conn.commit()

        return vehicles

    except Error as e:
        print(f"Error: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def fetch_user_vehicle_details(user_id):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT v.vehicle_id, v.make, v.model, v.registration_number, v.vehicle_image, v.qr_code_image, u.user_id, u.name as user_name 
            FROM vehicle v
            JOIN user u ON v.user_id = u.user_id
            WHERE u.user_id = %s
        """
        cursor.execute(query, (user_id,))
        vehicles = cursor.fetchall()

        return vehicles

    except Error as e:
        print(f"Error: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_user_data(name, user_id, username, password, security_status, user_img):
    conn = connect()
    cursor = conn.cursor()
    try:
        # Choose the appropriate table based on security_status
        table_name = "personnel" if security_status.lower() == "personnel" else "user"

        # Call the stored procedure with the selected table name
        # cursor.callproc("InsertUser", (table_name, name, user_id, username, password, user_img))

        # Convert the vehicle image to bytes
        with open(user_img, 'rb') as image_file:
            user_image_blob = image_file.read()

        # Insert data into the vehicles table
        cursor.execute(f"""
            INSERT INTO {table_name} (name, user_id, username, password, user_image)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, user_id, username, password, user_image_blob))

        conn.commit()

    except Error as e:
        print(f"Error: {e}")

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def fetch_personnel_details():
    conn = connect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Execute the SQL query to fetch personnel details
        query = """
               SELECT id, name, username, user_image
               FROM personnel
           """
        cursor.execute(query)

        # Fetch all rows
        personnels = cursor.fetchall()

        return personnels

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def fetch_all_user_details():
    conn = connect()
    cursor = conn.cursor(dictionary=True)

    try:
        # Execute the SQL query to fetch personnel details
        query = """
               SELECT id, name, username, user_id, user_image
               FROM user
           """
        cursor.execute(query)

        # Fetch all rows
        user = cursor.fetchall()

        return user

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return None

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def fetch_stolen_vehicle(user_id, plate_number):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM vehicle WHERE user_id = %s AND registration_number = %s ",
                       (user_id, plate_number))
        vehicle_details = cursor.fetchone()
        return vehicle_details
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()


def insert_stolen_vehicle(vehicle_make, vehicle_model, plate_number, user_id):
    conn = connect()
    cursor = conn.cursor()
    try:
        # Insert data into the vehicles table
        cursor.execute(f"""
            INSERT INTO stolen_vehicles (vehicle_make, vehicle_model, plate_number, user_id)
            VALUES (%s, %s, %s, %s)
        """, (vehicle_make, vehicle_model, plate_number, user_id))

        conn.commit()

    except Error as e:
        print(f"Error: {e}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def get_stolen():
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT s.vehicle_make, s.vehicle_model, s.plate_number, s.reported_at, v.vehicle_image, u.user_id, u.name as user_name
            FROM stolen_vehicles s
            JOIN vehicle v ON s.user_id = v.user_id
            JOIN user u ON v.user_id = u.user_id
        """
        cursor.execute(query)
        vehicles = cursor.fetchall()

        # conn.commit()

        return vehicles

    except Error as e:
        print(f"Error: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def insert_message(sender, receiver, message):
    conn = connect()
    cursor = conn.connect()
    try:
        cursor.execute("""
            INSERT INTO notifications (sender_id, receiver_id, message) VALUES (%s, %s, %s)
        """, (sender, receiver, message))
        conn.commit()

    except Error as e:
        print(f"Error: {e}")

    finally:
        conn.close()


def get_messages(user):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT sender_id, message, timestamp FROM notifications
            WHERE receiver_id=%s OR sender_id=%s
            ORDER BY timestamp DESC
        """, (user, user))
        return cursor.fetchall()

    except Error as e:
        print(f"Error: {e}")


def insert_notification(sender_id, receiver_id, message):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
           INSERT INTO notifications (sender_id, receiver_id, message) VALUES (%s, %s, %s)
       """, (sender_id, receiver_id, message))
    conn.commit()


def get_notifications(user_id):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
           SELECT id, sender_id, message, timestamp FROM notifications
           WHERE receiver_id=%s AND seen=0
           ORDER BY timestamp DESC
       """, (user_id,))
    return cursor.fetchall()


def update_notification_seen(notification_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
           UPDATE user_notifications SET seen=1 WHERE id=%s
       """, (notification_id,))

    cursor.execute("""
         DELETE FROM user_notifications WHERE seen=1
     """)
    conn.commit()


def insert_security_notification(sender_id, message):
    conn = connect()
    cursor = conn.cursor()
    try:
        # Insert a record into the security_notifications table
        cursor.execute("""
            INSERT INTO security_notifications (sender_id, message)
            VALUES (%s, %s)
        """, (sender_id, message))

        conn.commit()

    except Error as e:
        print(f"Error: {e}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def fetch_security_notifications():
    conn = connect()
    cursor = conn.cursor()
    try:
        # Fetch security notifications
        cursor.execute("""
            SELECT id, sender_id, message, timestamp, seen
            FROM security_notifications
            ORDER BY timestamp DESC
        """)
        notifications = cursor.fetchall()

        conn.commit()
        return notifications

    except Error as e:
        print(f"Error: {e}")
        return None

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def insert_user_notification(sender_id, receiver_id, message):
    conn = connect()
    cursor = conn.cursor()
    try:
        # Insert a record into the user_notifications table
        cursor.execute("""
            INSERT INTO user_notifications (sender_id, receiver_id, message)
            VALUES (%s, %s, %s)
        """, (sender_id, receiver_id, message))

        conn.commit()

    except Error as e:
        print(f"Error: {e}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def fetch_user_notifications(user_id):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    try:
        # Fetch user notifications for the specified user
        cursor.execute("""
            SELECT id, sender_id, message, timestamp, seen
            FROM user_notifications
            WHERE receiver_id = %s
            ORDER BY timestamp DESC
        """, (user_id,))
        notifications = cursor.fetchall()

        conn.commit()
        return notifications

    except Error as e:
        print(f"Error: {e}")
        return None

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def grant_temporary_access(user_id, registration_number, name, user_img, expiration_minutes=60):
    conn = connect()
    cursor = conn.cursor()
    # Calculate expiration time
    expiration_time = datetime.now() + timedelta(minutes=expiration_minutes)
    """print(expiration_time)
    car_dets = fetch_temp_vehicle_details(registration_number)
    print(car_dets)
    owner_name = car_dets['user_name']
    car_make = car_dets['make']
    car_image = car_dets['vehicle_image']"""

    with open(user_img, 'rb') as image_file:
        user_image_blob = image_file.read()

    qr_data = f"{user_id}-{registration_number}-{name}-{user_image_blob}"#{owner_name}-{car_make}-{car_image}-
    qr_image = qrcode.make(qr_data)

    # Convert the QR code image to bytes
    qr_code_bytes = BytesIO()
    qr_image.save(qr_code_bytes)
    qr_code_blob = qr_code_bytes.getvalue()

    try:
        query = """INSERT INTO temporary_access (user_id, registration_number, name, expiration_time, 
        user_image_blob, qr_code_blob) VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (user_id, registration_number, name, expiration_time, user_image_blob, qr_code_blob,))
        conn.commit()
        print("Temporary access granted successfully.")
    except Exception as e:
        #print(f"Error granting temporary access: {e}")
        print(e)
    finally:
        cursor.close()
        conn.close()


def fetch_temporary_access(user_id):
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """ SELECT qr_code_blob FROM temporary_access WHERE user_id = %s        
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()  # Assuming you expect only one result
        return result
    except Exception as e:
        err = f"{e}"
        return err
