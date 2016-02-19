#!/usr/bin/env python3

"""
TODO:
- nose testing someday
"""

import labware_driver
import sys
import datetime

class Harness(object):

	def __init__(self, publisher=None):
		"""
		"""
		print(datetime.datetime.now(),' - labware_harness.__init__:')
		print('\tpublisher: ',publisher)
		self._publisher = publisher
		self.driver_dict = {}
		self.meta_dict = {
			'drivers' : lambda from_,name,param: self.drivers(from_,name,param),
			'add_driver' : lambda from_,name,param: self.add_driver(from_,name,param),
			'remove_driver' : lambda form_,name,param: self.remove_driver(from_,name,param),
		#'meta_callbacks' : lambda from_,name, param: self.meta_callbacks(form_,name,param),
		#	'set_meta_callback' : lambda from_,name,param: self.set_meta_callback(from_,name,param),
			'add_callback' : lambda from_,name,param: self.add_callback(from_,name,param),
			'remove_callback' : lambda from_,name,param: self.remove_callback(from_,name,param),
			'flow' : lambda from_,name,param: self.flow(from_,name,param),
			'clear_queue' : lambda from_,name,param: self.clear_queue(from_,name,param),
		#	'connect' : lambda from_,name,param: self.connect(from_,name,param),
		#	'disconnect' : lambda from_,name,param: self.disconnect(from_,name,param),
		#	'commands' : lambda from_,name,param: self.commands(form_,name,param),
		#	'configs' : lambda from_,name,param: self.configs(from_,name,param),
		#	'set_config' : lambda from_,name,param: self.set_config(from_,name,param)
		}


	def set_publisher(self, publisher):
		"""
		"""
		print(datetime.datetime.now(),' - labware_harness.set_publisher:')
		print('\tpublisher: ',publisher)
		self._publisher = publisher


	def drivers(self, from_, name, param):
		"""
		name: n/a
		param: n/a
		"""
		print(datetime.datetime.now(),'- labware_harness.drivers:')
		print('\tfrom_: ',from_)
		print('\tname: ',name)
		print('\tparam: ',param)
		if name is None:
			name = 'None'
		if from_ == "":
			self._publisher.publish('frontend',from_,'labware',name,'drivers',list(self.driver_dict))
		else:
			self._publisher.publish(from_,from_,'labware',name,'drivers',list(self.driver_dict))
		return list(self.driver_dict)


	def add_driver(self, from_, name, param):
		"""
		name: name of driver to add_driver
		param: driver object
		"""
		print(datetime.datetime.now(),' - labware_harness.add_driver:')
		print('\tfrom_: ',from_)
		print('\tname: ',name)
		print('\tparam: ',param)
		self.driver_dict[name] = param
		if from_ == "":
			self._publisher.publish('frontend',from_,'labware',name,'drivers',list(self.driver_dict))
		else:
			self._publisher.publish(from_,from_,'labware',name,'drivers',list(self.driver_dict))
		return list(self.driver_dict)


	def remove_driver(self, from_, name, param):
		"""
		name: name of driver to be driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - labware_harness.remove_driver:')
		print('\tfrom_: ',from_)
		print('\tname: ',name)
		print('\tparam: ',param)
		del self.driver_dict[name]
		if from_ == "":
			self._publisher.publish('frontend',from_,'labware',name,'drivers',list(self.driver_dict))
		else:
			self._publisher.publish(from_,from_,'labware',name,'drivers',list(self.driver_dict))
		return list(self.driver_dict)


	def callbacks(self, from_, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - labware_harness.callbacks:')
		print('\tfrom_: ',from_)
		print('\tname: ',name)
		print('\tparam: ',param)
		if from_ == "":
			self._publisher.publish('frontend',from_,'labware',name,'callbacks',self.driver_dict[name].callbacks())
		else:
			self._publisher.publish(from_,from_,'labware',name,'callbacks',self.driver_dict[name].callbacks())
		
		return self.driver_dict[name].callbacks()


	#def meta_callbacks(self, from_, name, param):
	#	"""
	#	name: name of driver
	#	param: n/a
	#	"""
	#	print(datetime.datetime.now(),' - driver_harness.meta_callbacks:')
	#	print('\tfrom_: ',from_)
	#	print('\tname: ',name)
	#	print('\tparam: ',param)
	#	self._publisher.publish(from_,from_,'driver',name,'meta_callbacks',self.driver_dict[name].meta_callbacks())
	#	return self.driver_dict[name].meta_callbacks


	#def set_meta_callback(self, from_, name, param):
	#	"""
	#	name: name of driver
	#	param: { meta-callback-name : meta-callback-object }
	#	"""
	#	print(datetime.datetime.now(),' - driver_harness.set_meta_callback:')
	#	print('\tname: ',name)
	#	print('\tparam: ',param)
	#	if isinstance(param,dict):
	#		self.driver_dict.get(name).set_meta_callback(list(param)[0],list(param.values)[0])
	#	self._publisher.publish(from_,from_
	#		,'driver',name,'meta_callback',self.driver_dict.get(name).meta_callbacks())


	def add_callback(self, from_, name, param):
		"""
		name: name of driver
		param: { callback obj: [messages list] }
		"""
		print(datetime.datetime.now(),' - labware_harness.add_callback:')
		print('\tfrom_: ',from_)
		print('\tname: ',name)
		print('\tparam: ',param)
		self.driver_dict[name].add_callback(list(param)[0],list(param.values())[0])
		if from_ == "":
			self._publisher.publish('frontend',from_,'labware',name,'callbacks',self.driver_dict.get(name).callbacks())
		else:
			self._publisher.publish(from_,from_,'labware',name,'callbacks',self.driver_dict.get(name).callbacks())
		return self.driver_dict.get(name).callbacks()


	def remove_callback(self, from_, name, param):
		"""
		name: name of driver
		param: name of callback to remove
		"""
		print(datetime.datetime.now(),' - labware_harness.remove_callback:')
		print('\tfrom_: ',from_)
		print('\tname: ',name)
		print('\tparam: ',param)
		self.driver_dict[name].remove_callback(param)
		if from_ == "":
			self._publisher.publish('frontend',from_,'labware',name,'callbacks',self.driver_dict.get(name).callbacks())
		else:
			self._publisher.publish(from_,from_,'labware',name,'callbacks',self.driver_dict.get(name).callbacks())
		return self.driver_dict.get(name).callbacks()


	def flow(self, from_, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - labware_harness.flow:')
		print('\tfrom_: ',from_)
		print('\tname: ',name)
		print('\tparam: ',param)
		if from_ == "":
			self._publisher.publish(from_,from_,'labware',name,'flow',self.driver_dict.get(name).flow())
		else:
			self._publisher.publish(from_,from_,'labware',name,'flow',self.driver_dict.get(name).flow())
		return self.driver_dict.get(name).flow()


	def clear_queue(self, from_, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - labware_harness.clear_queue:')
		print('\tfrom_: ',from_)
		print('\tname: ',name)
		print('\tparam: ',param)
		self.driver_dict.get(name).clear_queue()
		self.flow(from_, name, None)


	#def connect(self, from_, name, param):
	#	"""
	#	name: name of driver
	#	param: n/a
	#	"""
	#	print(datetime.datetime.now(),' - driver_harness.connect:')
	#	print('\tname: ',name)
	#	print('\tparam: ',param)
	#	print('self.driver_dict: ',self.driver_dict)
	#	print('self.driver_dict[',name,']: ',self.driver_dict[name])
	#	self.driver_dict[name].connect()


	#def disconnect(self, from_, name, param):
	#	"""
	#	name: name of driver
	#	param: n/a
	#	"""
	#	print(datetime.datetime.now(),' - driver_harness.disconnect:')
	#	print('\tname: ',name)
	#	print('\tparam: ',param)
	#	self.driver_dict.get(name).disconnect()


	#def commands(self, from_, name, param):
	#	"""
	#	name: name of driver
	#	param: n/a
	#	"""
	#	print(datetime.datetime.now(),' - driver_harness.commands:')
	#	print('\tname: ',name)
	#	print('\tparam: ',param)
	#	self._publisher.publish(from_,from_,'driver',name,'commands',self.driver_dict.get(name).commands())


	def meta_commands(self, from_, name, param):
		"""
		name: name of driver
		param: n/a
		"""
		print(datetime.datetime.now(),' - labware_harness.meta_commands:')
		print('\tfrom_: ',from_)
		print('\tname: ',name)
		print('\tparam: ',param)
		if from_ == "":
			self._publisher.publish('frontend',from_,'labware',name,'meta_commands',copy.deepcopy(self.meta_dict))
		else:
			self._publisher.publish(from_,from_,'labware',name,'meta_commands',copy.deepcopy(self.meta_dict))
		return copy.deepcopy(self.meta_dict)

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


	def meta_command(self, from_, data):
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
		print('\tfrom_: ',from_)
		print('\tdata: ',data)
		if isinstance(data, dict):
			name = data['name']
			value = data['message']
			if name in self.driver_dict:
				if isinstance(value, dict):
					command = list(value)[0]
					params = value[command]
					try:
						self.meta_dict[command](from_,name,params)
					except:
						if from_ == "":
							self._publisher.publish('frontend',from_,'labware',name,'error',sys.exc_info())
						else:
							self._publisher.publish(from_,from_,'labware',name,'error',sys.exc_info())
						print(datetime.datetime.now(),' - meta_command error: ',sys.exc_info())
				elif isinstance(value, str):
					command = value
					try:
						self.meta_dict[command](from_,name,None)
					except:
						if from_ == "":
							self._publisher.publish('frontend',from_,'labware',name,'error',sys.exc_info())
						else:
							self._publisher.publish(from_,from_,'labware',name,'error',sys.exc_info())
						print(datetime.datetime.now(),' - meta_command error: ',sys.exc_info())
			else:
				if isinstance(value, dict):
					command = list(value)[0]
					params = value[command]
					try:
						self.meta_dict[command](from_,None, params)
					except:
						if from_ == "":
							self._publisher.publish('frontend',from_,'labware',name,'error',sys.exc_info())
						else:
							self._publisher.publish(from_,from_,'labware',name,'error',sys.exc_info())
						print(datetime.datetime.now(),' - meta_command error, name not in drivers: ',sys.exc_info())
				elif isinstance(value, str):
					command = value
					try:
						self.meta_dict[command](from_,None,None)
					except:
						if from_ == "":
							self._publisher.publish('frontend',from_,'labware','None','error',sys.exc_info())
						else:
							self._publisher.publish(from_,from_,'labware','None','error',sys.exc_info())
						print(datetime.datetime.now(),' - meta_command error, name not in drivers: ',sys.exc_info())


	def send_command(self, from_, data):
		"""
		data:
		{
			'name': <name-of-driver>
			'message': <string> or { message : {param:values} } <--- the part the driver cares about
		}
		"""
		print(datetime.datetime.now(),'labware_harness.send_command:')
		print('\tfrom: ',from_)
		print('\tdata: ',data)
		if isinstance(data, dict):
			name = data['name']
			value = data['message']
			if name in self.driver_dict:
				try:
					self.driver_dict[name].send_command(value)
				except:
					if from_ == "":
						self._publisher.publish('frontend',from_,'labware',name,'error',sys.exc_info())
					else:
						self._publisher.publish(from_,from_,'labware',name,'error',sys.exc_info())
					print(datetime.datetime.now(),' - send_command error: '+sys.exc_info())
			else:
				if from_ == "":
					self._publisher.publish('frontend',from_,'labware','None','error',sys.exc_info())
				else:
					self._publisher.publish(from_,from_,'labware','None','error',sys.exc_info())
				print(datetime.datetime.now(),' - send_command_error, name not in drivers: '+sys.exc_info())















