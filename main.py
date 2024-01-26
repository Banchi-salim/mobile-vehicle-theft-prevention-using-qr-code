import os
import sqlite3
from pathlib import Path
from fetch import get_user_credentials, fetch_user_details, save_vehicle_details
import requests
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivy.uix.image import Image
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.clock import Clock
from io import BytesIO
import qrcode
from pyfcm import FCMNotification
from pyzbar.pyzbar import decode
from qrcode.image.pil import PilImage
#from PIL import Image as img
from kivy.core.window import Window
from kivymd.uix.toolbar import MDTopAppBar
Builder.load_file('main.kv')

class LoginScreen(MDScreen):
    pass
class AdminScreen(MDScreen):
    pass


class ScanQRScreen(MDScreen):
    def __init__(self, **kwargs):
        super(ScanQRScreen, self).__init__(**kwargs)
        self.qr_code_result = None

    def scan_qr_code(self):
        image_path = "C:/Users/Salim_Banchi/PycharmProjects/mobile-vehicle-theft-prevention-using-qr-code/untitled.png"


        try:
            decoded_qr = self.decode_qr_code(image_path)
            if decoded_qr:
                self.qr_code_result = decoded_qr
                self.show_qr_result_popup()
            else:
                self.show_error_popup("No QR code found!")
        except Exception as e:
            self.show_error_popup(f"Error: {str(e)}")

    def decode_qr_code(self, image_path):
        # Open the image file using the Image class directly
        with Image.open(image_path) as img:
            # Convert the image to grayscale
            img = img.convert('L')
            # Decode the QR code
            decoded_objects = decode(img)

        if decoded_objects:
            # Return the first decoded object (assuming only one QR code in the image)
            return decoded_objects[0].data.decode("utf-8")
        else:
            return None

    def show_qr_result_popup(self):
        content = BoxLayout(orientation="vertical")
        content.add_widget(MDLabel(text="QR Code Result"))
        content.add_widget(MDLabel(text=self.qr_code_result))

        popup = Popup(
            title="QR Code Result",
            content=content,
            size_hint=(None, None),
            size=(200, 200),
            auto_dismiss=True,
        )
        popup.open()

    def show_error_popup(self, message):
        content = BoxLayout(orientation="vertical")
        content.add_widget(MDLabel(text=message))

        popup = Popup(
            title="Error",
            content=content,
            size_hint=(None, None),
            size=(300, 150),
            auto_dismiss=True,
        )
        popup.open()
