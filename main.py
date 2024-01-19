from kivy.lang import Builder
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
from pyzbar.pyzbar import decode
from qrcode.image.pil import PilImage
from PIL import Image
from kivy.core.window import Window

Builder.load_file('main.kv')


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
        # Handle the selected path (you can process the file path as needed)
        print("Selected Path:", path)

    def file_manager_open(self):
        self.file_manager.show('/')  # Set the initial directory (you can change it)

    def register_vehicle(self):
        car_make = self.ids.car_make.text
        car_model = self.ids.car_model.text
        plate_number = self.ids.plate_number.text
        # Process the file path (you can save it to a database, etc.)
        car_image_path = "path/to/selected/car/image.jpg"

        # Validate input
        if not car_make or not car_model or not plate_number:
            self.show_error_popup("Please fill in all fields.")
            return

        # Optionally, you can fetch user details based on the username
        username = "admin"  # Replace with the actual username
        user_details = self.fetch_user_details(username)

        # Optionally, you can save the car details to a database or perform other actions
        # For now, let's print the registration details
        print("User Details:", user_details)
        print("Car Make:", car_make)
        print("Car Model:", car_model)
        print("Plate Number:", plate_number)
        print("Car Image Path:", car_image_path)

        self.show_confirmation_popup()

    def fetch_user_details(self, username):
        # Replace this with your actual user details fetching logic
        # For now, let's simulate user details
        return {"username": username, "name": "John Doe", "email": "john@example.com"}

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
            {"car_make": "Toyota", "car_model": "Camry", "plate_number": "ABC123"},
            {"car_make": "Honda", "car_model": "Civic", "plate_number": "XYZ789"},
            # Add more vehicles as needed
        ]

        # Clear existing entries in the list
        self.ids.registered_vehicles_list.clear_widgets()

        # Add registered vehicles to the list
        for vehicle_data in registered_vehicles:
            card = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height="120dp"
            )

            card.add_widget(MDLabel(text=f"Car Make: {vehicle_data['car_make']}"))
            card.add_widget(MDLabel(text=f"Car Model: {vehicle_data['car_model']}"))
            card.add_widget(MDLabel(text=f"Plate Number: {vehicle_data['plate_number']}"))

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
    pass


class ViewStolenVehiclesScreen(MDScreen):
    pass


class ReportStolenVehicleScreen(MDScreen):
    pass


class InAppNotificationsScreen(MDScreen):
    pass


class SecurityScreen(MDScreen):
    pass


class UserScreen(MDScreen):
    pass


class MyApp(MDApp):
    def build(self):
        # Set window size to simulate a mobile device

        Window.size = (360, 640)
        screen_manager = self.create_screen_manager()
        return screen_manager

    def create_screen_manager(self):
        screen_manager = ScreenManager()

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


if __name__ == "__main__":
    MyApp().run()
