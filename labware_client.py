#!/usr/bin/env python3


import asyncio
import time
import json
import uuid
import datetime
import sys

from labware_subscriber import Subscriber
from labware_publisher import Publisher
from labware_harness import Harness
from labware_driver import LabwareDriver

from autobahn.asyncio import wamp, websocket
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner 

crossbar_connected = False

def make_connection():
    if loop.is_running():
        loop.stop()
    coro = loop.create_connection(transport_factory, '0.0.0.0', 8080)
    transport, protocoler = loop.run_until_complete(coro)
    #protocoler.set_outer(self)
    if not loop.is_running():
        loop.run_forever()


class WampComponent(wamp.ApplicationSession):
    """WAMP application session for OTOne (Overrides protocol.ApplicationSession - WAMP endpoint session)
    """

    def set_outer(self, outer_):
        outer = outer_

    def onConnect(self):
        """Callback fired when the transport this session will run over has been established.
        """
        self.join(u"ot_realm")


    @asyncio.coroutine
    def onJoin(self, details):
        """Callback fired when WAMP session has been established.

        May return a Deferred/Future.

        Starts instatiation of robot objects by calling :meth:`otone_client.instantiate_objects`.
        """
        print(datetime.datetime.now(),' - driver_client : WampComponent.onJoin:')
        print('\n\targs: ',locals(),'\n')
        if not self.factory._myAppSession:
            self.factory._myAppSession = self
    
        

        def handshake(client_data):
            """
            """
        #    #if debug == True:
            print(datetime.datetime.now(),' - labware_client : WampComponent.handshake:')
        #    #if outer is not None:
        #    #outer.
            publisher.handshake(client_data)

        yield from self.subscribe(handshake, 'com.opentrons.labware_handshake')
        yield from self.subscribe(subscriber.dispatch_message, 'com.opentrons.labware')


    def onLeave(self, details):
        """Callback fired when WAMP session has been closed.
        :param details: Close information.
        """
        print('driver_client : WampComponent.onLeave:')
        print('\n\targs: ',locals(),'\n')
        if self.factory._myAppSession == self:
            self.factory._myAppSession = None
        try:
            self.disconnect()
        except:
            raise
        

    def onDisconnect(self):
        """Callback fired when underlying transport has been closed.
        """
        print(datetime.datetime.now(),' - labware_client : WampComponent.onDisconnect:')
        asyncio.get_event_loop().stop()
        crossbar_connected = False


