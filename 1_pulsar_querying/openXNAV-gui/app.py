import re
import pandas as pd
import os
import kivymd.uix
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import StringProperty
from kivy.properties import *
from kivy.clock import Clock
from queryPulsar import *
import copy
import time
import numpy as np
from kivymd.uix.label import MDLabel


from kivy.core.window import Window
Window.size = (1920/2, 1080/2)

_root_app = False

def updateText(obj, formatFunc, txt):
	newText = formatFunc(txt)
	obj.text = newText

def setEnabled(button, isEnabled):
	button.disabled = not isEnabled

class StartPage(MDScreen):
	def __init__(self, **kwargs):
		super(MDScreen, self).__init__(**kwargs)
		# lambda functions
		self.generateLoadingText = lambda txt : "\n\n[b][font=Gentona-BookItalic][size=15sp]{}[/b][/size][/font]".format(txt)
		self.generateButtonText = lambda txt : "[font=Gentona-Bold]{}[/font]".format(txt)

		self.stack = []
		self.num_delayed = 0
		self.db_processing_event = None

		Clock.schedule_once(self._on_load_complete)

	def _on_load_complete(self, dt):

		# kivy objects
		progressBar = self.ids.progress
		loading_text = self.ids.loadingText
		startButton = self.ids.startButton
		# lambda functions
		generateLoadingText = self.generateLoadingText
		generateButtonText = self.generateButtonText
		
		# initialize
		updateText(startButton, generateButtonText, "LAUNCH APPLICATION")
		setEnabled(startButton, False) # disable button until we check for existing db
		updateText(loading_text, generateLoadingText, "Checking for existing pulsar database . . .")
		progressBar.start()

		## check for existing database
		hasExistingDatabase = self.checkForExistingDatabase("pulsar_database/")
		if hasExistingDatabase: 
			Clock.schedule_once(lambda x: self.setup_existingDatabase(progressBar, loading_text, startButton), 1.5)
		else: 
			Clock.schedule_once(lambda x: self.setup_generateDatabase(progressBar, loading_text, startButton), 1.5)
	

	#############
	## UTILITY ##
	#############

	def setup_existingDatabase(self, progressBar, loading_text, startButton): 
		updateText(loading_text, self.generateLoadingText, "Found existing database!")
		progressBar.stop()
		setEnabled(startButton, True)
		return

	def setup_generateDatabase(self, progressBar, loading_text, startButton):
		progressBar.stop()
		progressBar.type = 'determinate'
		progressBar.color = _root_app.theme_cls.accent_color
		self.generatePulsarDatabase(progressBar, loading_text)

	def checkForExistingDatabase(self, database_directory):
		if not os.path.exists(database_directory):
			os.mkdir(database_directory)
			return False
		else: 
			return True

	def generatePulsarDatabase(self, progressBar, loading_text, root_directory="pulsar_database/"):
		# first, grab all known pulsars
		db = _root_app.psrdb.full_database()
		progressBar.max = len(db)

		truncated_db = db[['PSRJ','PEPOCH', 'DECJ', 'RAJD']]
		truncated_db = truncated_db.values.tolist()

		self.db_processing_event = Clock.schedule_interval(lambda x: self.handleSinglePulsarEntry(), 0.001)

		for i in range(0, len(truncated_db)):
			pulsar = truncated_db[i]
			p = Pulsar(pulsar[0], pulsar[1], pulsar[2], pulsar[3])
			self.stack.append(copy.deepcopy(p))


	def handleSinglePulsarEntry(self):
		start = time.perf_counter()
		progressBar = self.ids.progress
		loading_text = self.ids.loadingText
		startButton = self.ids.startButton
		root_directory = "pulsar_database/"

		if len(self.stack) > 0:
			pulsar = self.stack.pop()
			pulsar.saveToFile(root_directory)
			updateText(loading_text, self.generateLoadingText, "Loading {} into database . . .".format(pulsar.p_name))
			progressBar.value = progressBar.value + 1
		else: 
			self.db_processing_event.cancel()
			updateText(loading_text, self.generateLoadingText, "Successfully generated pulsar database!")
			setEnabled(startButton, True) 

		stop = time.perf_counter()
		if stop - start > 0.5:
			self.num_delayed = self.num_delayed + 1



			