class RegisterVehicleScreen(MDScreen):
    def __init__(self, **kwargs):
        super(RegisterVehicleScreen, self).__init__(**kwargs)
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
        )

    def exit_manager(self, *args):
        self.file_manager.close()

    def select_path(self, path):
        self.exit_manager()
        #print("Selected Path:", path)
        car_image_path = path
        return car_image_path

    def file_manager_open(self):
        self.file_manager.show('/')  # Set the initial directory (you can change it)

    def register_vehicle(self):
        car_make = self.ids.car_make.text
        car_model = self.ids.car_model.text
        plate_number = self.ids.plate_number.text
        username = self.ids.username.text
        car_image_path = self.select_path()

        # Validate input
        if not car_make or not car_model or not plate_number or not username:
            self.show_error_popup("Please fill in all fields.")
            return

        # Fetch user details based on the username
        user_details = self.fetch_user_details(username)

        if user_details is None:
            self.show_error_popup("User not found.")
            return

        # Save the car details to the database
        self.save_vehicle_details(user_details["id"], car_make, car_model, plate_number, car_image_path)

        # Generate a QR code with the user and vehicle data
        qr_data = f"User: {user_details['name']}\nCar Make: {car_make}\nCar Model: {car_model}\nPlate Number: {plate_number}"
        self.generate_qr_code(qr_data)

        self.show_confirmation_popup()

    def fetch_user_details(self, username):
        user_data = fetch_user_details(username)
        if user_data:
            return {
                "id": user_data[1],
                "name": user_data[2],
                "username": user_data[3],
                "email": user_data[4],
                "security_status": user_data[5],
            }
        else:
            return None

    def save_vehicle_details(self, user_id, car_make, car_model, plate_number, car_image_path):
        conn = sqlite3.connect("securegate.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO vehicles (user_id, make, model, plate_number, image_path)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, car_make, car_model, plate_number, car_image_path))

        conn.commit()
        conn.close()

    def generate_qr_code(self, qr_data):
        img = qrcode.make(qr_data)
        temp_dir = Path(os.path.join(os.environ["TEMP"], "qr_codes"))
        temp_dir.mkdir(parents=True, exist_ok=True)
        qr_code_path = temp_dir / "vehicle_qr_code.png"
        img.save(qr_code_path)
        self.ids.qr_code_image.source = str(qr_code_path)

    def show_error_popup(self, message):
        content = BoxLayout(orientation="vertical")
        content.add_widget(MDLabel(text=message))

        popup = Popup(
            title="Error",
            content=content,
            size_hint=(None, None),
            size=(300, 150),
            auto_dismiss=True,
        )
        popup.open()

    def show_confirmation_popup(self):
        content = BoxLayout(orientation="vertical")
        content.add_widget(Image(source=self.ids.qr_code_image.source))

        popup = Popup(
            title="Confirmation",
            content=content,
            size_hint=(None, None),
            size=(300, 300),
            auto_dismiss=True,
        )
        popup.open()
    def show_confirmation_popup(self):
        content = BoxLayout(orientation="vertical")
        content.add_widget(MDLabel(text="Vehicle registered successfully!"))

        popup = Popup(
            title="Success",
            content=content,
            size_hint=(None, None),
            size=(300, 150),
            auto_dismiss=True,
        )
        popup.open()


class ViewRegisteredVehiclesScreen(MDScreen):
    def on_pre_enter(self, *args):
        self.load_registered_vehicles()

    def load_registered_vehicles(self):
        # Fetch registered vehicles from the database (replace with your actual logic)


        registered_vehicles = [
            {"car_make": "Toyota", "car_model": "Camry", "plate_number": "ABC123", "path": 'v1.jpg'},
            {"car_make": "Honda", "car_model": "Civic", "plate_number": "XYZ789", "path": 'v2.jpg'},
            # Add more vehicles as needed
        ]

        # Clear existing entries in the list
        self.ids.registered_vehicles_list.clear_widgets()

        # Add registered vehicles to the list
        for vehicle_data in registered_vehicles:
            card = MDCard(
                orientation='horizontal',  # Set orientation to horizontal
                padding="20dp",
                size_hint_y=None,
                height="120dp",
            )

            # Left side of the card
            left_layout = BoxLayout(orientation='vertical')
            left_layout.add_widget(MDLabel(text=f"Car Make: {vehicle_data['car_make']}"))
            left_layout.add_widget(MDLabel(text=f"Car Model: {vehicle_data['car_model']}"))
            left_layout.add_widget(MDLabel(text=f"Plate Number: {vehicle_data['plate_number']}"))

            # Right side of the card
            right_layout = BoxLayout(size_hint_x=None, width="56dp")
            image = Image(
                source=vehicle_data['path'],  # Replace with the actual path or URL of your image
                size_hint=(None, None),
                size=("56dp", "56dp"),
            )
            right_layout.add_widget(image)

            # Add left and right layouts to the card
            card.add_widget(left_layout)
            card.add_widget(right_layout)

            self.ids.registered_vehicles_list.add_widget(card)


class RegisterPersonnel_UserScreen(MDScreen):
    def register_user(self):
        # Retrieve input values
        name = self.ids.name_field.text
        user_id = self.ids.id_field.text
        username = self.ids.username_field.text
        password = self.ids.password_field.text
        confirm_password = self.ids.confirm_password_field.text
        security_status = self.ids.security_checkbox.active

        # Validate input (you may add more validation logic)
        if not all([name, user_id, username, password, confirm_password]):
            self.show_error_message("All fields are required.")
            return

        if password != confirm_password:
            self.show_error_message("Passwords do not match.")
            return

        # Store user data (replace with your database or backend logic)
        user_data = {
            "name": name,
            "id": user_id,
            "username": username,
            "password": password,
            "security_status": security_status,
        }

        # Add your logic to store user_data in the database or backend

        # Optionally, show a success message or navigate to another screen

        self.show_success_message("User registered successfully.")
        self.manager.current = "admin"

    def show_error_message(self, message):
        # Add your logic to display an error message (toast, popup, etc.)
        pass

        def show_success_message(self, message):
            # Add your logic to display a success message (toast, popup, etc.)
            pass


class ViewRegisteredPersonnelScreen(MDScreen):
    def on_pre_enter(self, *args):
        # Execute query to get personnel data from the database
        personnel_data = self.get_personnel_data()

        # Access the GridLayout
        personnel_grid = self.ids.personnel_grid

        # Create and add personnel cards to the GridLayout
        for personnel in personnel_data:
            card = MDCard(size_hint=(1, None), height=dp(120), on_release=self.view_personnel_details)
            box_layout = BoxLayout(orientation='horizontal')
            box_layout.add_widget(MDLabel(text=f"Name: {personnel['name']}"))
            box_layout.add_widget(MDLabel(text=f"ID: {personnel['id']}"))
            box_layout.add_widget(MDLabel(text=f"Username: {personnel['username']}"))
            card.add_widget(box_layout)
            personnel_grid.add_widget(card)

    def get_personnel_data(self):
        # Connect to the SQLite database
        conn = sqlite3.connect("securegate.db")
        cursor = conn.cursor()

        # Execute a query to fetch personnel data
        cursor.execute("SELECT name, id, username FROM personnel")
        personnel_data = [{"name": name, "id": id, "username": username} for name, id, username in cursor.fetchall()]

        # Close the database connection
        conn.close()

        return personnel_data

    def view_personnel_details(self, instance):
        # Implement logic to navigate to personnel details screen
        # For example: app.root.current = "personnel_details"
        pass


class ViewStolenVehiclesScreen(MDScreen):

    def on_pre_enter(self, *args):
        # Execute query to get stolen vehicles data from the database
        stolen_vehicles_data = self.get_stolen_vehicles_data()

        # Access the GridLayout
        stolen_vehicles_grid = self.ids.stolen_vehicles_grid

        # Create and add stolen vehicles cards to the GridLayout
        for vehicle in stolen_vehicles_data:
            card = MDCard(size_hint=(1, None), height=dp(120), on_release=self.view_vehicle_details)
            box_layout = BoxLayout(orientation='horizontal')
            box_layout.add_widget(MDLabel(text=f"Make: {vehicle['vehicle_make']}"))
            box_layout.add_widget(MDLabel(text=f"Model: {vehicle['vehicle_model']}"))
            box_layout.add_widget(MDLabel(text=f"Plate Number: {vehicle['plate_number']}"))
            card.add_widget(box_layout)
            stolen_vehicles_grid.add_widget(card)

    def get_stolen_vehicles_data(self):
        # Connect to the SQLite database
        conn = sqlite3.connect("securegate.db")
        cursor = conn.cursor()

        # Execute a query to fetch stolen vehicles data
        cursor.execute("SELECT vehicle_make, vehicle_model, plate_number FROM stolen_vehicles")
        stolen_vehicles_data = [
            {"vehicle_make": make, "vehicle_model": model, "plate_number": plate_number}
            for make, model, plate_number in cursor.fetchall()
        ]

        # Close the database connection
        conn.close()

        return stolen_vehicles_data

    def view_vehicle_details(self, instance):
        # Implement logic to navigate to vehicle details screen
        # For example: app.root.current = "vehicle_details"
        pass


class ReportStolenVehicleScreen(MDScreen):
    def report_theft(self):
        # Get values from the input fields
        make = self.ids.make_input.text
        model = self.ids.model_input.text
        plate_number = self.ids.plate_number_input.text

        # Validate input (you can add more validation as needed)

        # Insert the stolen vehicle data into the database
        self.insert_stolen_vehicle_data(make, model, plate_number)

        # Optional: Show a confirmation message or navigate to another screen
        # For example: app.root.current = "confirmation_screen"

    def insert_stolen_vehicle_data(self, make, model, plate_number):
        # Connect to the SQLite database
        conn = sqlite3.connect("securegate.db")
        cursor = conn.cursor()

        # Execute a query to insert stolen vehicle data
        cursor.execute("INSERT INTO stolen_vehicles (vehicle_make, vehicle_model, plate_number) VALUES (?, ?, ?)",
                       (make, model, plate_number))

        # Commit the changes and close the database connection
        conn.commit()
        conn.close()


class InAppNotificationsScreen(MDScreen):
    def send_push_notification(self):
        # Get the push notification message from the admin
        push_notification_message = "Push notification: Important update!"

        # Send push notification to users
        self.send_push_notification_to_users(push_notification_message)

        # Add the new notification to the in-app notifications list
        self.add_notification(push_notification_message)

    def send_in_app_alert(self):
        # Get the in-app alert message from the admin
        in_app_alert_message = "In-app alert: Action required from security!"

        # Send in-app alert to security
        self.send_in_app_alert_to_security(in_app_alert_message)

        # Add the new notification to the in-app notifications list
        self.add_notification(in_app_alert_message)

    def send_push_notification_to_users(self, message):
        # Implement push notification sending to users using FCM
        push_service = FCMNotification(api_key="YOUR_FCM_API_KEY")
        registration_ids = ["device_registration_id_1", "device_registration_id_2"]
        push_service.notify_multiple_devices(registration_ids=registration_ids, message_title="Notification",
                                             message_body=message)

    def send_in_app_alert_to_security(self, message):
        # Implement in-app alert sending to security using FCM or another service
        # For iOS, you need to use APNs. This is a simplified example.
        security_registration_ids = ["security_device_registration_id_1", "security_device_registration_id_2"]
        self.send_push_notification_to_users(message, registration_ids=security_registration_ids)

    def send_push_notification_to_users(self, message, registration_ids):
        # This is a simplified example. In a real-world scenario, you'd integrate with APNs for iOS.
        # Replace 'YOUR_FCM_API_KEY' with your actual FCM API key
        push_service = FCMNotification(api_key="YOUR_FCM_API_KEY")
        push_service.notify_multiple_devices(registration_ids=registration_ids, message_title="Notification",
                                             message_body=message)

    def add_notification(self, message):
        # Add the new notification to the database or wherever you store notifications
        # (Implement this based on your actual database structure)
        # For example: INSERT INTO notifications (user_id, message) VALUES (?, ?)

        # Reload notifications to reflect the latest changes
        self.load_notifications()

    def load_notifications(self):
        # Implement loading notifications from the database
        # (Implement this based on your actual database structure)
        pass


class SecurityScreen(MDScreen):
    pass


class UserScreen(MDScreen):
    pass


class MyApp(MDApp):
    def on_start(self):
        # Initialize current_user_type attribute
        self.current_user_type = None
    def build(self):
        # Set window size to simulate a mobile device

        Window.size = (360, 640)
        self.theme_cls.theme_style = 'Light'  # Set 'Light' or 'Dark' based on your preference
        self.theme_cls.primary_palette = 'Green'
        screen_manager = self.create_screen_manager()
        return screen_manager

    def create_screen_manager(self):
        screen_manager = ScreenManager()

        Login_screen = LoginScreen()
        admin_screen = AdminScreen()
        scan_qr_screen = ScanQRScreen()
        register_vehicle_screen = RegisterVehicleScreen()
        view_registered_vehicles_screen = ViewRegisteredVehiclesScreen()
        view_registered_personnel_screen = ViewRegisteredPersonnelScreen()
        register_personnel_screen = RegisterPersonnel_UserScreen()
        view_stolen_vehicles_screen = ViewStolenVehiclesScreen()
        report_stolen_vehicle_screen = ReportStolenVehicleScreen()
        in_app_notifications_screen = InAppNotificationsScreen()
        security_screen = SecurityScreen()
        user_screen = UserScreen()

        screen_manager.add_widget(Login_screen)
        screen_manager.add_widget(admin_screen)
        screen_manager.add_widget(security_screen)
        screen_manager.add_widget(user_screen)
        screen_manager.add_widget(scan_qr_screen)
        screen_manager.add_widget(register_vehicle_screen)
        screen_manager.add_widget(view_registered_vehicles_screen)
        screen_manager.add_widget(view_registered_personnel_screen)
        screen_manager.add_widget(register_personnel_screen)
        screen_manager.add_widget(view_stolen_vehicles_screen)
        screen_manager.add_widget(report_stolen_vehicle_screen)
        screen_manager.add_widget(in_app_notifications_screen)

        return screen_manager

    def verify_login(self, username, password):
        try:
            # Call the function to get user credentials
            credentials = get_user_credentials(username, password)

            if credentials:
                # Check the 'usertype' to determine the appropriate screen
                usertype = credentials.get('usertype')
                self.current_user_type = usertype
                if usertype == 'admin':
                    self.root.current = 'admin'
                elif usertype == 'personnel':
                    self.root.current = 'admin'
                elif usertype == 'user':
                    self.root.current = 'user'
            else:
                print("Invalid username or password.")

        except Exception as e:
            print(f"Error during login verification: {str(e)}")

    def go_back(self):
        if self.current_user_type == 'admin':
            self.root.current = 'admin'
        elif self.current_user_type == 'personnel':
            self.root.current = 'security'
        elif self.current_user_type == 'user':
            self.root.current = 'user'
if __name__ == "__main__":
    MyApp().run()
