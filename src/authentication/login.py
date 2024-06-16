from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.storage.jsonstore import JsonStore
from kivy.properties import BooleanProperty
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from functools import partial
import requests

class Login(MDScreen):

	title = 'Login'
	name = 'login'
	in_progress = BooleanProperty(False)
	store = JsonStore('assets/authentication.json')

	def __init__(self, **kw):
		super().__init__(**kw)

	def on_leave(self, *args):
		self.in_progress = False
		self.ids.username.text = ''
		self.ids.password.text = ''

	def login(self):
		self.clear(['username', 'password'])
		if self.in_progress:
			return False;
		self.in_progress = True
		Clock.schedule_once(partial(self.process), 0.25)

	def process(self, *args):
		parameters = {
			'username': self.ids.username.text,
			'password': self.ids.password.text,
		};
		request = requests.post(
			'http://localhost:8000/login',
			data=parameters,
			headers={'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
		)
		# Sets up the response parameters
		response = request.json()
		if request.status_code != 200:
			if 'errors' in response:
				for key, value in response['errors'].items():
					self.ids[key].error = True
					self.ids[key].helper_text = self.output_error(response, key)
			else:
				self.ids.username.error = True
				self.ids.username.helper_text = response['message']
		else:
			MDApp.get_running_app().setMessage(response['message'], 'success')
			if response['multi_factor_authentication']:
				self.store.put('mfa', token=response['token'])
				MDApp.get_running_app().root.ids.main_screen_manager.current = 'mfa_verify'
			else:
				store = JsonStore('assets/user.json')
				store.put('user', name=response['user']['name'], phone=response['user']['phone'], email=response['user']['email'], image=response['user']['image'], token=response['token'])
				MDApp.get_running_app().root.ids.main_screen_manager.current = 'dashboard'
		self.in_progress = False

	def output_error(self, response, key):
		return response['errors'][key][0] or 'There is an error with this field'

	def clear(self, keys):
		if isinstance(keys, list):
			for key in keys:
				self.ids[key].error = False
				self.ids[key].helper_text = ''
		else:
			self.ids[keys].error = False
			self.ids[keys].helper_text = ''