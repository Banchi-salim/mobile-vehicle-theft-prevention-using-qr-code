import os
import sqlite3
from kivy.core.image import Image as CoreImage
from kivy.core.image import ImageLoader, Texture
import fetch
from fetch import get_user_credentials, fetch_user_details, save_vehicle_details
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
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
        super().__init__(**kwargs)
        self.name = 'register_vehicle'
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )
        self.v_img = ''

    def file_manager_open(self):
        self.file_manager.show('/')

    def exit_manager(self, *args):
        self.file_manager.close()

    def select_path(self, path):
        self.file_manager.close()
        self.v_img = path
        print(self.v_img)
        return self.v_img

    def register_vehicle(self):
        car_make = self.ids.car_make.text
        car_model = self.ids.car_model.text
        plate_number = self.ids.plate_number.text
        user_id = self.ids.user_id.text
        car_image_path = self.v_img

        # Validate input
        if not car_make or not car_model or not plate_number or not user_id:
            self.show_error_popup("Please fill in all fields.")
            return

        # Fetch user details based on the username
        user_details = fetch_user_details(user_id)
        print(user_details)

        if user_details is None:
            self.show_error_popup("User not found.")
            return

        # Save the car details to the database
        self.save_vehicle_details(user_details["user_id"], car_make, car_model, plate_number, car_image_path)

        """# Generate a QR code with the user and vehicle data
        qr_data = f"User: {user_details['name']}\nCar Make: {car_make}\nCar Model: {car_model}\nPlate Number: {plate_number}"
        self.generate_qr_code(qr_data)"""

        self.show_confirmation_popup()

    """def fetch_user_details(self, user_id):
        user_data = fetch_user_details(user_id)
        if user_data:
            return {
                "user_id": user_data[3],
                "name": user_data[1],
                "username": user_data[2],
            }
        else:
            return None"""

    def save_vehicle_details(self, user_id, car_make, car_model, plate_number, car_image_path):
        fetch.save_vehicle_details(user_id, car_make, car_model, plate_number, car_image_path)

    def show_error_popup(self, message):
        content = BoxLayout(orientation="vertical")
        content.add_widget(MDLabel(text=message))

        popup = Popup(
            title="Error",
            content=content,
            size_hint=(None, None),
            size=(300, 150),
            auto_dismiss=True,
            #template="PopupError",
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
            #template="FloatingWindow",
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
            #template="FloatingWindow",
        )
        popup.open()


class ViewRegisteredVehiclesScreen(MDScreen):
    def on_pre_enter(self, *args):
        self.load_registered_vehicles()

    def load_registered_vehicles(self):
        # Clear existing entries in the list
        self.ids.registered_vehicles_list.clear_widgets()
        registered_vehicles = fetch.fetch_vehicle_details()
        print(registered_vehicles)

        if registered_vehicles:
            for vehicle_data in registered_vehicles:
                card = MDCard(
                    orientation='horizontal',
                    padding="20dp",
                    spacing="20dp",
                    size_hint=(None, None),
                    height="200dp",
                    width="300dp",
                    pos_hint={"center_x":.5}
                )

                left_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
                left_layout.add_widget(MDLabel(text=f"Car Make: {vehicle_data['make']}"))
                left_layout.add_widget(MDLabel(text=f"Car Model: {vehicle_data['model']}"))
                left_layout.add_widget(MDLabel(text=f"Plate Number: {vehicle_data['registration_number']}"))

                # Right side of the card
                right_layout = BoxLayout(orientation = "vertical", size_hint_x=None, width="100dp")
                # Convert image bytes to source
                vehicle_image_bytes = BytesIO(vehicle_data['vehicle_image']).read()
                vehicle_image_bytes_1 = BytesIO(vehicle_data['qr_code_image']).read()

                # Use kivy.core.image.Image to load the image
                vehicle_image = CoreImage(BytesIO(vehicle_image_bytes), ext='png').texture
                qr_image = CoreImage(BytesIO(vehicle_image_bytes_1), ext='png').texture

                # Create Kivy Image
                image_widget = Image(texture=vehicle_image, size=("56dp", "56dp"))
                image_widget_1 = Image(texture=qr_image, size=("56dp", "56dp"))

                right_layout.add_widget(image_widget)
                right_layout.add_widget(image_widget_1)



                card.add_widget(left_layout)
                card.add_widget(right_layout)

                self.ids.registered_vehicles_list.add_widget(card)


class RegisterPersonnel_UserScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'register_user'
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )
        self.u_img = ''

    def file_manager_open(self):
        self.file_manager.show('/')

    def exit_manager(self, *args):
        self.file_manager.close()

    def select_path(self, path):
        self.file_manager.close()
        self.u_img = path
        print(self.u_img)
        return self.u_img

    def register_user(self):
        # Retrieve input values
        name = self.ids.name_field.text
        user_id = self.ids.id_field.text
        username = self.ids.username_field.text
        password = self.ids.password_field.text
        confirm_password = self.ids.confirm_password_field.text
        security_status = self.ids.user_type.text
        user_img = self.u_img

        # Validate input (you may add more validation logic)
        if not all([name, user_id, username, password, confirm_password, security_status,]):
            self.show_error_message("All fields are required.")
            return

        if password != confirm_password:
            self.show_error_message("Passwords do not match.")
            return
        if all([name, user_id, username, password, confirm_password, security_status]) and password == confirm_password:
            fetch.insert_user_data(name, user_id, username, password, security_status, user_img)


        # Optionally, show a success message or navigate to another screen

        self.show_success_popup("User registered successfully.")
        self.manager.current = "admin"

    def show_error_popup(self, message):
        content = BoxLayout(orientation="vertical")
        content.add_widget(MDLabel(text=message))

        popup = Popup(
            title="Error",
            content=content,
            size_hint=(None, None),
            size=(300, 150),
            auto_dismiss=True,
            # template="PopupError",
        )
        popup.open()

    def show_success_popup(self,  message):
        content = BoxLayout(orientation="vertical")
        content.add_widget(MDLabel(text=message))

        popup = Popup(
            title="Confirmation",
            content=content,
            size_hint=(None, None),
            size=(300, 300),
            auto_dismiss=True,
            # template="FloatingWindow",
        )
        popup.open()


