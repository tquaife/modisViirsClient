#!/usr/bin/python
"""modisViirsClient

Provides an interface to the ORNL Web Service for
MODIS and VIIRS-NPP data and a basic class for handling
small amounts of satellite data
    
Copyright (C) 2018 Tristan Quaife

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

Tristan Quaife
t.l.quaife@reading.ac.uk
"""



import sys
from datetime import datetime, date

import json
from StringIO import StringIO

import pycurl
import numpy as np


def __error( msg ):
    raise Exception, msg
        
def latLonErr( ):
    __error( 'Latitude and longitude must both be specified' )
    
def serverDataErr( ):    
    __error( 'Server not returning data (possibly busy)' )


def mkIntDate( s ):
    """
    Convert the webserver formatted dates
    to an integer format by stripping the
    leading char and casting
    """
    n=s.__len__( )
    d=int( s[-(n-1):n] )
    return d


def readURL(url, header=['Accept: application/json']):
    """Use pyCurl to read the contents of a 
    URL into a StringIO buffer.
    """
    buff = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buff)
    c.setopt(c.HTTPHEADER, header)
    c.perform()
    http_status=c.getinfo(pycurl.HTTP_CODE)
    c.close()    
    return buff.getvalue(), http_status


def getJSONData(url):
    """Download JSON data and raise an exception
    if the returned status is not inthe list of 
    OK status values
    """
    status_OK=[200]
    body, status=readURL(url)
    if status not in status_OK:
        msg=json.dumps(json.loads(body),indent=4)
        raise Exception, "Sever returned status code: %d\n%s"%(status,msg)
    return json.loads(body)


def getCSVData(url):
    body=readURL(url,header=['Accept: text/csv'] )
    return body

    
def formatDateForRequest(date):
    """Return a string with the date formatted as the
    ORNL server expects it.
    
    date -- Python datetime.dat object
    """
    y=date.year
    d=date.timetuple().tm_yday
    return "A%d%03d"%(y,d)
        
        
        
class modViirRequest:
    
    def __init__(self, product=None, band=None, latitude=None, longitude=None, start_date=None, end_date=None, km_above_below=0, km_left_right=0):
        """Base class for forming requests
        for the ORNL MODIS/VIIRS webservice
        """
        
        self.product=product
        self.band=band
        self.latitude=latitude
        self.longitude=longitude
        self.start_date=start_date
        self.end_date=end_date
        self.km_above_below=km_above_below
        self.km_left_right=km_left_right
        
        self.chunk_size=10
        self.api_version='v1'
        self.got_full_request_params=False
        self.base_url='https://modis.ornl.gov/rst/api/'
        self.url=self.base_url+self.api_version+'/'

        
    def get_url(self,start_date,end_date):   
        """Generate a single request URL based 
        on which arguments have been specified 
        when the class was created.
        
        Note that starte_date and end_date
        
        """
        request_url=self.url
        request_url+=self.product+'/subset'
        request_url+='?latitude='+str(self.latitude)
        request_url+='&longitude='+str(self.longitude)
        if self.band != 'all':
            request_url+='&band='+str(self.band)
        request_url+='&startDate='+formatDateForRequest(start_date)
        request_url+='&endDate='+formatDateForRequest(end_date)
        request_url+='&kmAboveBelow='+str(self.km_above_below)
        request_url+='&kmLeftRight='+str(self.km_left_right)
        
        return request_url
        
        
        
    def generate_request(self):
        """Generate a request URL based on which
        arguments have been specified when the 
        class was created.
        
        Split request strings into chunks based on
        dates so as to circumnavigate the 10 date
        restriction
        """
        
        request_url=self.url

        #product list
        if self.product==None:
            request_url+='products'
            return [request_url]
                      
        #band list                
        if self.band==None:
            request_url+=self.product+'/bands'
            return [request_url]

        #check coordinates exist
        if self.latitude==None or self.longitude==None:
            latLonErr( )

        #date list
        if self.start_date==None or self.end_date==None:
            request_url+=self.product+'/dates'
            request_url+='?latitude='+str(self.latitude)
            request_url+='&longitude='+str(self.longitude)
            return [request_url]
        
        #set flag so we know we have all the parameters:
        self.got_full_request_params=True

        #get date list:
        request_url=self.url         
        request_url+=self.product+'/dates'
        request_url+='?latitude='+str(self.latitude)
        request_url+='&longitude='+str(self.longitude)
        json_data=getJSONData(request_url)
        
        #break the dates down into chunks
        #of ten days inbetween those requested
        start_list=[]
        end_list=[]
        ndates=0
        for date_str in json_data["dates"]:
            date=datetime.strptime(date_str["calendar_date"], "%Y-%m-%d")
            if date>=self.start_date and date<=self.end_date:
                ndates+=1
                if ndates==1:
                    start_list.append(date)
                if ndates == 10:
                    end_list.append(date)
                    ndates=0
                last_date=date
        if len(start_list) != len(end_list):
            end_list.append(last_date)
            
        #generate the list of requests:
        request_list=[]
        for (start_date,end_date) in zip(start_list,end_list):
            request_list.append(self.get_url(start_date,end_date))
            
        return request_list



