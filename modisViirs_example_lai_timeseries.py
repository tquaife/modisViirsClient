#!/usr/bin/python

from datetime import datetime
import matplotlib.pyplot as plt
from modisViirsClient import *

#start and end times
beg=datetime(year=2015,month=1,day=1)
end=datetime(year=2015,month=12,day=31)

#NEON Harvard tower
#lat=42.5369	
#lon=-72.1727

#Ozarks tower
lat=38.7441	
lon=-92.2000

scale=0.1
	
#list of OK QA fields
QAOK=np.arange(0,257,2)

#Terra-MODIS  
r=modViirRequest('MOD15A2H',band='all',latitude=lat,longitude=lon,start_date=beg, end_date=end) 
modlai=parseModViirJSON(r)
modlai.filterQA('Lai_500m','FparLai_QC',QAOK)

#Aqua-MODIS
r=modViirRequest('MYD15A2H',band='all',latitude=lat,longitude=lon,start_date=beg, end_date=end) 
mydlai=parseModViirJSON(r)
mydlai.filterQA('Lai_500m','FparLai_QC',QAOK)

#VIIRS-NPP
r=modViirRequest('VNP15A2H',band='all', latitude=lat,longitude=lon,start_date=beg, end_date=end) 
viirslai=parseModViirJSON(r)
viirslai.filterQA('Lai','FparLai_QC',QAOK)

#make a plot
plt.rcParams.update({'font.size': 14})
plt.plot(modlai.dates, scale*modlai.data['Lai_500m'][:,0,0],label='Terra')
plt.plot(mydlai.dates, scale*mydlai.data['Lai_500m'][:,0,0],label='Aqua')
plt.plot(viirslai.dates, scale*viirslai.data['Lai'][:,0,0],label='Viirs')
plt.ylabel('LAI')
plt.xlabel('Date')
plt.legend()

fig = plt.gcf()
fig.set_size_inches(15, 5)
fig.savefig('modisViirs_example_lai.png', dpi=100)

