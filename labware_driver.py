#!/usr/bin/env python3

#import serial
import asyncio, json, copy
import datetime
import sys
from collections import Callable
import labware



class LabwareDriver(object):
	"""

	How data flows to and from Smoothieboard:

	To:




	From:

	1. Data coming in is split up by delimiter ('\n') and then
	each section is sent to a callback (labwareDriver._data_handler)
	The raw data is then sent to another callback (SmoothieDriver._raw_data_handler)

	Function: Output.data_received()
	-> _data_handler - callback for raw data
	-> _raw_data_handler - callback for chunks of data separated by delimiter

	2. In labwareDriver._data_handler data is divided between text data and
	JSON data, serial text data formatted for JSON. Either way, the data is then 
	reformatted into a list of standardized dictionary objects with the following format:

	[
		{
		  [MESSAGE]:
			{ 
			  [PARAMETER]:[VALUE],
			  ...
			}
		},
		...
	]

	3. The standard dictionary object is checked for specific flow control data and 
	flow control logic is updated accordingly.

	4. The standard dictionary object is then routed to the appropriate callback based
	on the message


	"""




	def __init__(self, simulate=False):
		"""
		"""
		print(datetime.datetime.now(),' - labware_driver.__init__:')
		print('\targs:',locals())
		self.simulation = simulate
		self.the_loop = asyncio.get_event_loop()
		self.command_queue = []
		self.simulation_queue = []
	
		#self.smoothie_transport = None
		self.session = None

		self.the_loop = None

		self.state_dict = {
			'name':'labware',
			'simulation':False,
			'connected':False,
			'queue_size':0
		}


		self.callbacks_dict = {}
		#  {
		#    <callback_name>:
		#    {
		#      callback: <CALLBACK OBJECT>,
		#      messages: [ <messages>... ]
		#    },
		#    ...
		#  }

		self.meta_callbacks_dict = {
			'on_connect' : None,
			'on_disconnect' : None,
			'on_empty_queue' : None,
		#	'on_raw_data' : None
		}

		#self.commands_dict = {
		#	"move":{
		#		"code":"G91 G0",
		#		"parameters":["","X","Y","Z","A","B"]
		#	}
		#}


	def callbacks(self):
		"""
		"""
		print(datetime.datetime.now(),' - labware_driver.callbacks')
		return_dict = {}
		for name, value in self.callbacks_dict.items():
			return_dict[name] = value['messages']
		return return_dict
		#return copy.deepcopy(self.callbacks_dict)


	def meta_callbacks(self):
		"""
		"""
		print(datetime.datetime.now(),' - labware_driver.meta_callbacks')
		return_dict = dict()
		for name, value in self.meta_callbacks_dict.items():
			if value is not None and isinstance(value, Callable):
				return_dict[name] = value.__name__
			else:
				return_dict[name] = 'None'
		# cannot just send back copy becuase NoneObject causes problem
		#return copy.deepcopy(self.meta_callbacks_dict)
		return return_dict


	def set_meta_callback(self, name, callback):
		"""
		name should correspond 
		"""
		print(datetime.datetime.now(),' - labware_driver.set_meta_callback:')
		print('\targs:',locals())
		if name in self.meta_callbacks_dict and isinstance(callback, Callable):
			self.meta_callbacks_dict[name] = callback
		else:
			return '{error:name not in meta_callbacks or callback is not Callable}'
		return self.meta_callbacks()


	def add_callback(self, callback, messages):
		"""
		"""
		print(datetime.datetime.now(),' - labware_driver.add_callback:')
		print('\targs:',locals())
		if callback.__name__ not in list(self.callbacks_dict):
			if isinstance(messages, list):
				self.callbacks_dict[callback.__name__] = {'callback':callback, 'messages':messages}
			else:
				self.callbacks_dict[callback.__name__] = {'callback':callback, 'messages':[messages]}
		elif message not in self.callbacks_dict[callback.__name__]['messages']:
			if isinstance(messages, list):
				self.callbacks_dict[callback.__name__]['messages'].extend(messages)
			else:
				self.callbacks_dict[callback.__name__]['messages'].append(messages)


	def remove_callback(self, callback_name):
		"""
		"""
		print(datetime.datetime.now(),' - labware_driver.remove_callback:')
		print('\targs:',locals())
		del self.callbacks_dict[callback_name]


	def flow(self):
		"""
		"""
		print(datetime.datetime.now(),' - labware_driver.flow')
		return copy.deepcopy(self.state_dict)


	def clear_queue(self):
		"""
		"""
		print(datetime.datetime.now(),' - labware_driver.clear_queue')
		self.command_queue = []
		self.state_dict['queue_size'] = len(self.command_queue)
	#	self.state_dict['ack_received'] = True
	#	self.state_dict['ack_ready'] = True


	def connect(self, session_id):
		"""
		"""
		print(datetime.datetime.now(),' - labware_driver.connect called:')
		print('\targs:',locals())
		self.session = Session(session_id)
		self._on_connection_made(session_id)
			

	def close(self, session_id):
		"""
		"""
		print(datetime.datetime.now(),' - labware_driver.close')
	#	self.smoothie_transport.close()
		if self.session is not None:
			self.session.close()
		self._on_connection_lost(session_id)


	def send(self, session_id, message):
		print(datetime.datetime.now(),' - labware_driver.send:')
		print('\targs:',locals())
		self.state_dict['queue_size'] = len(self.command_queue)
		#message = message + self.config_dict['message_ender']
		if self.simulation:
			self.simulation_queue.append(message)
		
		print('CALL labware COMMAND HERE WITH:\n\
		 	self._data_handler(  * * * BOOSTRAPPER CALL * * *  )')
		self._data_handler(session_id, self.session.execute(command(message)))