#class modViirRequestSite(modViirRequest):
#    def __init__(self,site_id=None):
#        self.site_id=site_id
#        modViirRequest.__init__(self)

#    def generate_request(self):   
#        """Generate a request URL based on which
#        arguments have been specified when the 
#        class was created.
#        """
#        request_url=self.url

#        if self.site_id==None:
#            request_url+='sites'
#            return request_url


class modViirData:
    def __init__(self):
        """A basic class for handling small amounts of satellite
        data such as that from the ORNL web service"""
        
        self.attribute_list=[]
        
        #"data" is a dictionary that should be indexed
        #by (e.g.) the name of the band.
        self.data={}

    def filterQA( self, databand, qaband, QAOK, fill=np.nan ):
        """replace any data that doesn't pass QA checks
        with a fill value
        
        
        databand  -- (string) the dictionary index for the data 
                     band to be filtered
        qaband    -- (string) the dictionary index for the data 
                     band containing QA/QC data
        QAOK      -- a numpy array of QA/QC values that the user
                     to allow through the filtering
        fill      -- (any) the value to put in place of filtered
                     data.                    
        """
        
        if np.size( self.data[databand] ) != np.size( self.data[qaband] ):
            raise Exception, 'data and QA are different sizes'
                
        t=np.shape( self.data[databand] )[0]
        r=np.shape( self.data[databand] )[1]
        c=np.shape( self.data[databand] )[2]
        
        for i in xrange( t ):
            for j in xrange( r ):
                for k in xrange( c ):
                    if np.sum( QAOK == self.data[qaband][i,j,k] ) == 0:
                        self.data[databand][i,j,k] = fill

 
      

def parseModViirJSON(request):
    """
    A factory function that returns an instance of the 
    modViirData class populated with data retrieved 
    from the ORNL Web Service.
    
    request -- instance of the modViirRequest class
    """

    #list of items to treat separately
    reserved=['subset']

    m=modViirData()
    json_data=[]

    #send requests to the server
    req_list=request.generate_request()
    for (i,req) in enumerate(req_list):
        json_data.append(getJSONData(req))

    
    #set up modis data class based on first
    #request in the list
    for item in json_data[0]:
        if item not in reserved:
            m.attribute_list.append(item)
            setattr(m,item,json_data[0][item])


    #if the data contains a subset (i.e. actual
    #data of some description) process it into
    #numpy arrays for onward processing by the user
    if 'subset' in json_data[0]:
               
        m.dates=[]
        m.modis_dates=[]
        for (k,jsn) in enumerate(json_data):            
            for (n,item) in enumerate(jsn['subset']):
                date=datetime.strptime(item['calendar_date'],'%Y-%m-%d')
                if date not in m.dates:
                    m.dates.append(date)
                    m.modis_dates.append(item['modis_date'])
               
        n_dates=len(m.dates)           
        ndate_counter=0
        
        for (k,jsn) in enumerate(json_data):            
            for (n,item) in enumerate(jsn['subset']):
                
                #work out which band we're dealing with
                band=item['band']
                if band not in m.data:
                    m.data[band]=np.zeros((n_dates,m.nrows,m.ncols))
                                
                #pack the data into a numpy array
                pos=m.modis_dates.index(item['modis_date'])
                for i in xrange(m.nrows):
                    for j in xrange(m.ncols):                        
                        m.data[band][pos,i,j]=item['data'][i*m.ncols+j]
     
    return m  





if __name__=="__main__":

    #print a list of products that are currently on the server:
    r=modViirRequest()
    m=parseModViirJSON(r)
    for p in m.products:
        print p['product'], ' '*(12-len(p['product'])), p['description']


 
