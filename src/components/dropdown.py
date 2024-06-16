from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import ObjectProperty, StringProperty
from kivy.metrics import dp

class Dropdown(MDBoxLayout):

	caller = ObjectProperty()
	output = ObjectProperty()
	name_key = StringProperty()
	subtitle_key = StringProperty()
	value_key = StringProperty()

	def create(self, caller, items):
		self.menu_items = [
			{
				'text': items[index][self.name_key],
				'height': dp(62),
				'font_style': 'Body2',
				'secondary_text': str(items[index][self.subtitle_key]),
				'secondary_font_style': 'Caption',
				'viewclass': 'TwoLineListItem',
				'on_release': lambda x=items[index]: self.menu_callback(x),
			} for index in range(len(items))
		]
		# Creates the menu object
		self.menu = MDDropdownMenu(
			caller=self.caller,
			items=self.menu_items,
			width=dp(310),
			position='center'
		)
		self.menu.open()

	def menu_callback(self, item):
		self.output.text = str(item[self.value_key])
		self.output.helper_text = item[self.name_key]
		self.output.helper_text_mode = 'persistent'
		self.output.line_color_normal = 'grey'
		self.menu.dismiss()