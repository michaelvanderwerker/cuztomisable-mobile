from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import BooleanProperty
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from functools import partial
import requests
import weakref

from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.button import MDTextButton
class MFAVerify(MDScreen):

	title = 'Verify MFA'
	name = 'mfa_verify'
	in_progress = BooleanProperty(False)

	def __init__(self, **kw):
		super().__init__(**kw)

	def on_pre_enter(self, *args):
		Clock.schedule_once(partial(self.verify, False), 0.25)

	def on_leave(self, *args):
		self.in_progress = False
		#self.ids.code.text = ''

	def verify(self, *args):
		store = JsonStore('assets/authentication.json')
		if 'token' in store.get('mfa'):
			#self.clear(['code'])
			if self.in_progress:
				return False;
			self.in_progress = True
			Clock.schedule_once(partial(self.process), 0.35)
		else:
			# The reset token was not found and the user shouldn't be here
			MDApp.get_running_app().root.ids.main_screen_manager.current = 'login'

	def process(self, *args):
		store = JsonStore('assets/authentication.json')
		token = store.get('mfa')['token']
		request = requests.get(
			'http://localhost:8000/login/mfa/'+token+'/verify',
			headers={'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
		)
		# Sets up the response parameters
		response = request.json()
		if request.status_code != 200:
			MDApp.get_running_app().root.ids.main_screen_manager.current = 'login'
		else:
			self.ids.form_layout.clear_widgets()
			# Removes any old widgets
			if response['email'] != None:
				layout = MDBoxLayout(size_hint_y=None, size_hint_x=None, height=50)
				self.ids['email_checkboxes'] = weakref.ref(layout)
				self.ids.form_layout.add_widget(layout)
				checkbox = MDCheckbox(ripple_scale=0, group='mfa-group', size_hint_x=None, active=True, allow_no_selection=False, width=22)
				self.ids.email_checkboxes.add_widget(checkbox)
				self.ids.email_checkboxes.add_widget(MDTextButton(id='email_checkbox_button', pos_hint={"center_x": 0.5, "center_y": 0.5}, text=response['email'], on_release=self.select, size_hint_y=None, padding=[15,0,0,0], height=8))
				self.ids['email_checkbox'] = weakref.ref(checkbox)
			if response['phone'] != None:
				layout = MDBoxLayout(size_hint_y=None, size_hint_x=None, height=50)
				self.ids['phone_checkboxes'] = weakref.ref(layout)
				self.ids.form_layout.add_widget(layout)
				checkbox = MDCheckbox(ripple_scale=0, group='mfa-group', size_hint_x=None, allow_no_selection=False, width=22)
				self.ids.phone_checkboxes.add_widget(checkbox)
				self.ids.phone_checkboxes.add_widget(MDTextButton(id='phone_checkbox_button', pos_hint={"center_x": 0.5, "center_y": 0.5}, text=response['phone'], on_release=self.select, size_hint_y=None, padding=[15,0,0,0], height=8))
				self.ids['phone_checkbox'] = weakref.ref(checkbox)
		self.in_progress = False

	def select(self, item):
		if item.id == 'email_checkbox_button':
			self.ids.email_checkbox.active = True
		if item.id == 'phone_checkbox_button':
			self.ids.phone_checkbox.active = True

	def send(self):
		store = JsonStore('assets/authentication.json')
		if 'token' in store.get('mfa'):
			if self.in_progress:
				return False;
			self.in_progress = True
			Clock.schedule_once(partial(self.processSend), 0.35)
		else:
			# The reset token was not found and the user shouldn't be here
			MDApp.get_running_app().root.ids.main_screen_manager.current = 'login'

	def processSend(self, *args):
		store = JsonStore('assets/authentication.json')
		token = store.get('mfa')['token']
		if 'email_checkbox' in self.ids and self.ids.email_checkbox.active:
			sendType = 'email'
		elif 'phone_checkbox' in self.ids and self.ids.phone_checkbox.active:
			sendType = 'phone'
		parameters = {
			'type': sendType,
		}
		request = requests.post(
			'http://localhost:8000/login/mfa/'+token+'/send',
			data=parameters,
			headers={'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
		)
		# Sets up the response parameters
		response = request.json()
		if request.status_code != 200:
			MDApp.get_running_app().setMessage(response['message'], 'danger')
		else:
			MDApp.get_running_app().setMessage(response['message'], 'success')
			MDApp.get_running_app().root.ids.main_screen_manager.current = 'mfa'
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