class QueryPage(MDScreen):
	def __init__(self, **kwargs):
		super(MDScreen, self).__init__(**kwargs)
		self.raj1 = None
		self.dec1 = None
		self.rad1 = None
		self.tag1 = None

		self.outputStack = []
		self.bannerStack = []

		self.outputDisplay = None
		self.outputBanner = None

		self.generateOutputText = lambda txt : "[font=Gentona-Book]{}[/font]".format(txt)

		Clock.schedule_once(self._on_load_complete)

	def _on_load_complete(self, dt):
		self.raj1 = self.ids.raj1.text
		self.dec1 = self.ids.dec1.text
		if self.rad1 != None and self.rad1 != "": 
			self.rad1 = float(self.ids.rad1.text)
		self.tag1 = self.ids.tag1.text
		self.outputDisplay = self.ids.output_display
		self.outputBanner = self.ids.output_banner

		setEnabled(self.ids.find_pulsars_button, True)

	def setRAJ1(self, user_input):
		self.raj1 = user_input

	def setDEC1(self, user_input):
		self.dec1 = user_input

	def setRAD1(self, user_input):
		self.rad1 = float(user_input)

	def setTag(self, user_input):
		print(self.tag1)
		self.tag1 = user_input

	def updateOutputDisplay(self, display, stack):
		display.clear_widgets()
		for i in range(0, len(stack)):
			display.add_widget(stack[i])
		stack = []

	def findPulsars(self):
		print("Your query: " + str(self.raj1) + str(self.dec1) + str(self.rad1))
		if len(str(self.raj1)) > 0 and  len(str(self.dec1)) > 0 and  len(str(self.rad1)) > 0:
			result = _root_app.psrdb.query(self.raj1, self.dec1, self.rad1)
			# result = _root_app.psrdb.query("17:47:26", "65.64", 15)

			truncated_db = result[['PSRJ','PEPOCH', 'DECJ', 'RAJD']]
			truncated_db = truncated_db.values.tolist()

			data_directory = "query_results/"
			if not os.path.exists(data_directory):
				os.mkdir(data_directory)

			print("tag")
			print(self.tag1)
			if self.tag1 != None and self.tag1 != "" and len(str(self.tag1)) > 0: 
				if len(self.tag1) > 0:
					data_directory = data_directory + self.tag1 + "/"

			else: 
				full_str = str(self.raj1) + str(self.dec1) + str(self.rad1)
				auto_gen_tag = re.sub(r'[^a-zA-Z0-9]', '', full_str)
				data_directory = data_directory + auto_gen_tag + "/"
			
			if not os.path.exists(data_directory):
					os.mkdir(data_directory)

			if len(truncated_db) > 0:
				banner_str = "[b]{} pulsars found.[/b]".format(str(len(truncated_db))) + "\nResults saved to: " + data_directory
				self.outputBanner.text = self.generateOutputText(banner_str)
				
				for pulsar in truncated_db:
					p = Pulsar(pulsar[0], pulsar[1], pulsar[2], pulsar[3])
					nameLabel = "id-" + str(pulsar[0])
					output_str = self.generateOutputText(str(pulsar[0]))
					output_widget = MDLabel(id=nameLabel, adaptive_height=True, markup=True, text=output_str, theme_text_color='Secondary', size_hint=[1.0, 0.1])
					self.outputStack.append(output_widget)
					p.saveToFile(data_directory)
			else: 
				self.outputBanner.text = self.generateOutputText("No pulsars found from this query. Adjust the parameters and try again.".format(str(len(truncated_db)))) 

			self.updateOutputDisplay(self.outputDisplay, self.outputStack)
			print("Results saved to: " + data_directory)


class ScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(ScreenManager, self).__init__(**kwargs)

    def changeScreen(self, screen_name):
        self.current = screen_name



class MainApp(MDApp):
	def build(self):
		global _root_app
		_root_app = self

		self.psrdb = PulsarDatabase()
		self.pulsar_dict = {}

		## theme ##
		self.theme_cls.theme_style = "Dark"
		self.theme_cls.primary_palette = "Gray"
		self.theme_cls.accent_palette = "Blue"

		## icon ##
		self.icon = '23-03611_OpenXNav_Color-icon.png'
		self.title = 'OpenXNAV'

		self.sm = ScreenManager()

		return self.sm

	