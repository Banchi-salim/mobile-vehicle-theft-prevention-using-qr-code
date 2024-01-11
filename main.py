from kivy.clock import Clock
from kivy.core import window
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix import *
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField

# Define screens for different user roles
Builder.load_file('main.kv')

# Define Screens
class SplashScreen(Screen):
    def on_enter(self, *args):
        # Schedule a callback to switch to the login screen after 15 seconds
        #Clock.schedule_once(lambda dt: self.switch(), 5)
        pass

    def switch(self):
        self.manager.current = 'login'
class LoginScreen(MDScreen):
    pass


class UserScreen(Screen):
    pass


class SecurityScreen(Screen):
    pass


class AdminScreen(Screen):
    pass


# Create the screen manager
class SecureGate(MDApp):
    def build(self):
        Window.size = (400, 600)
        self.sm = ScreenManager()
        self.sm.add_widget(SplashScreen())
        self.sm.add_widget(LoginScreen())
        self.sm.add_widget(UserScreen())
        self.sm.add_widget(SecurityScreen())
        self.sm.add_widget(AdminScreen())
        return self.sm

    def login(self, username, password):
        # Add your authentication logic here (e.g., check username and password)
        # For simplicity, let's assume all users have the same password
        '''if password == 'password':
            if username == 'admin':
                self.sm.current = 'admin'
            elif username == 'security':
                self.sm.current = 'security'
            else:
                self.sm.current = 'user'
        '''
        self.sm.current = 'admin'

    def logout(self):
        self.sm.current = 'login'


if __name__ == '__main__':
    SecureGate().run()
