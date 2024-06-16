from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.properties import BooleanProperty
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from functools import partial
import requests
import re

class Reset(MDScreen):

	title = 'Reset Password'
	name = 'reset'
	in_progress = BooleanProperty(False)
	password_requirements_met = BooleanProperty(False)

	def __init__(self, **kw):
		super().__init__(**kw)

	def on_leave(self, *args):
		self.in_progress = False
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

	def reset(self):
		store = JsonStore('assets/authentication.json')
		if 'token' in store.get('password') and 'code' in store.get('password'):
			self.clear(['password'])
			if self.in_progress:
				return False;
			self.in_progress = True
			Clock.schedule_once(partial(self.process), 0.25)
		else:
			# The reset token was not found and the user shouldn't be here
			MDApp.get_running_app().root.ids.main_screen_manager.current = 'login'
			return

	def process(self, *args):
		store = JsonStore('assets/authentication.json')
		token = store.get('password')['token']
		parameters = {
			'code': store.get('password')['code'],
			'password': self.ids.password.text,
		};
		request = requests.post(
			'http://localhost:8000/password/forgot/'+token,
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
				self.ids.password.error = True
				self.ids.password.helper_text = response['message']
		else:
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