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

loop = asyncio.get_event_loop()




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
    outer = None

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

        print('BEGIN INIT...\n')

        # TRYING THE FOLLOWING IN INSTANTIATE OBJECTS vs here
        # INITIAL SETUP PUBLISHER, HARNESS, SUBSCRIBER
        print(datetime.datetime.now(),' - INITIAL SETUP - publisher, harness, subscriber ','* * '*10)
        publisher = Publisher(session_factory)
        labware_harness = Harness(publisher)
        subscriber = Subscriber(labware_harness,publisher)
        labware_harness.set_publisher(publisher)


        # INSTANTIATE DRIVERS:
        print(datetime.datetime.now(),' - INSTANTIATE DRIVERS - labbie_driver ','* * '*10)
        labbie_driver = LabwareDriver()


        # ADD DRIVERS TO HARNESS
        print(datetime.datetime.now(),' - ADD DRIVERS TO HARNESS ','* * '*10)   
        labware_harness.add_driver(publisher.id,'','labware',labbie_driver)
        print(labware_harness.drivers(publisher.id,'',None,None))

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
            publisher.publish('frontend',from_,session_id,'labware',name,dd_name,dd_value)
            

        def driver(name, from_, session_id, data_dict):
            """
            """
            print(datetime.datetime.now(),' - labware_client.driver')
            print('\n\targs: ',locals(),'\n')
            dd_name = list(data_dict)[0]
            dd_value = data_dict[dd_name]
            publisher.publish('driver',from_,session_id,name,dd_name,dd_value)


        def bootstrapper(name, from_, session_id, data_dict):
            """
            """
            print(datetime.datetime.now(),' - labware_client.bootstrapper')
            print('\n\targs: ',locals(),'\n')
            dd_name = list(data_dict)[0]
            dd_value = data_dict[dd_name]
            publisher.publish('bootstrapper','',session_id,name,dd_name,dd_value)


        def labware(name, from_, session_id, data_dict):
            """
            """
            print(datetime.datetime.now(),' - labware_client.labware')
            print('\n\targs: ',locals(),'\n')
            dd_name = list(data_dict)[0]
            dd_value = data_dict[dd_name]
            publisher.publish('labware','',session_id,name,dd_name,dd_value)



        def none(name, from_, session_id, data_dict):
            """
            """
            print(datetime.datetime.now(),' - labware_client.none_cb')
            print('\n\targs: ',locals(),'\n')
            dd_name = list(data_dict)[0]
            dd_value = data_dict[dd_name]
            if from_ != session_id:
                publisher.publish('frontend',from_,session_id,'labware',name,dd_name,dd_value)
                publisher.publish(from_,from_,session_id,'labware',name,dd_name,dd_value)
            else:
                # next line just for testing
                publisher.publish('frontend',from_,session_id,'labware',name,dd_name,dd_value)
                
        # ADD TO HARNESS BELOW
        labware_harness.add_callback('frontend','','labware', {frontend:['frontend']})
        labware_harness.add_callback('driver','','labware', {driver:['driver']})
        labware_harness.add_callback('bootstrapper','','labware', {bootstrapper:['bootstrapper']})
        labware_harness.add_callback('labware','','labware', {labware:['labware']})
        # none is for debugging
        labware_harness.add_callback('frontend','','labware', {none:['None']})


        # ADD METACALLBACKS VIA HARNESS:
        print(datetime.datetime.now(),' - DEFINE AND ADD META-CALLBACKS VIA HARNESS ','* * '*10)
        def on_connect(from_,session_id):
            print(datetime.datetime.now(),' - labware_client.on_connect')
            print('\n\targs: ',locals(),'\n')
            publisher.publish(from_,from_,session_id,'connect','labware','result','connected')

        def on_disconnect(from_,session_id):
            print(datetime.datetime.now(),' - labware_client.on_disconnect')
            print('\n\targs: ',locals(),'\n')
            publisher.publish(from_,from_,session_id,'connect','labware','result','disconnected')

        def on_empty_queue(from_,session_id):
            print(datetime.datetime.now(),' - labware_client.on_empty_queue')
            print('\n\targs: ',locals(),'\n')
            publisher.publish(from_,from_,session_id,'queue','labware','result','empty')

        labware_harness.set_meta_callback(publisher.id,'','labware',{'on_connect':on_connect})
        labware_harness.set_meta_callback(publisher.id,'','labware',{'on_disconnect':on_disconnect})
        labware_harness.set_meta_callback(publisher.id,'','labware',{'on_empty_queue':on_empty_queue})

        # CONNECT TO DRIVERS:
        #print('*\t*\t* connect to drivers\t*\t*\t*')
        #driver_harness.connect(publisher.id,'smoothie',None)

        print('\n END INIT...\n')

        make_connection()

    except KeyboardInterrupt:
        pass
    finally:
        loop.close()