# flow control 
	def _add_to_command_queue(self, session_id, command):
		print(datetime.datetime.now(),' - labware_driver._add_to_command_queue:')
		print('\targs:',locals())
		cmd = {session_id,command}
		self.command_queue.append(cmd)
		self.state_dict['queue_size'] = len(self.command_queue)
		self._step_command_queue()


	def _step_command_queue(self):
		print(datetime.datetime.now(),' - labware_driver._step_command_queue')
	#	self.lock_check()
	#	if self.state_dict['locked'] == False:
	#		if len(self.command_queue) == 0:
	#			if isinstance(self.meta_callbacks_dict['on_empty_queue'],Callable):
	#				self.meta_callbacks_dict['on_empty_queue']()
	#		else:
		self.send(self.command_queue.pop(0))


	def _format_text_data(self, text_data):
		print(datetime.datetime.now(),' - labware_driver._format_text_data:')
		print('\targs:',locals())
		return_list = []
		remainder_data = text_data
		while remainder_data.find(',')>=0:
			stupid_dict = self._format_group( remainder_data[:remainder_data.find(',')] ) 
			return_list.append(stupid_dict)
			remainder_data = remainder_data[remainder_data.find(',')+1:]
		stupid_dict = self._format_group( remainder_data )
		return_list.append(stupid_dict)
		return return_list


	def _format_group(self, group_data):
		print(datetime.datetime.now(),' - labware_driver._format_group:')
		print('\targs:',locals())
		return_dict = dict()
		remainder_data = group_data
		if remainder_data.find(':')>=0:
			while remainder_data.find(':')>=0:
				message = remainder_data[:remainder_data.find(':')].replace('\n','').replace('\r','')
				remainder_data = remainder_data[remainder_data.find(':')+1:]
				if remainder_data.find(' ')>=0:
					parameter = remainder_data[:remainder_data.find(' ')].replace('\n','').replace('\r','')
					remainder_data = remainder_data[remainder_data.find(' ')+1:]
				else:
					parameter = remainder_data.replace('\r','').replace('\n','')
					return_dict[message] = parameter
		else:
			return_dict[group_data.strip()] = ''
		return return_dict


	def _format_json_data(self, json_data):

		#
		#	{ 
		#		name : value,
		#		... ,
		#		name : { ... }???
		#	}
		#
		#
		print(datetime.datetime.now(),' - labware_driver._format_json_data:')
		print('\targs:',locals())
		return_list = []
		for name, value in json_data.items():
			if isinstance(value, dict):
				message = name
				for value_name, value_value in value.items():
					parameter = value_name
					this_dict = {}
					this_dict[message] = {}
					this_dict[message][parameter] = value_value
					return_list.append(this_dict)
			else:
				message = 'None'
				parameter = name
				this_dict = {}
				this_dict[message] = {}
				this_dict[message][parameter] = value
				return_list.append(this_dict)


		#
		#	so, if json_data looks like:
		#	{ X:<f>, Y:<f>, Z:<f>, A:<f>, B:<f> }
		#
		#	it gets turned into:
		#	[ 
		#	  {  'None':
		#			{ X:<f>, Y:<f>, Z:<f>, A:<f>, B:<f> } 
		#	  } 
		#	]
		#


		return return_list


	def _process_message_dict(self, session_id, message_dict):
		print(datetime.datetime.now(),' - labware_driver._process_message_dict:')
		print('\targs:',locals())
		# first, check if ack_received confirmation - NOT FOR LABWARE
		
		# second, check if ack_ready confirmation - NOT FOR LABWARE

		# finally, pass messages to their respective callbacks based on callbacks and messages they're registered to receive
		# eg:
		#
		#	message dict:
		#	{ 'None':
		#		{ X:<f>, Y:<f>, Z:<f>, A:<f>, B:<f> } 
		#	}
		#
		#	---->  name_message = 'None'
		#	---->  value = { X:<f>, Y:<f>, Z:<f>, A:<f>, B:<f> } 
		#
		#
		for name_message, value in message_dict.items():
			for callback_name, callback in self.callbacks_dict.items():
				if name_message in callback['messages']:
					callback['callback'](self.state_dict['name'], session_id, value)
		self._step_command_queue()


