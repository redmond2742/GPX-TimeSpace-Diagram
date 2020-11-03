# gpxpy libraries
import gpxpy
import gpxpy.gpx
import gpxpy.geo as geo
import pandas as pd
# graph libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.offsetbox import AnchoredText
#dateformatter
import datetime
import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


#######   How to Use  #######
#     1. Fill in initial variable values below for street, time of day, direction, and if it's a reverse route or not, and run number. File name needs to correspond to this also.
#        for example: MainSt-AM-NB-1.gpx in the data folder.
#     2. Add lat, long of the center of each of the intersections the GPX track uses. Add in the order driven through for one direction
#     3. Run at terminal; $python3 ./TSplotter.py  (where TSplotter is the file name of this file)


#Initial variables - ***Requires Manual Input***
street_name = 'Red Hill Road'                #label street name
time_period = 'PM'                #label time period (ie. AM, MD, PM)
direction = 'WB'                  #label direction (WB, EB, NB, SB) of street (for charts and gpx files)
route_reverse = True           #set False for same direction intersection coordinates are listed and True for opposite direction of intersection coordinates.
run_num = 1                     #set to number of run for GPX file


#load file and parse for one direction
gpx_file = open('data/'+street_name+'-'+time_period+'-'+direction+'-'+str(run_num)+'.gpx','r')
gpx = gpxpy.parse(gpx_file)


#setup variables and dataframes needed for one direction
i = 0
df1 = pd.DataFrame(columns=['lat', 'long', 'elev', 'time'])
df2 = pd.DataFrame(columns=['dist'])
df3 = pd.DataFrame(columns=['cumlDist'])
df3.loc[0]=0.00000
timedf = pd.DataFrame(columns=['cumlTime'])
gpxPlot = pd.DataFrame()
gpxMaster = pd.DataFrame()


#Intersection Locations Setup - ***Requires manual input***

intersectionMaster = pd.DataFrame(columns=['intDist'])
intersectionPlot = pd.DataFrame(columns=['t'])
intersectionDF = pd.DataFrame(columns=['ilat', 'ilong'])


#Add intersection coordinates in order of driving them.
#Lat,Long should be location of the center of the intersection
#For Example:
#   intersectionDF.loc[0] = [33.677863] + [-117.876008]
#   intersectionDF.loc[1] = [33.679869] + [-117.873993]
#   intersectionDF.loc[2] = [33.689353] + [-117.864506]

intersectionDF.loc[0] = [33.660985] + [-117.887634]  # Mesa Dr
intersectionDF.loc[1] = [33.666640] + [-117.882035]  # Bristol St
intersectionDF.loc[2] = [33.672243] + [-117.878458]  # Kalmus Dr
intersectionDF.loc[3] = [33.677863] + [-117.876008]  # Baker St
intersectionDF.loc[4] = [33.679869] + [-117.873993]  # Paularino Ave
intersectionDF.loc[5] = [33.689353] + [-117.864506]  # Main Street
intersectionDF.loc[6] = [33.692519] + [-117.858395]  # Sky Park
intersectionDF.loc[7] = [33.693921] + [-117.854891]  # MacArthur Blvd
intersectionDF.loc[8] = [33.697283] + [-117.851564]  # McGaw Ave
intersectionDF.loc[9] = [33.700067] + [-117.848703]  # Alton Pkwy
intersectionDF.loc[10] = [33.702797] + [-117.846000] # Deere Ave
intersectionDF.loc[11] = [33.705567] + [-117.843222] # Barranca Pkwy
intersectionDF.loc[12] = [33.708434] + [-117.840488] # Carnegie Ave



#intersection Plot is for drawing a line from t=0 to t=max
intersectionPlot.loc[0] = 0.0
intersectionPlot.loc[1] = 0.0
for x in range(0,len(intersectionDF.index)):
        intersectionPlot['int'+str(x)]= None

#second conversion
def convert(seconds):
    """Convert input of seconds into travel times into MM:SS"""
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%02d:%02d" % ( minutes, seconds)


#Load GPX into dataframe for one direction
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            df1.loc[i] = [point.latitude] + [point.longitude] + [point.elevation] + [point.time]
            i=i+1


#distance in feet using haversine formula .haversine_distance(latitude_1: float, longitude_1: float, latitude_2: float, longitude_2: float)
for x in range(1,len(df1.index)):
    df2.loc[x-1] = [(geo.haversine_distance(df1.iloc[x-1,0], df1.iloc[x-1,1], df1.iloc[x,0], df1.iloc[x,1]))*3.28084]
    df2.loc[x]   = df2.loc[x-1]


#calculating cumulative distance of gpx track
for x in range(1,len(df2.index)):
    df3.loc[x] = [(df2.dist.iat[x-1]) + df3.cumlDist.iat[x-1]]


#calculate elapsed time from first GPX point fo each row in timedf as a second
for x in range (0,len(df1.index)):
    timedf.loc[x] = (df1.iloc[x,3]-df1.iloc[0,3])/np.timedelta64(1, 's')


