from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.properties import BooleanProperty
from kivy.clock import Clock
from functools import partial
import requests
import re

class Register(MDScreen):

	title = 'Register'
	name = 'register'
	in_progress = BooleanProperty(False)
	password_requirements_met = BooleanProperty(False)

	def __init__(self, **kw):
		super().__init__(**kw)

	def on_leave(self, *args):
		self.in_progress = False
		self.ids.first_name.text = ''
		self.ids.last_name.text = ''
		self.ids.email.text = ''
		self.ids.password.text = ''

	def check(self):
		self.password_requirements_met = False
		password = self.ids.password.text
		self.ids.minimum_characters_checkbox.icon = 'checkbox-marked-outline' if len(password) >= 8 else 'checkbox-blank-outline'
		self.ids.special_characters_checkbox.icon = 'checkbox-marked-outline' if len(password) - len(re.findall('[\w]', password)) >= 1 else 'checkbox-blank-outline'
		self.ids.uppercase_characters_checkbox.icon = 'checkbox-marked-outline' if sum(1 for c in password if c.isupper()) >= 1 else 'checkbox-blank-outline'
		self.ids.number_checkbox.icon = 'checkbox-marked-outline' if any(char.isdigit() for char in password) else 'checkbox-blank-outline'
		# Checks to make sure the requiremetns were met
		if (self.ids.minimum_characters_checkbox.icon == 'checkbox-marked-outline' and
			self.ids.special_characters_checkbox.icon == 'checkbox-marked-outline' and
			self.ids.uppercase_characters_checkbox.icon == 'checkbox-marked-outline' and
			self.ids.number_checkbox.icon == 'checkbox-marked-outline'):
			self.password_requirements_met = True

	def register(self):
		self.clear(['first_name', 'last_name','email', 'password'])
		if self.in_progress:
			return False;
		self.in_progress = True
		Clock.schedule_once(partial(self.process), 0.35)

	def process(self, *args):
		parameters = {
			'first_name': self.ids.first_name.text,
			'last_name': self.ids.last_name.text,
			'email': self.ids.email.text,
			'password': self.ids.password.text,
		};
		request = requests.post(
			'http://localhost:8000/register',
			data=parameters,
			headers={'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
		)
		# Sets up the response parameters
		response = request.json()
		print(response)
		if request.status_code != 200:
			if 'errors' in response:
				for key, value in response['errors'].items():
					self.ids[key].error = True
					self.ids[key].helper_text = self.output_error(response, key)
			else:
				MDApp.get_running_app().setMessage(response['message'], 'danger')
		else:
			MDApp.get_running_app().setMessage(response['message'], 'success')
			MDApp.get_running_app().root.ids.main_screen_manager.current = 'login'
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