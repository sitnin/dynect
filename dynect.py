#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dynect Platform REST API Client

This module encapsulates Dynect Platform REST API calls.

Currently implemented:
    * Token authentication and logout
    * Keepalive
    * A Record listing, creation and deletion
    * Zone changes publishing

Usage example:

    #!/usr/bin/env python
    from dynect import Dynect
    from pprint import pprint
    dyn = Dynect("customer", "username", "**************")
    dyn.keepalive()
    pprint(dyn.read_rec_a("domain.tld", "domain.tld"))


Details are coming...
"""

__author__ = "Gregory Sitnin <g.sitnin@wwpass.com>"
__copyright__ = "Copyright WWPASS Corporation, 2010"
__version__ = "0.1"

import httplib
import urllib
import json
import pprint

DynectException = Exception

class Dynect(object):
    def __init__(self, customer, user, password, autologin=True):
        self.customer = customer
        self.user = user
        self.password = password
        self.conn = None
        self.token = None
        if autologin:
            self.login()

    def __del__(self):
        if self.token:
            self.logout()
        self._close()

    def _connect(self):
        self.conn = httplib.HTTPSConnection("api2.dynect.net")

    def _close(self):
        self.conn.close()

    def _api_call(self, method, resource, params={}):
        if not self.conn:
            self._connect()
        try:
            headers = {
                "Content-Type": "application/json",
            }
            if self.token:
                headers["Auth-Token"] = self.token
            self.conn.request(method, "/REST/%s/"%resource, json.dumps(params), headers)
            response = self.conn.getresponse()
            data = response.read()
            if response.status != 200:
                raise Exception("%d %s - %s"%(response.status, response.reason, data))
            self.conn.close()
            res = (True, json.loads(data))
        except Exception, e:
            res = (False, str(e))
        return res

    def login(self):
        params = {
            "customer_name": self.customer,
            "user_name": self.user,
            "password": self.password,
        }
        result, data = self._api_call("POST", "Session", params)
        if not result:
            raise DynectException(data)
        self.token = data["data"]["token"]

    def keepalive(self):
        result, data = self._api_call("PUT", "Session")
        if not result:
            raise DynectException(data)

    def logout(self, autoclose=True):
        result, data = self._api_call("DELETE", "Session")
        if not result:
            raise DynectException(data)
        self.token = None
        if autoclose:
            self._close()

    def publish_zone(self, zone):
        resource = "Zone/%s"%zone
        result, data = self._api_call("PUT", resource, {"publish": True})
        if not result:
            raise DynectException(data)
        else:
            return data

    def create_rec_a(self, zone, fqdn, address, ttl=0):
        resource = "ARecord/%s/%s"%(zone, fqdn)
        params = {
            "rdata": {
                "address": address
            },
            "ttl": str(ttl)
        }
        result, data = self._api_call("POST", resource, params)
        if not result:
            raise DynectException(data)
        else:
            return data
        
    def read_rec_a(self, zone, fqdn, record=None):
        resource = "ARecord/%s/%s"%(zone, fqdn)
        if record:
            resource += "/%s/"%record
        result, data = self._api_call("GET", resource)
        if not result:
            raise DynectException(data)
        else:
            return data

    def delete_rec_a(self, zone, fqdn, record):
        resource = "ARecord/%s/%s/%s"%(zone, fqdn, record)
        result, data = self._api_call("DELETE", resource)
        if not result:
            raise DynectException(data)
        else:
            return data