class LabwareClient():

    def __init__(self):
        #__init__ VARIABLES FROM HARNESS
        print(datetime.datetime.now(),' - LabwareClient.__init__:')
        print('\n\targs: ',locals(),'\n')
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
            'connect' : lambda from_,session_id,name,param: self.driver_connect(from_,session_id,name,param),
            'close' : lambda from_,session_id,name,param: self.driver_close(from_,session_id,name,param),
            'meta_commands' : lambda from_,session_id,name,param: self.meta_commands(from_,session_id,name,param)
        }

        #__init__ VARIALBES FROM SUBSCRIBER
        self.in_dispatcher = {
            'command': lambda from_,session_id,data: self.send_command(from_,session_id,data),
            'meta': lambda from_,session_id,data: self.meta_command(from_,session_id,data)
        }

        #__init__ VARIALBES FROM PUBLISHER
        self.topic = {
            'frontend' : 'com.opentrons.frontend',
            'driver' : 'com.opentrons.driver',
            'labware' : 'com.opentrons.labware',
            'bootstrapper' : 'com.opentrons.bootstrapper'
        }

        self.clients = {
            # uuid : 'com.opentrons.[uuid]'
        }
        self.max_clients = 4

        self.id = str(uuid.uuid4())

        self.session_factory = wamp.ApplicationSessionFactory()
        self.session_factory.session = WampComponent

        self.loop = asyncio.get_event_loop()


    # FUNCTIONS FROM SUBSCRIBER
    def dispatch_message(self, message):
        print(datetime.datetime.now(),' - LabwareClient.dispatch_message:')
        print('\n\targs: ',locals(),'\n')
        try:
            dictum = collections.OrderedDict(json.loads(message.strip(), object_pairs_hook=collections.OrderedDict))
            if 'type' in dictum and 'from' in dictum and 'sessionID' in dictum and 'data' in dictum:
                if dictum['type'] in self.in_dispatcher:
                    #if self.publisher.client_check(dictum['from']):
                        #opportunity to filter, not actually used
                    self.in_dispatcher[dictum['type']](dictum['from'],dictum['sessionID'],dictum['data'])
                    #else:
                    #    self.in_dispatcher[doctum['type']](dictum['from'],dictum['data'])
                else:
                    print(datetime.datetime.now(),' - {error:malformed message, type not in in_dispatcher}\n\r',sys.exc_info())
                    print('type: ',dictum['type'])
                    return '{error,malformed message, type not in in_dispatcher}'
            else:
                print(datetime.datetime.now(),' - {error:subscriber.dispatch_message type or data error}\n\r',sys.exc_info())
                return '{error:subscriber.dispatch_message type or data error}'
        except:
            print(datetime.datetime.now(),' - {error:general subscriber.dispatch_message error}\n\r',sys.exc_info())
            return '{error:general subscriber.dispatch_message error}'


    # FUNCTIONS FROM PUBLISHER
    def handshake(self, data):
        print(datetime.datetime.now(),' - LabwareClient.handshake:')
        print('\n\targs: ',locals(),'\n')
    
        data_dict = json.loads(data)
        if isinstance(data_dict, dict):
            if 'from' in data:
                print('* data has "from"')
                client_id = data_dict['from']
                print('client_id: ',client_id)
                if client_id in self.clients:
                    print('* from is a client')
                    if 'data' in data_dict:
                        if 'message' in data_dict['data']:
                            if 'extend' in data_dict['data']['message']:
                                print('handshake called again on client ',client_id,'. We could have done something here to repopulate data')
                                self.publish( client_id , client_id , client_id ,'handshake','labware','result','already_connected')
                            if 'shake' in data_dict['data']['message']:
                                self.publish_client_ids(client_id,client_id)
                else:
                    print('* from is NOT a client')
                    if len(self.clients) > self.max_clients:
                        self.publish( 'frontend', '' , 'handshake' , '' , 'labware' , 'result' , 'fail' )
                    else:
                        if client_id != "":
                            self.clients[client_id] = 'com.opentrons.'+client_id
                            self.publish( 'frontend' , client_id , client_id , 'handshake', 'labware', 'result','success')
                        else:
                            self.gen_client_id()
            else:
                print('* data does NOT have "from"')
                self.gen_client_id()
    
            if 'get_ids' in data_dict:
                publish_client_ids('','')
        else:
            self.gen_client_id()


    def gen_client_id(self):
        ret_id = ''
        if len(self.clients) > self.max_clients:
            self.publish( 'frontend', '' , '' , 'handshake' , 'labware' , 'result' , 'fail' )
        else:
            client_id = str(uuid.uuid4())
            self.clients[client_id] = 'com.opentrons.'+client_id
            self.publish( 'frontend' , client_id , client_id , 'handshake' , 'labware' , 'result' , 'success' )
            ret_id = client_id
        return ret_id


    def client_check(self, id_):
        if id_ in self.clients:
            return True
        else:
            return False


    def publish_client_ids(self, id_, session_id):
        if id_ in self.clients:
            self.publish( id_ , id_ , session_id, 'handshake' , 'labware' , 'ids' , list(self.clients) )
        else:
            self.publish( 'frontend' , '' , session_id, 'handshake' , 'labware' , 'ids' , list(self.clients) )
        return list(self.clients)


    def set_caller(self, session):
        """
        """
        print(datetime.datetime.now(),' - LabwareClient.set_caller:')
        print('\n\targs: ',locals(),'\n')
        self.caller = session


    def publish(self,topic,to,session_id,type_,name,message,param):
        """
        """
        print(datetime.datetime.now(),' - LabwareClient.publish:')
        print('\n\targs: ',locals(),'\n')
        if self.caller is not None and topic is not None and type_ is not None:
            if name is None:
                name = 'None'
            if message is None:
                message = ''
            if param is None:
                param = ''
            if self.caller is not None:
                if self.caller._myAppSession is not None:
                    msg = {'type':type_,'to':to,'sessionID':session_id,'from':self.id,'data':{'name':name,'message':{message:param}}}
                    try:
                        if topic in self.topic:
                            print('TOPIC: ',self.topic)
                            print(datetime.datetime.now(),'url topic: ',self.topic.get(topic))
                            self.caller._myAppSession.publish(self.topic.get(topic),json.dumps(msg))
                        else:
                            print('TO:',to)
                            url_topic = 'com.opentrons.'+to
                            print(datetime.datetime.now(),'url topic: ',url_topic)
                            self.caller._myAppSession.publish(url_topic,json.dumps(msg))
                        #elif topic in self.clients:
                        #    print('CLIENTS: ',self.clients)
                        #    print(datetime.datetime.now(),'url topic: ',self.clients.get(topic))
                        #    self.caller._myAppSession.publish(self.clients.get(topic),json.dumps(msg))


                    except:
                        print(datetime.datetime.now(),' - publisher.py - publish - error:\n\r',sys.exc_info())
            else:
                print(datetime.datetime.now(),' - publisher.py - publish - error: caller._myAppSession is None')
        else:
            print(datetime.datetime.now(),' - publisher.py - publish - error: calller, topic, or type_ is None')


    # FUNCTIONS FROM HARNESS
    def drivers(self, from_, session_id, name, param):
        """
        name: n/a
        param: n/a
        """
        print(datetime.datetime.now(),'- LabwareClient.drivers:')
        print('\n\targs: ',locals(),'\n')
        return_list = list(self.driver_dict)
        if name is None:
            name = 'None'
        if from_ == "":
            self.publish('frontend',from_,session_id,'labware',name,'drivers',return_list)
        else:
            self.publish(from_,from_,session_id,'labware',name,'drivers',return_list)
        return return_list


    def add_driver(self, from_, session_id, name, param):
        """
        name: name of driver to add_driver
        param: driver object
        """
        print(datetime.datetime.now(),' - LabwareClient.add_driver:')
        print('\n\targs: ',locals(),'\n')
        self.driver_dict[name] = param
        return_list = list(self.driver_dict)
        if from_ == "":
            self.publish('frontend',from_,session_id,'labware',name,'drivers',return_list)
        else:
            self.publish(from_,from_,session_id,'labware',name,'drivers',return_list)
        return return_list


    def remove_driver(self, from_, session_id, name, param):
        """
        name: name of driver to be driver
        param: n/a
        """
        print(datetime.datetime.now(),' - LabwareClient.remove_driver:')
        print('\n\targs: ',locals(),'\n')
        del self.driver_dict[name]
        return_list = list(self.driver_dict)
        if from_ == "":
            self.publish('frontend',from_,session_id,'labware',name,'drivers',return_list)
        else:
            self.publish(from_,from_,session_id,'labware',name,'drivers',return_list)
        return return_list


    def callbacks(self, from_, session_id, name, param):
        """
        name: name of driver
        param: n/a
        """
        print(datetime.datetime.now(),' - LabwareClient.callbacks:')
        print('\n\targs: ',locals(),'\n')
        return_dict = self.driver_dict[name].callbacks()
        if from_ == "":
            self.publish('frontend',from_,session_id,'labware',name,'callbacks',return_dict)
        else:
            self.publish(from_,from_,session_id,'labware',name,'callbacks',return_dict)
        return return_dict


    def meta_callbacks(self, from_, session_id, name, param):
        """
        name: name of driver
        param: n/a
        """
        print(datetime.datetime.now(),' - labware_harness.meta_callbacks:')
        print('\n\targs: ',locals(),'\n')
        return_dict = self.driver_dict[name].meta_callbacks()
        self.publish(from_,from_,session_id,'labware',name,'meta_callbacks',return_dict)
        return return_dict


    def set_meta_callback(self, from_, session_id, name, param):
        """
        name: name of driver
        param: { meta-callback-name : meta-callback-object }
        """
        print(datetime.datetime.now(),' - LabwareClient.set_meta_callback:')
        print('\n\targs: ',locals(),'\n')
        if isinstance(param,dict):
            return_dict = self.driver_dict.get(name).set_meta_callback(list(param)[0],list(param.values())[0])
        else:
            return_dict = self.driver_dict.get(name).meta_callbacks()
        self.publish(from_,from_,session_id,'labware',name,'meta_callback',return_dict)
        return return_dict


    def add_callback(self, from_, session_id, name, param):
        """
        name: name of driver
        param: { callback obj: [messages list] }
        """
        print(datetime.datetime.now(),' - LabwareClient.add_callback:')
        print('\n\targs: ',locals(),'\n')
        return_dict = self.driver_dict[name].add_callback(list(param)[0],list(param.values())[0])
        if from_ == "":
            self.publish('frontend',from_,session_id,'labware',name,'callbacks',return_dict)
        else:
            self.publish(from_,from_,session_id,'labware',name,'callbacks',return_dict)
        return return_dict


    def remove_callback(self, from_, session_id, name, param):
        """
        name: name of driver
        param: name of callback to remove
        """
        print(datetime.datetime.now(),' - LabwareClient.remove_callback:')
        print('\n\targs: ',locals(),'\n')
        return_dict = self.driver_dict[name].remove_callback(param)
        if from_ == "":
            self.publish('frontend',from_,session_id,'labware',name,'callbacks',return_dict)
        else:
            self.publish(from_,from_,session_id,'labware',name,'callbacks',return_dict)
        return return_dict


    def flow(self, from_, session_id, name, param):
        """
        name: name of driver
        param: n/a
        """
        print(datetime.datetime.now(),' - LabwareClient.flow:')
        print('\n\targs: ',locals(),'\n')
        return_dict = self.driver_dict.get(name).flow()
        if from_ == "":
            self.publish('frontend',from_,session_id,'labware',name,'flow',return_dict)
        else:
            self.publish(from_,from_,session_id,'labware',name,'flow',return_dict)
        return return_dict


    def clear_queue(self, from_, session_id, name, param):
        """
        name: name of driver
        param: n/a
        """
        print(datetime.datetime.now(),' - LabwareClient.clear_queue:')
        print('\n\targs: ',locals(),'\n')
        return_dict = self.driver_dict.get(name).clear_queue()
        if from_ == "":
            self.publish('frontend',from_,session_id,'labware',name,'clear_queue',return_dict)
        else:
            self.publish(from_,from_,session_id,'labware',name,'clear_queue',return_dict)
        return return_dict


    def driver_connect(self, from_, session_id, name, param):
        """
        name: name of driver
        param: n/a
        """
        print(datetime.datetime.now(),' - LabwareClient.driver_connect:')
        print('\n\targs: ',locals(),'\n')
        print('self.driver_dict: ',self.driver_dict)
        print('self.driver_dict[',name,']: ',self.driver_dict[name])
        self.driver_dict[name].connect(from_,session_id)


    #def disconnect(self, from_, session_id, name, param):
    #   """
    #   name: name of driver
    #   param: n/a
    #   """
    #   print(datetime.datetime.now(),' - labware_harness.disconnect:')
    #   print('\n\targs: ',locals(),'\n')
    #   self.driver_dict.get(name).disconnect(session_id)


    def driver_close(self, from_, session_id, name, param):
        """
        name: name of driver
        param: n/a
        """
        print(datetime.datetime.now(),' - LabwareClient.driver_close:')
        print('\n\targs: ',locals(),'\n')
        self.driver_dict.get(name).close(from_,session_id)


    #def commands(self, from_, name, param):
    #   """
    #   name: name of driver
    #   param: n/a
    #   """
    #   print(datetime.datetime.now(),' - driver_harness.commands:')
    #   print('\tname: ',name)
    #   print('\tparam: ',param)
    #   self._publisher.publish(from_,from_,'driver',name,'commands',self.driver_dict.get(name).commands())


    def meta_commands(self, from_, session_id, name, param):
        """
        name: name of driver
        param: n/a
        """
        print(datetime.datetime.now(),' - LabwareClient.meta_commands:')
        print('\n\targs: ',locals(),'\n')
        return_list = list(self.meta_dict)
        if from_ == "":
            self.publish('frontend',from_,session_id,'labware',name,'meta_commands',return_list)
        else:
            self.publish(from_,from_,session_id,'labware',name,'meta_commands',return_list)
        return return_list


    #def configs(self, from_, name, param):
    #   """
    #   name: name of driver
    #   param: n/a
    #   """
    #   print(datetime.datetime.now(),' - driver_harness.meta_commands:')
    #   print('\tname: ',name)
    #   print('\tparam: ',param)
    #   self._publisher.publish(from_,from_,'driver',name,'configs',self.driver_dict.get(name).configs())


    #def set_config(self, from_, name, param):
    #   """
    #   name: name
    #   param: { config name : config value }
    #   """
    #   print(datetime.datetime.now(),' - driver_harness.meta_commands:')
    #   print('\tname: ',str(name))
    #   print('\tparam: ',str(param))
    #   if isinstance(param,dict):
    #       self.driver_dict.get(name).set_config(list(param)[0],list(param.values)[0])
    #   self._publisher.publish(from_,from_,'driver',name,'configs',self.driver_dict.get(name).configs())


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
        print(datetime.datetime.now(),' - LabwareClient.meta_command:')
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
                            self.publish('frontend',from_,session_id,'labware',name,'error',str(sys.exc_info()))
                        else:
                            self.publish(from_,from_,session_id,'labware',name,'error',str(sys.exc_info()))
                        print(datetime.datetime.now(),' - meta_command error: ',str(sys.exc_info()))
                elif isinstance(value, str):
                    command = value
                    try:
                        self.meta_dict[command](from_,session_id,name,None)
                    except:
                        if from_ == "":
                            self.publish('frontend',from_,session_id,'labware',name,'error',str(sys.exc_info()))
                        else:
                            self.publish(from_,from_,session_id,'labware',name,'error',str(sys.exc_info()))
                        print(datetime.datetime.now(),' - meta_command error: ',sys.exc_info())
            else:
                if isinstance(value, dict):
                    command = list(value)[0]
                    params = value[command]
                    try:
                        self.meta_dict[command](from_,session_id,None,params)
                    except:
                        if from_ == "":
                            self.publish('frontend',from_,session_id,'labware',name,'error',sys.exc_info())
                        else:
                            self.publish(from_,from_,session_id,'labware',name,'error',sys.exc_info())
                        print(datetime.datetime.now(),' - meta_command error, name not in drivers: ',sys.exc_info())
                elif isinstance(value, str):
                    command = value
                    try:
                        self.meta_dict[command](from_,session_id,None,None)
                    except:
                        if from_ == "":
                            self.publish('frontend',from_,session_id,'labware','None','error',sys.exc_info())
                        else:
                            self.publish(from_,from_,session_id,'labware','None','error',sys.exc_info())
                        print(datetime.datetime.now(),' - meta_command error, name not in drivers: ',sys.exc_info())


    def send_command(self, from_, session_id, data):
        """
        data:
        {
            'name': <name-of-driver>
            'message': <string> or { message : {param:values} } <--- the part the driver cares about
        }
        """
        print(datetime.datetime.now(),'LabwareClient.send_command:')
        print('\n\targs: ',locals(),'\n')
        if isinstance(data, dict):
            name = data['name']
            value = data['message']
            if name in self.driver_dict:
                try:
                    self.driver_dict[name].send_command(session_id,value)
                except:
                    if from_ == "":
                        self.publish('frontend',from_,session_id,'labware',name,'error',sys.exc_info())
                    else:
                        self.publish(from_,from_,session_id,'labware',name,'error',sys.exc_info())
                    print(datetime.datetime.now(),' - send_command error: '+sys.exc_info())
            else:
                if from_ == "":
                    self.publish('frontend',from_,session_id,'labware','None','error',sys.exc_info())
                else:
                    self.publish(from_,from_,session_id,'labware','None','error',sys.exc_info())
                print(datetime.datetime.now(),' - send_command_error, name not in drivers: '+sys.exc_info())


    def _make_connection(self, url_domain='0.0.0.0', url_port=8080):
        if self.loop.is_running():
            self.loop.stop()
        coro = self.loop.create_connection(transport_factory, url_domain, url_port)
        self.transport, self.protocoler = self.loop.run_until_complete(coro)
        #protocoler.set_outer(self)
        if not self.loop.is_running():
            self.loop.run_forever()


    def connect(self, url_protocol='ws', url_domain='0.0.0.0', url_port=8080, url_path='ws', keep_trying=True, period=5, debug=False, debug_wamp=False):
        if self.transport_factory is None:
            self.transport_factory = websocket.WampWebSocketClientFactory(self.session)

            url = url_protocol+"://"+url_domain+':'+str(url_port)+'/'+url_path

            try:
                self._make_connection()
                while (keep_trying):
                    while (self.crossbar_connected == False):
                        try:
                            print('\nLabware attempting crossbar connection\n')
                            self._make_connection()
                        except KeyboardInterrupt:
                            crossbar_connected = True
                        except:
                            print('crossbar connection attempt error:\n',sys.exc_info())
                            pass
                        finally:
                            print('\nCrossbar connection failed, sleeping for 5 seconds\n')
                            time.sleep(5)
            except:
                print('crossbar connection attempt error:\n',sys.exc_info())
                raise


    def disconnect(self):
        self.transport.close()
        self.transport_factory = None



    
    



