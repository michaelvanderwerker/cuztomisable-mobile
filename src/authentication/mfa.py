from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.properties import BooleanProperty
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from functools import partial
import requests

class MFA(MDScreen):

	title = 'Multi-Factor Authentication'
	name = 'mfa'
	in_progress = BooleanProperty(False)

	def __init__(self, **kw):
		super().__init__(**kw)

	def on_leave(self, *args):
		self.in_progress = False
		self.ids.code.text = ''
		self.ids.remember.active = False

	def verify(self):
		store = JsonStore('assets/authentication.json')
		if 'token' in store.get('mfa'):
			self.clear(['code', 'remember'])
			if self.in_progress:
				return False;
			self.in_progress = True
			Clock.schedule_once(partial(self.process), 0.25)
		else:
			# The reset token was not found and the user shouldn't be here
			MDApp.get_running_app().root.ids.main_screen_manager.current = 'login'

	def process(self, *args):
		store = JsonStore('assets/authentication.json')
		token = store.get('mfa')['token']
		parameters = {
			'code': self.ids.code.text,
			'remember': 1 if self.ids.remember.active else 0,
		};
		request = requests.post(
			'http://localhost:8000/login/mfa/'+token,
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
				self.ids.code.error = True
				self.ids.code.helper_text = response['message']
		else:
			store = JsonStore('assets/user.json')
			store.put('user', name=response['user']['name'], phone=response['user']['phone'], email=response['user']['email'], image=response['user']['image'], token=response['token'])
			MDApp.get_running_app().root.ids.main_screen_manager.current = 'dashboard'
		self.in_progress = False

	def resend(self):
		store = JsonStore('assets/authentication.json')
		if 'token' in store.get('mfa'):
			self.clear(['code', 'remember'])
			if self.in_progress:
				return False;
			self.in_progress = True
			Clock.schedule_once(partial(self.processResend), 0.25)
		else:
			# The reset token was not found and the user shouldn't be here
			MDApp.get_running_app().root.ids.main_screen_manager.current = 'login'

	def processResend(self, *args):
		token = store.get('mfa')['token']
		request = requests.get(
			'http://localhost:8000/login/mfa/'+token+'/send',
			headers={'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
		)
		# Sets up the response parameters
		response = request.json()
		if request.status_code != 200:
			self.ids.code.error = True
			self.ids.code.helper_text = response['message']
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