from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from functools import partial
import requests

class Dashboard(MDScreen):

	title = 'Dashboard'
	name = 'dashboard'

	def __init__(self, **kw):
		super().__init__(**kw)

	def on_pre_enter(self, *args):
		store = JsonStore('assets/user.json')
		if 'token' not in store.get('user') or store.get('user')['token'] == None:
			MDApp.get_running_app().setMessage('Your token has expired.', 'danger')
			MDApp.get_running_app().root.ids.main_screen_manager.current = 'login'
		else:
			self.ids.user_name.text = store.get('user')['name']

	def on_leave(self, *args):
		pass