# Device callbacks
	def _on_connection_made(self, session_id):
		print(datetime.datetime.now(),' - labware_driver._on_connection_made')
		self.state_dict['connected'] = True
	#	self.state_dict['transport'] = True if self.smoothie_transport else False
		print('*\t*\t* connected!\t*\t*\t*')
		if isinstance(self.meta_callbacks_dict['on_connect'],Callable):
			self.meta_callbacks_dict['on_connect'](session_id)


	def _data_handler(self, session_id, datum):
		"""Handles incoming data from Smoothieboard that has already been split by delimiter
		"""
		print(datetime.datetime.now(),' - labware_driver._data_handler:')
		print('\targs:',locals())
		json_data = ""
		text_data = datum

		if self.config_dict['ack_received_message'] in datum:
			self.ack_received = True

		if datum.find('{')>=0:
			json_data = datum[datum.find('{'):].replace('\n','').replace('\r','')
			text_data = datum[:datum.index('{')]

		if text_data != "":
			print('\ttext_data: ',text_data)
			text_message_list = self._format_text_data(text_data)

			for message in text_message_list:
				self._process_message_dict(message)

		if json_data != "":
			print('\tjson_data: ',json_data)
			try:
				json_data_dict = json.loads(json_data)
				json_message_list = self._format_json_data(json_data_dict)
				for message in json_message_list:
					self._process_message_dict(session_id,message)
			except:
				print(datetime.datetime.now(),' - {error:driver._data_handler - json.loads(json_data)}\n\r',sys.exc_info())


	def _on_connection_lost(self, session_id):
		print(datetime.datetime.now(),' - labware_driver._on_connection_lost')
		self.state_dict['connected'] = False
	#	self.state_dict['transport'] = True if self.smoothie_transport else False
		print('*\t*\t* not connected!\t*\t*\t*')
		if isinstance(self.meta_callbacks_dict['on_disconnect'],Callable):
			self.meta_callbacks_dict['on_disconnect'](session_id)


	def send_command(self, session_id, data):
		print(datetime.datetime.now(),' - labware_driver.send_command:')
		print('\targs:',locals())
	#	"""
	#
	#	data should be in one of 2 forms:
	#
	#	1. string
	#
	#	If there is additional information to go with the command, then it should
	#	be in JSON format. We're not going to parse the string to try to get additional
	#	values to go with the command
	#
	#	2. {command:params}
	#		params --> {param1:value, ... , paramN:value}
	#
		self._add_to_command_queue(session_id, data)
	




if __name__ == '__main__':
	pass