#Combine dataframes
gpxPlot = timedf.join(df3)
gpxMaster = df1.join(gpxPlot)



# Intersection Distance Calculations
# Calculates the cumulative distance for each of the intersections

def int_cumldist_v2(dfint,dfgpx,intMstr):
    """intersection locations in dfint are compared to closest gpx point in dfgpx and saved as intMstr cumlative distance location"""
    for x in range(0,len(dfint.index)):
        dfgpx['int'+str(x)]= None

    for y in range(0,len(dfint.index)):
        for z in range(0,len(dfgpx.index)):
            dfgpx.iloc[z,y+6] = geo.haversine_distance(dfgpx.lat.iat[z],dfgpx.long.iat[z],dfint.ilat.iat[y],dfint.ilong.iat[y])*3.28084

    for m in range(0,len(dfint.index)):
         val = int(dfgpx[dfgpx.iloc[:,m+6] == dfgpx.iloc[:,m+6].min()].index[0])
         intMstr.loc[m] = dfgpx.iloc[val,5]

    return intMstr,dfgpx

def clip_bounds(clipdist,dfint,dfgpx,rev):
    """clip gpx track to a clipdistance based on first and last intersection location. rev auto set from top variables"""
    clipdistance = clipdist

    if(rev == False):
        lowerbound = dfint.intDist.iat[0] - clipdistance
        upperbound = dfint.intDist.iat[-1] + clipdistance
    else:
         #reverse direction
        lowerbound = dfint.intDist.iat[-1] - clipdistance
        upperbound = dfint.intDist.iat[0] + clipdistance


    dfgpx = dfgpx[dfgpx.cumlDist > lowerbound]
    dfgpx = dfgpx[dfgpx.cumlDist < upperbound]

    dfgpx = dfgpx.reset_index(drop=True)

    return(dfint,dfgpx)


int_cumldist_v2(intersectionDF,gpxMaster,intersectionMaster)

clip_bounds(1000,intersectionMaster,gpxMaster,route_reverse)


for x in range(0,len(intersectionMaster.index)):
    intersectionMaster.intDist.iat[x] = intersectionMaster.intDist.iat[x] - gpxMaster.cumlDist.iat[0]

intersectionPlot.iloc[0,0] = (gpxMaster.cumlTime.iat[0])

for x in range(0,len(intersectionMaster.index)):
    intersectionPlot.iloc[0,x+1] = intersectionMaster.intDist.iat[x]
    intersectionPlot.iloc[1,x+1] = intersectionMaster.intDist.iat[x]


j=len(gpxMaster.index)-1
intersectionPlot.iloc[1,0] = (gpxMaster.cumlTime.iat[j])


def calibrate_cumldist(dfgpx,rev):
    """recalibrate cumulative distance based on clipped distances"""
    dfgpx['zcumlDist']= None

    for x in range(0,len(dfgpx.index)):
        if rev == False:
            dfgpx.zcumlDist.iat[x] = (dfgpx.cumlDist.iat[x] - dfgpx.cumlDist.iat[0])
            #df_in.zcumlTime.iat[x] = [df_in.iloc[x,3] - df_in.iloc[0,3]]
        else:
            dfgpx.zcumlDist.iat[x] = (dfgpx.cumlDist.iat[x] - dfgpx.cumlDist.iat[0])
            #df_in.zcumlTime.iat[x] = [df_in.iloc[x,3] - df_in.iloc[0,3]]

    return dfgpx

calibrate_cumldist(gpxMaster,route_reverse)


def travel_time(dfint,dfgpx,rev):
    """calculate travel time of gpx route based on intersection locations. Calculates from center of intersection."""

    m=len(dfint.index)

    int_first_index = int(dfgpx[dfgpx.iloc[:,6] == dfgpx.iloc[:,6].min()].index[0])
    int_last_index = int(dfgpx[dfgpx.iloc[:,m+5] == dfgpx.iloc[:,m+5].min()].index[0])

    if rev == False:
        TT = dfgpx.iloc[int_last_index,4] - dfgpx.iloc[int_first_index,4]
    else:
        TT = dfgpx.iloc[int_first_index,4] - dfgpx.iloc[int_last_index,4]

    return convert(TT)

tt = travel_time(intersectionDF,gpxMaster,route_reverse)


# Plot Statements

font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 16,
        }

fig, ax = plt.subplots()
plt.style.use([u'seaborn-white'])
plt.plot('cumlTime', 'zcumlDist', data=gpxMaster)

# multiple intersections as horizontal lines on plot
for column in intersectionPlot.drop('t', axis=1):
    plt.plot(intersectionPlot['t'], intersectionPlot[column], marker='', color='grey', linewidth=1, alpha=0.4)


plt.title(street_name+' - '+direction+' - '+time_period+' - Run '+str(run_num), fontdict=font)
plt.xlabel('time (s)', fontdict=font)
plt.ylabel('Distance (ft)', fontdict=font)


anchored_text = AnchoredText('TT: '+str(tt), loc=2)
ax.add_artist(anchored_text)

plt.subplots_adjust(left=0.15)
plt.show()
