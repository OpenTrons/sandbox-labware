#!/usr/bin/env python3

import json, collections
import sys
import datetime
import labware_publisher

driver = None

class Subscriber():
    def __init__(self, harness=None, publisher=None):
        print(datetime.datetime.now(),' - labware_subscriber.__init__:')
        print('\targs:',locals())
        self.harness = harness
        self.publisher = publisher

        self.in_dispatcher = {
            'command': lambda from_,session_id,data: self.harness.send_command(from_,session_id,data),
            'meta': lambda from_,session_id,data: self.harness.meta_command(from_,session_id,data)
        }

    def set_harness(self, harness):
        print(datetime.datetime.now(),' - labware_subscriber.set_harness:')
        print('\targs:',locals())
        self.harness = harness


    def dispatch_message(self, message):
        print(datetime.datetime.now(),' - labware_subscriber.dispatch_message:')
        print('\targs:',locals())
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





