import os
from kivy.clock import Clock
import mysql.connector
from kivy.core.image import Image as CoreImage
from kivy.core.image import ImageLoader, Texture
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import ThreeLineListItem
from kivymd.uix.menu import MDDropdownMenu

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
# from PIL import Image as img
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
            # template="PopupError",
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
            # template="FloatingWindow",
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
            # template="FloatingWindow",
        )
        popup.open()


class ViewRegisteredVehiclesScreen(MDScreen):
    def on_pre_enter(self, *args):
        self.load_registered_vehicles()

    def load_registered_vehicles(self):
        # Clear existing entries in the list
        self.ids.registered_vehicles_list.clear_widgets()
        registered_vehicles = fetch.fetch_vehicle_details()

        if registered_vehicles:
            for vehicle_data in registered_vehicles:
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
                left_layout.add_widget(MDLabel(text=f"Car Make: {vehicle_data['make']}"))
                left_layout.add_widget(MDLabel(text=f"Car Model: {vehicle_data['model']}"))
                left_layout.add_widget(MDLabel(text=f"Plate Number: {vehicle_data['registration_number']}"))

                # Right side of the card
                right_layout = BoxLayout(orientation="vertical", size_hint_x=None, width="100dp")
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
        if not all([name, user_id, username, password, confirm_password, security_status, ]):
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

    def show_success_popup(self, message):
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
            left_layout.add_widget(MDLabel(text=f"Car owner: {vehicle_data['user_name']}"))
            left_layout.add_widget(MDLabel(text=f"User ID: {vehicle_data['user_id']}"))
            left_layout.add_widget(MDLabel(text=f"Car Make: {vehicle_data['vehicle_make']}"))
            left_layout.add_widget(MDLabel(text=f"Car Model: {vehicle_data['vehicle_model']}"))
            left_layout.add_widget(MDLabel(text=f"Plate Number: {vehicle_data['plate_number']}"))

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
        # print(vehicle_details)
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
        # self.vehicle_info_label.text = f"Vehicle Information:\n{vehicle_details}"

    def show_success_message(self, message):
        popup = Popup(title='Success', content=MDLabel(text=message), size_hint=(None, None), size=(300, 150))
        popup.open()

    def show_error_message(self, message):
        popup = Popup(title='Error', content=MDLabel(text=message), size_hint=(None, None), size=(300, 150))
        popup.open()


class Security_Alert_Screen(MDScreen):

    def __init__(self, **kwargs):
        super(Security_Alert_Screen, self).__init__(**kwargs)

    def send_message(self, *args):
        sen = "admin"
        msg = self.ids.msg.text
        receivers = fetch.fetch_personnel_details()

        for i in receivers:
            receiver = i['user_id']
            message = msg
            sender = sen

            app = MDApp.get_running_app()
            app.send_notification(sender, receiver, message)


class Personal_Notification_Screen(MDScreen):
    def __init__(self, **kwargs):
        super(Personal_Notification_Screen, self).__init__(**kwargs)

    def send_message(self, *args):
        # Implement the logic for sending a message

        sender = "admin"
        n_user_id_input = self.ids.n_user_id.text
        user_id = fetch.fetch_user_details(n_user_id_input)
        receiver = user_id['user_id']

        message = self.ids.message_text.text

        # Call the send_notification method from the app
        app = MDApp.get_running_app()
        app.send_notification(sender, receiver, message)


class SecurityScreen(MDScreen):
    pass