class ViewRegisteredPersonnelScreen(MDScreen):
    def on_pre_enter(self, *args):
        self.load_personnel()


    def load_personnel(self):
        # Clear existing entries in the list
        self.ids.registered_personnel.clear_widgets()
        personnels = fetch.fetch_personnel_details()
        print(personnels)

        if personnels:
            for personnel in personnels:
                card = MDCard(
                    orientation='horizontal',
                    padding="20dp",
                    spacing="20dp",
                    size_hint=(None, None),
                    height="150dp",
                    width="300dp",
                    pos_hint={"center_x": .5}
                )

                left_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
                left_layout.add_widget(MDLabel(text=f"Name: {personnel['name']}"))
                left_layout.add_widget(MDLabel(text=f"ID: {personnel['id']}"))
                left_layout.add_widget(MDLabel(text=f"Username: {personnel['username']}"))

                # Right side of the card
                right_layout = BoxLayout(orientation="vertical", size_hint_x=None, width="100dp")
                # Convert image bytes to source
                personnel_image_bytes = BytesIO(personnel['user_image']).read()


                # Use kivy.core.image.Image to load the image
                security_image = CoreImage(BytesIO(personnel_image_bytes), ext='png').texture


                # Create Kivy Image
                image_widget = Image(texture=security_image, size=("56dp", "150dp"))
                right_layout.add_widget(image_widget)

                card.add_widget(left_layout)
                card.add_widget(right_layout)

                self.ids.registered_personnel.add_widget(card)

class ViewStolenVehiclesScreen(MDScreen):

    def on_pre_enter(self, *args):
        # Execute query to get stolen vehicles data from the database
        self.get_stolen_vehicles_data()

        # Access the GridLayout
    def get_stolen_vehicles_data(self):
        self.ids.stolen_vehicles_grid.clear_widgets()
        stolen_vehicles_data = fetch.get_stolen()

        for vehicle_data in stolen_vehicles_data:
            card = MDCard(
                orientation='horizontal',
                padding="20dp",
                spacing="20dp",
                size_hint=(None, None),
                height="200dp",
                width="300dp",
                pos_hint={"center_x": .5}
            )



            left_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
            left_layout.add_widget(MDLabel(text=f"Car owner: {vehicle_data['name']}"))
            left_layout.add_widget(MDLabel(text=f"User ID: {vehicle_data['user_id']}"))
            left_layout.add_widget(MDLabel(text=f"Car Make: {vehicle_data['make']}"))
            left_layout.add_widget(MDLabel(text=f"Car Model: {vehicle_data['model']}"))
            left_layout.add_widget(MDLabel(text=f"Plate Number: {vehicle_data['registration_number']}"))

            # Right side of the card
            right_layout = BoxLayout(orientation="vertical", size_hint_x=None, width="100dp")
            # Convert image bytes to source
            vehicle_image_bytes = BytesIO(vehicle_data['vehicle_image']).read()

            # Use kivy.core.image.Image to load the image
            vehicle_image = CoreImage(BytesIO(vehicle_image_bytes), ext='png').texture


            # Create Kivy Image
            image_widget = Image(texture=vehicle_image, size=("56dp", "56dp"))
            right_layout.add_widget(image_widget)


            card.add_widget(left_layout)
            card.add_widget(right_layout)
            self.ids.stolen_vehicles_grid.add_widget(card)



class ReportStolenVehicleScreen(MDScreen):
    def report_theft(self, *args):
        user_id = self.ids.user_id.text
        plate_number = self.ids.plate_number.text

        # Validate input (you may add more validation logic)
        if not user_id:
            self.show_error_message("Please enter User ID.")
            return

        # Fetch vehicle details by user_id
        vehicle_details = fetch.fetch_stolen_vehicle(user_id, plate_number)
        #print(vehicle_details)
        v_make = vehicle_details['make']
        v_model = vehicle_details['model']
        plate_number = vehicle_details['registration_number']
        user_id = vehicle_details['user_id']

        if not vehicle_details:
            self.show_error_message("No vehicle details found for the provided User ID.")
            return

        elif vehicle_details:
            fetch.insert_stolen_vehicle(v_make, v_model, plate_number, user_id)
            # Optionally, show a success message or navigate to another screen
            self.show_success_message("Vehicle theft reported successfully.")
        # Display vehicle details
        #self.vehicle_info_label.text = f"Vehicle Information:\n{vehicle_details}"

    def show_success_message(self, message):
        popup = Popup(title='Success', content=MDLabel(text=message), size_hint=(None, None), size=(300, 150))
        popup.open()

    def show_error_message(self, message):
        popup = Popup(title='Error', content=MDLabel(text=message), size_hint=(None, None), size=(300, 150))
        popup.open()



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
