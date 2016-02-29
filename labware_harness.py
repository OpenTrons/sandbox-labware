#!/usr/bin/env python3

"""
TODO:
- nose testing someday
"""

import labware_driver
import sys
import datetime
import copy

class Harness(object):

	def __init__(self, publisher=None):
		"""
		"""
		print(datetime.datetime.now(),' - labware_harness.__init__:')
		print('\n\targs: ',locals(),'\n')
		self._publisher = publisher
		self.driver_dict = {}
		self.meta_dict = {
			'drivers' : lambda from_,session_id,name,param: self.drivers(from_,session_id,name,param),
			'add_driver' : lambda from_,session_id,name,param: self.add_driver(from_,session_id,name,param),
			'remove_driver' : lambda from_,session_id,name,param: self.remove_driver(from_,session_id,name,param),
			'callbacks' : lambda from_,session_id,name,param: self.callbacks(from_,session_id,name,param),
			'meta_callbacks' : lambda from_,session_id,name,param: self.meta_callbacks(from_,session_id,name,param),
			'set_meta_callback' : lambda from_,session_id,name,param: self.set_meta_callback(from_,session_id,name,param),
			'add_callback' : lambda from_,session_id,name,param: self.add_callback(from_,session_id,name,param),
			'remove_callback' : lambda from_,session_id,name,param: self.remove_callback(from_,session_id,name,param),
			'flow' : lambda from_,session_id,name,param: self.flow(from_,session_id,name,param),
			'clear_queue' : lambda from_,session_id,name,param: self.clear_queue(from_,session_id,name,param),
			'connect' : lambda from_,session_id,name,param: self.connect(from_,session_id,name,param),
		#	'disconnect' : lambda from_,session_id,name,param: self.disconnect(from_,session_id,name,param),
			'close' : lambda from_,session_id,name,param: self.close(from_,session_id,name,param),
		#	'commands' : lambda from_,name,param: self.commands(from_,name,param),
		#	'configs' : lambda from_,name,param: self.configs(from_,name,param),
		#	'set_config' : lambda from_,name,param: self.set_config(from_,name,param)
			'meta_commands' : lambda from_,session_id,name,param: self.meta_commands(from_,session_id,name,param)
		}


	def set_publisher(self, publisher):
		"""
		"""
		print(datetime.datetime.now(),' - labware_harness.set_publisher:')
		print('\n\targs: ',locals(),'\n')
		self._publisher = publisher


	def drivers(self, from_, session_id, name, param):
		"""
		name: n/a
		param: n/a
		"""
		print(datetime.datetime.now(),'- labware_harness.drivers:')
		print('\n\targs: ',locals(),'\n')
		return_list = list(self.driver_dict)
		if name is None:
			name = 'None'
		if from_ == "":
			self._publisher.publish('frontend',from_,session_id,'labware',name,'drivers',return_list)
		else:
			self._publisher.publish(from_,from_,session_id,'labware',name,'drivers',return_list)
		return return_list


	def add_driver(self, from_, session_id, name, param):
		"""
		name: name of driver to add_driver
		param: driver object
		"""
		print(datetime.datetime.now(),' - labware_harness.add_driver:')
		print('\n\targs: ',locals(),'\n')
		self.driver_dict[name] = param
		return_list = list(self.driver_dict)
		if from_ == "":
			self._publisher.publish('frontend',from_,session_id,'labware',name,'drivers',return_list)
		else:
			self._publisher.publish(from_,from_,session_id,'labware',name,'drivers',return_list)
		return return_list


	def remove_driver(self, from_, session_id, name, param):
		"""
		name: name of driver to be driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - labware_harness.remove_driver:')
		print('\n\targs: ',locals(),'\n')
		del self.driver_dict[name]
		return_list = list(self.driver_dict)
		if from_ == "":
			self._publisher.publish('frontend',from_,session_id,'labware',name,'drivers',return_list)
		else:
			self._publisher.publish(from_,from_,session_id,'labware',name,'drivers',return_list)
		return return_list


	def callbacks(self, from_, session_id, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - labware_harness.callbacks:')
		print('\n\targs: ',locals(),'\n')
		return_dict = self.driver_dict[name].callbacks()
		if from_ == "":
			self._publisher.publish('frontend',from_,session_id,'labware',name,'callbacks',return_dict)
		else:
			self._publisher.publish(from_,from_,session_id,'labware',name,'callbacks',return_dict)
		return return_dict


	def meta_callbacks(self, from_, session_id, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - labware_harness.meta_callbacks:')
		print('\n\targs: ',locals(),'\n')
		return_dict = self.driver_dict[name].meta_callbacks()
		self._publisher.publish(from_,from_,session_id,'labware',name,'meta_callbacks',return_dict)
		return return_dict


	def set_meta_callback(self, from_, session_id, name, param):
		"""
		name: name of driver
		param: { meta-callback-name : meta-callback-object }
		"""
		print(datetime.datetime.now(),' - labware_harness.set_meta_callback:')
		print('\n\targs: ',locals(),'\n')
		if isinstance(param,dict):
			return_dict = self.driver_dict.get(name).set_meta_callback(list(param)[0],list(param.values())[0])
		else:
			return_dict = self.driver_dict.get(name).meta_callbacks()
		self._publisher.publish(from_,from_,session_id,'labware',name,'meta_callback',return_dict)
		return return_dict


	def add_callback(self, from_, session_id, name, param):
		"""
		name: name of driver
		param: { callback obj: [messages list] }
		"""
		print(datetime.datetime.now(),' - labware_harness.add_callback:')
		print('\n\targs: ',locals(),'\n')
		return_dict = self.driver_dict[name].add_callback(list(param)[0],list(param.values())[0])
		if from_ == "":
			self._publisher.publish('frontend',from_,session_id,'labware',name,'callbacks',return_dict)
		else:
			self._publisher.publish(from_,from_,session_id,'labware',name,'callbacks',return_dict)
		return return_dict


	def remove_callback(self, from_, session_id, name, param):
		"""
		name: name of driver
		param: name of callback to remove
		"""
		print(datetime.datetime.now(),' - labware_harness.remove_callback:')
		print('\n\targs: ',locals(),'\n')
		return_dict = self.driver_dict[name].remove_callback(param)
		if from_ == "":
			self._publisher.publish('frontend',from_,session_id,'labware',name,'callbacks',return_dict)
		else:
			self._publisher.publish(from_,from_,session_id,'labware',name,'callbacks',return_dict)
		return return_dict


	def flow(self, from_, session_id, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - labware_harness.flow:')
		print('\n\targs: ',locals(),'\n')
		return_dict = self.driver_dict.get(name).flow()
		if from_ == "":
			self._publisher.publish('frontend',from_,session_id,'labware',name,'flow',return_dict)
		else:
			self._publisher.publish(from_,from_,session_id,'labware',name,'flow',return_dict)
		return return_dict


	def clear_queue(self, from_, session_id, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - labware_harness.clear_queue:')
		print('\n\targs: ',locals(),'\n')
		return_dict = self.driver_dict.get(name).clear_queue()
		if from_ == "":
			self._publisher.publish('frontend',from_,session_id,'labware',name,'clear_queue',return_dict)
		else:
			self._publisher.publish(from_,from_,session_id,'labware',name,'clear_queue',return_dict)
		return return_dict


	def connect(self, from_, session_id, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - labware_harness.connect:')
		print('\n\targs: ',locals(),'\n')
		print('self.driver_dict: ',self.driver_dict)
		print('self.driver_dict[',name,']: ',self.driver_dict[name])
		self.driver_dict[name].connect(from_,session_id)


	#def disconnect(self, from_, session_id, name, param):
	#	"""
	#	name: name of driver
	#	param: n/a
	#	"""
	#	print(datetime.datetime.now(),' - labware_harness.disconnect:')
	#	print('\n\targs: ',locals(),'\n')
	#	self.driver_dict.get(name).disconnect(session_id)


	def close(self, from_, session_id, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - labware_harness.close:')
		print('\n\targs: ',locals(),'\n')
		self.driver_dict.get(name).close(from_,session_id)


	#def commands(self, from_, name, param):
	#	"""
	#	name: name of driver
	#	param: n/a
	#	"""
	#	print(datetime.datetime.now(),' - driver_harness.commands:')
	#	print('\tname: ',name)
	#	print('\tparam: ',param)
	#	self._publisher.publish(from_,from_,'driver',name,'commands',self.driver_dict.get(name).commands())


	def meta_commands(self, from_, session_id, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - labware_harness.meta_commands:')
		print('\n\targs: ',locals(),'\n')
		return_list = list(self.meta_dict)
		if from_ == "":
			self._publisher.publish('frontend',from_,session_id,'labware',name,'meta_commands',return_list)
		else:
			self._publisher.publish(from_,from_,session_id,'labware',name,'meta_commands',return_list)
		return return_list

	#def configs(self, from_, name, param):
	#	"""
	#	name: name of driver
	#	param: n/a
	#	"""
	#	print(datetime.datetime.now(),' - driver_harness.meta_commands:')
	#	print('\tname: ',name)
	#	print('\tparam: ',param)
	#	self._publisher.publish(from_,from_,'driver',name,'configs',self.driver_dict.get(name).configs())


	#def set_config(self, from_, name, param):
	#	"""
	#	name: name
	#	param: { config name : config value }
	#	"""
	#	print(datetime.datetime.now(),' - driver_harness.meta_commands:')
	#	print('\tname: ',str(name))
	#	print('\tparam: ',str(param))
	#	if isinstance(param,dict):
	#		self.driver_dict.get(name).set_config(list(param)[0],list(param.values)[0])
	#	self._publisher.publish(from_,from_,'driver',name,'configs',self.driver_dict.get(name).configs())


	def meta_command(self, from_, session_id, data):
		"""

		data should be in the form:

		{
			'name': name,
			'message': value
		}

		where name the name of the driver or None if n/a,

		and value is one of two forms:

		1. string

		2. {command:params}
			params --> {param1:value, ... , paramN:value}


		"""
		print(datetime.datetime.now(),' - labware_harness.meta_command:')
		print('\n\targs: ',locals(),'\n')
		if isinstance(data, dict):
			name = data['name']
			value = data['message']
			if name in self.driver_dict:
				if isinstance(value, dict):
					command = list(value)[0]
					params = value[command]
					try:
						self.meta_dict[command](from_,session_id,name,params)
					except:
						if from_ == "":
							self._publisher.publish('frontend',from_,session_id,'labware',name,'error',str(sys.exc_info()))
						else:
							self._publisher.publish(from_,from_,session_id,'labware',name,'error',str(sys.exc_info()))
						print(datetime.datetime.now(),' - meta_command error: ',str(sys.exc_info()))
				elif isinstance(value, str):
					command = value
					try:
						self.meta_dict[command](from_,session_id,name,None)
					except:
						if from_ == "":
							self._publisher.publish('frontend',from_,session_id,'labware',name,'error',str(sys.exc_info()))
						else:
							self._publisher.publish(from_,from_,session_id,'labware',name,'error',str(sys.exc_info()))
						print(datetime.datetime.now(),' - meta_command error: ',sys.exc_info())
			else:
				if isinstance(value, dict):
					command = list(value)[0]
					params = value[command]
					try:
						self.meta_dict[command](from_,session_id,None,params)
					except:
						if from_ == "":
							self._publisher.publish('frontend',from_,session_id,'labware',name,'error',sys.exc_info())
						else:
							self._publisher.publish(from_,from_,session_id,'labware',name,'error',sys.exc_info())
						print(datetime.datetime.now(),' - meta_command error, name not in drivers: ',sys.exc_info())
				elif isinstance(value, str):
					command = value
					try:
						self.meta_dict[command](from_,session_id,None,None)
					except:
						if from_ == "":
							self._publisher.publish('frontend',from_,session_id,'labware','None','error',sys.exc_info())
						else:
							self._publisher.publish(from_,from_,session_id,'labware','None','error',sys.exc_info())
						print(datetime.datetime.now(),' - meta_command error, name not in drivers: ',sys.exc_info())


	def send_command(self, from_, session_id, data):
		"""
		data:
		{
			'name': <name-of-driver>
			'message': <string> or { message : {param:values} } <--- the part the driver cares about
		}
		"""
		print(datetime.datetime.now(),'labware_harness.send_command:')
		print('\n\targs: ',locals(),'\n')
		if isinstance(data, dict):
			name = data['name']
			value = data['message']
			if name in self.driver_dict:
				try:
					self.driver_dict[name].send_command(session_id,value)
				except:
					if from_ == "":
						self._publisher.publish('frontend',from_,session_id,'labware',name,'error',sys.exc_info())
					else:
						self._publisher.publish(from_,from_,session_id,'labware',name,'error',sys.exc_info())
					print(datetime.datetime.now(),' - send_command error: '+sys.exc_info())
			else:
				if from_ == "":
					self._publisher.publish('frontend',from_,session_id,'labware','None','error',sys.exc_info())
				else:
					self._publisher.publish(from_,from_,session_id,'labware','None','error',sys.exc_info())
				print(datetime.datetime.now(),' - send_command_error, name not in drivers: '+sys.exc_info())


















