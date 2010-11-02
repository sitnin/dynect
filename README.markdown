# Dynect Platform REST API Client

This module encapsulates Dynect Platform REST API calls.

## Currently implemented

*   Token authentication and logout
*   Keepalive
*   A Record listing, creation and deletion
*   Zone changes publishing

## Usage example

``#!/usr/bin/env python``
``from dynect import Dynect``
``from pprint import pprint``
``dyn = Dynect("customer", "username", "**************")``
``dyn.keepalive()``
``pprint(dyn.read_rec_a("domain.tld", "domain.tld"))``

## Contacts

My email is g.sitnin@wwpass.com

Details are coming...
