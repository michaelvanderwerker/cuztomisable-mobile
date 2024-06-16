from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.properties import BooleanProperty
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial

#  Import the python files defining the Screens
from src.authentication.forget import Forget
from src.authentication.login import Login
from src.authentication.mfa import MFA
from src.authentication.mfa_verify import MFAVerify
from src.authentication.register import Register
from src.authentication.reset import Reset
from src.authentication.reset_verify import ResetVerify
from src.dashboard import Dashboard

class Dashboard(MDScreen):

	title = 'Dashboard'
	name = 'dashboard'

class MainApp(MDApp):

	window_height = Window.size[1]
	messages = []

	def build(self):
		self.theme_cls.theme_style = 'Light'
		self.theme_cls.primary_palette = 'Blue'
		Window.size = (360, 640)
		return Builder.load_file('views/app.kv')

	def output_error():
		pass

	def setMessage(self, message, type):
		color = 'red' if type == 'danger' else 'green'
		item = MDLabel(text=message, size_hint_y=None, height=60, color='white', padding=[15, 0], opacity=0)
		item.md_bg_color = color
		item.color='white'
		self.root.ids.messages.add_widget(item)
		anim = Animation(opacity=1, duration=0.35)
		anim.start(item)
		Clock.schedule_once(partial(self.clearMessage, item), 6)

	def clearMessage(self, item, *args):
		self.root.ids.messages.remove_widget(item)


if __name__ == '__main__':
	MainApp().run()