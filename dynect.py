#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dynect Platform API Client

This module encapsulates Dynect Platform REST API calls.

Also it can be used as a command line tool

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
from pprint import pprint
from optparse import OptionParser

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


class DynTool(object):
    def __init__(self):
        parser = OptionParser(usage="\n%prog [options] ARGS\n%prog --version\n%prog --help", version="%prog v0.1")
        parser.add_option("-c", "--customer", dest="customer", help="Dynect customer name")
        parser.add_option("-u", "--username", dest="user", help="Dynect user name")
        parser.add_option("-p", "--password", dest="password", help="Dynect user password")
        parser.add_option("-z", "--zone", dest="zone", help="Dynect zone name (example: domain.tld)")
        parser.add_option("-n", "--node", dest="fqdn", help="Node name (example: node.domain.tld)")
        parser.add_option("-o", "--object", dest="object", help="Object type")
        parser.add_option("-w", "--command", dest="command", help="Command name")
        parser.add_option("-q", "--quiet", action="store_false", dest="verbose", default=True, help="don't print status messages to stdout")
        (options, args) = parser.parse_args()
        if not options.customer: parser.error("Customer name must be set")
        if not options.user: parser.error("User name must be set")
        if not options.password: parser.error("Password name must be set")
        if not options.zone: parser.error("Zone must be set")
        self.options = options
        self.object = options.object.lower()
        self.command = options.command.lower()
        self.arguments = args
    
    def set_connection(self, conn):
        self.conn = conn

    def list_a(self, zone, fqdn):
        result = list()
        qres = self.conn.read_rec_a(tool.options.zone, tool.options.fqdn)
        if qres["status"] != "success":
            raise Exception(res["msgs"][0]["INFO"])
        if len(qres["data"]) > 0:
            for rec in qres["data"]:
                rec_val = rec.split("/")[5]
                res = self.conn.read_rec_a(tool.options.zone, tool.options.fqdn, rec_val)
                result.append((rec_val, res["data"]["rdata"]["address"]))
        return result

    def add_a(self, zone, fqdn, val):
        qres = self.conn.create_rec_a(tool.options.zone, tool.options.fqdn, val)
        if qres["status"] != "success":
            raise Exception(res["msgs"][0]["INFO"])
        qres = self.conn.publish_zone(tool.options.zone)
        if qres["status"] != "success":
            raise Exception(res["msgs"][0]["INFO"])
        return True

    def del_a(self, zone, fqdn, val):
        rec_id = None
        for rec in self.list_a(tool.options.zone, tool.options.fqdn):
            if rec[1] == val:
                rec_id = rec[0]
        if not rec_id:
            raise DynectException("Can't find record %s"%val)
        qres = self.conn.delete_rec_a(tool.options.zone, tool.options.fqdn, rec_id)
        if qres["status"] != "success":
            raise DynectException(res["msgs"][0]["INFO"])
        qres = self.conn.publish_zone(tool.options.zone)
        if qres["status"] != "success":
            raise DynectException(res["msgs"][0]["INFO"])
        return True


if __name__ == "__main__":
    tool = DynTool()
    dyn = Dynect(tool.options.customer, tool.options.user, tool.options.password)
    tool.set_connection(dyn)
    try:
        dyn.keepalive()
        if (tool.object == "a") and (tool.command == "list"):
            res = tool.list_a(tool.options.zone, tool.options.fqdn)
            if len(res) > 0:
                for rec in res:
                    print("%s (record id: %s)"%(rec[1], rec[0]))
            else:
                print("No A records found")
        elif (tool.object == "a") and (tool.command == "add"):
            if tool.add_a(tool.options.zone, tool.options.fqdn, tool.arguments[0]) and tool.options.verbose:
                print("OK")
        elif (tool.object == "a") and (tool.command == "del"):
            if tool.del_a(tool.options.zone, tool.options.fqdn, tool.arguments[0]) and tool.options.verbose:
                print("OK")
        else:
            raise DynectException("Invalid arguments")
    except DynectException, e:
        print("ERROR: %s"%str(e))
