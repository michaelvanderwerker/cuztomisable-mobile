from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.properties import BooleanProperty
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from functools import partial
import requests

class ResetVerify(MDScreen):

	title = 'Verify Reset Code'
	name = 'reset_verify'
	in_progress = BooleanProperty(False)

	def __init__(self, **kw):
		super().__init__(**kw)

	def on_pre_enter(self, *args):
		Clock.schedule_once(partial(self.verify, False), 0.25)

	def on_leave(self, *args):
		self.in_progress = False
		self.ids.code.text = ''

	def verify(self, code = False, *args):
		store = JsonStore('assets/authentication.json')
		if 'token' in store.get('password'):
			self.clear(['code'])
			if self.in_progress:
				return False;
			self.in_progress = True
			Clock.schedule_once(partial(self.process, code), 0.25)
		else:
			# The reset token was not found and the user shouldn't be here
			MDApp.get_running_app().root.ids.main_screen_manager.current = 'login'

	def process(self, code, *args):
		store = JsonStore('assets/authentication.json')
		token = store.get('password')['token']
		if code == '':
			self.ids.code.error = True
			self.ids.code.helper_text = 'The code is required.'
			self.in_progress = False
			return
		request = requests.get(
			'http://localhost:8000/password/forgot/'+token+'/verify'+(('/'+code) if code != False else '' ),
			headers={'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
		)
		# Sets up the response parameters
		response = request.json()
		self.in_progress = False
		if request.status_code != 200:
			MDApp.get_running_app().root.ids.main_screen_manager.current = 'login'
		elif code != False:
			store.put('password', code=code, token=token)
			MDApp.get_running_app().root.ids.main_screen_manager.current = 'reset'

	def resend(self):
		store = JsonStore('assets/authentication.json')
		if 'token' in store.get('password'):
			self.clear(['code'])
			if self.in_progress:
				return False;
			self.in_progress = True
			Clock.schedule_once(partial(self.processResend), 0.25)
		else:
			# The reset token was not found and the user shouldn't be here
			MDApp.get_running_app().root.ids.main_screen_manager.current = 'login'

	def processResend(self, *args):
		token = store.get('password')['token']
		request = requests.get(
			'http://localhost:8000/password/forgot/'+token+'/send',
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