if __name__ == '__main__':

    try:
        session_factory = wamp.ApplicationSessionFactory()
        session_factory.session = WampComponent
        session_factory._myAppSession = None

        url = "ws://0.0.0.0:8080/ws"
        transport_factory = websocket.WampWebSocketClientFactory(session_factory,
                                                                url=url,
                                                                debug=False,
                                                                debug_wamp=False)
        loop = asyncio.get_event_loop()

        print('\nBEGIN INIT...\n')

        # TRYING THE FOLLOWING IN INSTANTIATE OBJECTS vs here
        # INITIAL SETUP PUBLISHER, HARNESS, SUBSCRIBER
        print(datetime.datetime.now(),' - INITIAL SETUP - publisher, harness, subscriber ','* * '*10)
        labware_client = LabwareClient()


        # INSTANTIATE DRIVERS:
        print(datetime.datetime.now(),' - INSTANTIATE DRIVERS - labbie_driver ','* * '*10)
        labbie_driver = LabwareDriver()


        # ADD DRIVERS TO HARNESS
        print(datetime.datetime.now(),' - ADD DRIVERS TO HARNESS ','* * '*10)   
        labware_client.add_driver(publisher.id,'','labware',labbie_driver)
        print(labware_client.drivers(publisher.id,'',None,None))

        # DEFINE CALLBACKS:
        #
        #   data_dict format:
        #
        #
        #
        #
        #
        print(datetime.datetime.now(),' - DEFINE CALLBACKS AND ADD VIA HARNESS ','* * '*10)
        def frontend(name, from_, session_id, data_dict):
            """
            """
            print(datetime.datetime.now(),' - labware_client.frontend')
            print('\n\targs: ',locals(),'\n')
            dd_name = list(data_dict)[0]
            dd_value = data_dict[dd_name]
            labware_client.publish('frontend',from_,session_id,'labware',name,dd_name,dd_value)
            

        def driver(name, from_, session_id, data_dict):
            """
            """
            print(datetime.datetime.now(),' - labware_client.driver')
            print('\n\targs: ',locals(),'\n')
            dd_name = list(data_dict)[0]
            dd_value = data_dict[dd_name]
            labware_client.publish('driver',from_,session_id,name,dd_name,dd_value)


        def bootstrapper(name, from_, session_id, data_dict):
            """
            """
            print(datetime.datetime.now(),' - labware_client.bootstrapper')
            print('\n\targs: ',locals(),'\n')
            dd_name = list(data_dict)[0]
            dd_value = data_dict[dd_name]
            labware_client.publish('bootstrapper','',session_id,name,dd_name,dd_value)


        def labware(name, from_, session_id, data_dict):
            """
            """
            print(datetime.datetime.now(),' - labware_client.labware')
            print('\n\targs: ',locals(),'\n')
            dd_name = list(data_dict)[0]
            dd_value = data_dict[dd_name]
            labware_client.publish('labware','',session_id,name,dd_name,dd_value)



        def none(name, from_, session_id, data_dict):
            """
            """
            print(datetime.datetime.now(),' - labware_client.none_cb')
            print('\n\targs: ',locals(),'\n')
            dd_name = list(data_dict)[0]
            dd_value = data_dict[dd_name]
            if from_ != session_id:
                labware_client.publish('frontend',from_,session_id,'labware',name,dd_name,dd_value)
                labware_client.publish(from_,from_,session_id,'labware',name,dd_name,dd_value)
            else:
                # next line just for testing
                labware_client.publish('frontend',from_,session_id,'labware',name,dd_name,dd_value)
                
        # ADD TO HARNESS BELOW
        labware_client.add_callback('frontend','','labware', {frontend:['frontend']})
        labware_client.add_callback('driver','','labware', {driver:['driver']})
        labware_client.add_callback('bootstrapper','','labware', {bootstrapper:['bootstrapper']})
        labware_client.add_callback('labware','','labware', {labware:['labware']})
        # none is for debugging
        labware_client.add_callback('frontend','','labware', {none:['None']})


        # ADD METACALLBACKS VIA HARNESS:
        print(datetime.datetime.now(),' - DEFINE AND ADD META-CALLBACKS VIA HARNESS ','* * '*10)
        def on_connect(from_,session_id):
            print(datetime.datetime.now(),' - labware_client.on_connect')
            print('\n\targs: ',locals(),'\n')
            labware_client.publish(from_,from_,session_id,'connect','labware','result','connected')

        def on_disconnect(from_,session_id):
            print(datetime.datetime.now(),' - labware_client.on_disconnect')
            print('\n\targs: ',locals(),'\n')
            labware_client.publish(from_,from_,session_id,'connect','labware','result','disconnected')

        def on_empty_queue(from_,session_id):
            print(datetime.datetime.now(),' - labware_client.on_empty_queue')
            print('\n\targs: ',locals(),'\n')
            labware_client.publish(from_,from_,session_id,'queue','labware','result','empty')

        labware_client.set_meta_callback(labware_client.id,'','labware',{'on_connect':on_connect})
        labware_client.set_meta_callback(labware_client.id,'','labware',{'on_disconnect':on_disconnect})
        labware_client.set_meta_callback(labware_client.id,'','labware',{'on_empty_queue':on_empty_queue})

        # CONNECT TO DRIVERS:
        #print('*\t*\t* connect to drivers\t*\t*\t*')
        #driver_harness.connect(publisher.id,'smoothie',None)

        print('\nEND INIT...\n')

        while (True):
            while (crossbar_connected == False):
                try:
                    print('\nLabware attempting crossbar connection\n')
                    make_connection()
                except KeyboardInterrupt:
                    crossbar_connected = True
                except:
                    print('crossbar connection attempt error:\n',sys.exc_info())
                    pass
                finally:
                    print('\nCrossbar connection failed, sleeping for 5 seconds\n')
                    time.sleep(5)

    except KeyboardInterrupt:
        pass
    finally:
        loop.close()














