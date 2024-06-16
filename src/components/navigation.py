from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.gridlayout import MDGridLayout
from kivy.properties import ObjectProperty
from kivy.storage.jsonstore import JsonStore

class Navigation(MDGridLayout):

	object_root = ObjectProperty()

	def __init__(self, *args, **kwargs):
		MDGridLayout.__init__(self, *args, **kwargs)
		Builder.load_file('views/navigation.kv')

	def logout(self):
		store = JsonStore('assets/user.json')
		store.put('user', token=None)
		MDApp.get_running_app().setMessage('You have logged out!', 'success')
		MDApp.get_running_app().root.ids.main_screen_manager.current = 'login'