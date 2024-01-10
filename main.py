from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivy.uix.label import Label


#Builder.load_file('main.kv')

class SecureGate(MDBoxLayout, Screen):
    pass

class MainApp(MDApp):
    def build(self):
        Window.size = (375, 600)
        return SecureGate()

if __name__ == '__main__':
    MainApp().run()