class UserScreen(MDScreen):

    def __init__(self, **kwargs):
        super(UserScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.update()

    def update(self, *args):
        self.ids.qr_card.clear_widgets()
        app = MDApp.get_running_app()
        veh = app.get_user_vehicle_qr()
        image_widget = Image(texture=veh, size=("280dp", "280dp"))

        self.ids.qr_card.add_widget(image_widget)


class User_View_Vehicles(MDScreen):
    def on_pre_enter(self, *args):
        self.vehicles()

    def vehicles(self, *args):
        app = MDApp.get_running_app()
        self.ids.registered_vehicles_list.clear_widgets()
        registered_vehicles = app.get_user_vehicles()

        if registered_vehicles:
            for vehicle_data in registered_vehicles:
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
                left_layout.add_widget(MDLabel(text=f"Car Make: {vehicle_data['make']}"))
                left_layout.add_widget(MDLabel(text=f"Car Model: {vehicle_data['model']}"))
                left_layout.add_widget(MDLabel(text=f"Plate Number: {vehicle_data['registration_number']}"))

                # Right side of the card
                right_layout = BoxLayout(orientation="vertical", size_hint_x=None, width="100dp")
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


class BroadcastScreen(MDScreen):
    def __init__(self, **kwargs):
        super(BroadcastScreen, self).__init__(**kwargs)

    def send_message(self, *args):
        sen = "admin"
        msg = self.ids.broadcast.text
        receivers = fetch.fetch_all_user_details()
        print(receivers)

        for i in receivers:
            receiver = i['user_id']
            message = msg
            sender = sen

            app = MDApp.get_running_app()
            app.send_notification(sender, receiver, message)


class Temporary_Access(MDScreen):
    def __init__(self, **kwargs):
        super(Temporary_Access, self).__init__(**kwargs)
        self.name = 'temp_access'
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

    def create_access(self):
        name = self.ids.name_field.text
        registration_number = self.ids.registration_number.text
        img = self.v_img
        app = MDApp.get_running_app()
        user_id = app.current_user
        try:
            fetch.grant_temporary_access(user_id, registration_number, name, img, expiration_minutes=60)
            self.display_success_dialog()
            return True
        except Exception as e:
            error_message = str(e)
            self.display_failure_dialog(error_message)
            print(f"Error granting temporary access: {error_message}")
            return error_message




    def display_success_dialog(self):
        qr_image = self.generate_qr_code()  # Call a function to generate QR code
        dialog = MDDialog(
            title="Success!",
            text="Access granted successfully.",
            buttons=[
                MDRaisedButton(
                    text="Download QR",
                    on_release=lambda x: self.download_qr(qr_image)
                )
            ],
        )
        dialog.ids.dialog_content.add_widget(Image(texture=qr_image.texture))
        dialog.open()

    def display_failure_dialog(self, error_message):
        dialog = MDDialog(
            title="Access Failed",
            text=f"Error: {error_message}",
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def generate_qr_code(self):
        # Call the function to generate QR code here and return the Image texture
        # Replace the following line with your actual QR code generation logic
        app = MDApp.get_running_app()
        qr_fetch = fetch.fetch_temporary_access(app.current_user)
        print(qr_fetch)
        if qr_fetch:
            vehicle_image_bytes = BytesIO(qr_fetch['qr_code_blob']).read()
            qr_image = CoreImage(BytesIO(vehicle_image_bytes), ext='png').texture
            return qr_image
        # return Image(source="path_to_your_qr_code_image.png").texture

    def download_qr(self, qr_image):
        # Save the QR code to the device
        qr_image.texture.save("downloaded_qr_code.png")


class MyApp(MDApp):
    def on_start(self):
        # Initialize current_user_type attribute
        self.current_user_type = None
        self.current_user = None
        self.message_list = None
        Clock.schedule_once(self.load_notifications)

    def open_menu(self, button):
        menu_items = [
            {"viewclass": "MenuContent", "text": "Broadcast Notification"},
            {"viewclass": "MenuContent", "text": "Private Notification"},
            {"viewclass": "MenuContent", "text": "Personnel Notification"},
            {"viewclass": "MenuContent", "text": "Logout"},
        ]
        menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            position="auto",
            width_mult=4,
        )
        menu.open()

    def handle_menu_item(self, item_text):
        if item_text == "Broadcast Notification":
            self.root.current = ''
        elif item_text == "Private Notification":
            self.root.current = ''
        elif item_text == "Personnel Notification":
            self.root.current = ''
        elif item_text == "logout":
            self.root.current = 'login'

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
        BS = BroadcastScreen()
        PNS = Personal_Notification_Screen()
        SAS = Security_Alert_Screen()
        security_screen = SecurityScreen()
        user_screen = UserScreen()
        user_view_vehicle = User_View_Vehicles()
        temp_access = Temporary_Access()

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
        screen_manager.add_widget(BS)
        screen_manager.add_widget(SAS)
        screen_manager.add_widget(PNS)
        screen_manager.add_widget(user_view_vehicle)
        screen_manager.add_widget(temp_access)

        return screen_manager

    def verify_login(self, username, password):
        try:
            # Call the function to get user credentials
            credentials = get_user_credentials(username, password)
            self.current_user = credentials.get('user_id')

            if credentials:
                # Check the 'usertype' to determine the appropriate screen
                usertype = credentials.get('usertype')
                self.current_user_type = usertype
                if usertype == 'admin':
                    self.root.current = 'admin'
                elif usertype == 'personnel':
                    self.root.current = 'security'
                elif usertype == 'user':
                    self.root.current = 'user'
                    Clock.schedule_once(self.load_notifications, 0)
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

    def get_user_vehicle_qr(self):
        user_vehicle = fetch.fetch_user_vehicle_details(self.current_user)
        for i in user_vehicle:
            vehicle_image_bytes_1 = BytesIO(i['qr_code_image']).read()
            qr_image = CoreImage(BytesIO(vehicle_image_bytes_1), ext='png').texture

            return qr_image

    def get_user_vehicles(self):
        user_vehicles = fetch.fetch_user_vehicle_details(self.current_user)
        return user_vehicles

    def load_notifications(self, dt):
        # Load notifications from the database
        if self.current_user_type == 'personnel':

            self.new_notifications = fetch.fetch_security_notifications(self.current_user)

            self.display_new_notifications()

            # Schedule periodic check for new notifications
            Clock.schedule_interval(self.periodic_check_notifications, 30)  # Check every 30 seconds
        elif self.current_user_type == 'user':
            self.new_notifications = fetch.fetch_user_notifications(self.current_user)
            self.display_new_notifications()

            Clock.schedule_interval(self.periodic_check_notifications, 30)

    def periodic_check_notifications(self, *args):
        # Check for new notifications periodically
        if self.current_user_type == 'user':
            new_notifications = fetch.fetch_user_notifications(self.current_user)
            for notification in new_notifications:
                if notification not in self.new_notifications:
                    self.new_notifications.append(notification)
                    self.display_notification(notification)

        elif self.current_user_type == 'personnel':
            new_notifications = fetch.fetch_security_notifications(self.current_user)
            for notification in new_notifications:
                if notification not in self.new_notifications:
                    self.new_notifications.append(notification)
                    self.display_notification(notification)

    def send_notification(self, sender, receiver_type, message):
        fetch.insert_user_notification(sender, receiver_type, message)
        # self.refresh_notifications()

    def display_new_notifications(self):
        # Display only new notifications
        for notification in self.new_notifications:
            self.display_notification(notification)

    def display_notification(self, notification):
        print(notification)
        # Display notification as a popup on the respective screen
        if notification:
            dialog = MDDialog(
                title=f"New Notification",
                text=notification['message'],
                buttons=[
                    MDRaisedButton(
                        text="OK",
                        on_release=lambda x: (self.handle_notification_seen(notification['id']), dialog.dismiss())
                    )
                ]
            )
            dialog.open()

    def handle_notification_seen(self, notification_id):
        # Update the 'seen' status of the notification
        fetch.update_notification_seen(notification_id)

    def refresh_notifications(self):
        # Reload notifications to reflect the latest changes
        self.load_notifications()

    def get_username(self, user_id):
        # Retrieve username based on the user_id
        # Implement this based on your actual database structure
        return "admin"  # Replace with the actual logic


if __name__ == "__main__":
    MyApp().run()
