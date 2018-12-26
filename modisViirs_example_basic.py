#!/usr/bin/python

from modisViirsClient import *

#1) Request and print a list of all the products
#   available on the ORNL server
r=modViirRequest()
m=parseModViirJSON(r)
print '**** List of products on the ORNL Web Service ****'
for p in m.products:
    print p['product'], ' '*(12-len(p['product'])), p['description']
print ''


#2) List the bands in the VIIRS LAI product
product='VNP15A2H'
#product='MYD15A2H'
r=modViirRequest(product)
m=parseModViirJSON(r)
print '**** List of bands in %s ****'%product
for b in m.bands:
    print b['band']
print ''


#3) List the bands in the Aqua vegetation index product
r=modViirRequest('VNP15A2H', 'Lai', latitude=52., longitude=-2.)
m=parseModViirJSON(r)
print '**** List of dates in VNP15A2H/Lai is available ****'
for d in m.dates:
    print d['calendar_date'],
print '\n'





