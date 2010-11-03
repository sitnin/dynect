# Dynect Platform API Client

This module encapsulates Dynect Platform REST API calls.

Also it can be used as a command line tool

## Currently implemented

*   Token authentication and logout
*   Keepalive
*   A Record listing, creation and deletion
*   Zone changes publishing

## Library usage example

    #!/usr/bin/env python
    from dynect import Dynect
    from pprint import pprint
    dyn = Dynect("customer", "username", "**************")
    dyn.keepalive()
    pprint(dyn.read_rec_a("domain.tld", "domain.tld"))

## Using as a command line tool

This command will print all A records for the domain.tld zone

    ./dynect.py -c CUSTOMER -u USERNAME -p PASSWORD -z domain.tld -n node.domain.tld -o a -w list

This will produce output like this:

    190.161.49.7 (record id: 6493308)
    62.148.64.1 (record id: 6495858)

### Possible object types and commands

#### Object type: A (-o a)

*   list -- list all A records for the node in zone
*   add A.B.C.D -- add A records for the node
*   del A.B.C.D -- delete A records from the node

## Contacts

My email is g.sitnin@wwpass.com

Details are coming...
