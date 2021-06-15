# import os
# import sys
# import inspect

# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
# pydssdir = str(parentdir)+"\\pydsstools-master\\pydsstools"
# sys.path.insert(0, pydssdir) 

from datetime import datetime
from pydsstools.heclib.dss import HecDss
from pydsstools.core import TimeSeriesContainer,UNDEFINED
import plotly
from plotly.graph_objs import Scatter, Layout
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Open file A & B to compare.

dssFilename = r"C:\py\compareDssData\ClearCreekHarveyNWSVieuxFlowCompare.dss"
dssFile = HecDss.Open(dssFilename)

# NOTE: Assuming b-parts match between the two files. ASsuming pathname strcture of both files.

NWS_structure =  '//Subbasin/Flow//15MIN/NWS/'
Vieux_structure =  '//Subbasin/Flow//15MIN/VIEUXHIST/'
fpartA_structure = NWS_structure.split("/")[6]
fpartB_structure = Vieux_structure.split("/")[6]
startDate = "23Aug2017 00:15:00"
endDate = "30Aug2017 24:00:00"

# for each b-part get C=PRECIP-INC
# get b-parts
DSSpaths = dssFile.getPathnameList('*') 
# DSSpathsA = fileA.getCatalogedPathnames("/*/*/PRECIP-INC/*/*/*/")
# DSSpathsA_accum = fileA.getPathnameList('C=PRECIP-CUM')
subbasinList = []
DSSpathsA_incList = []
DSSpathsA_accumList = []
DSSpathsB_incList = []
DSSpathsB_accumList = []
for dssPath in DSSpaths:
    pathSplit = dssPath.split("/")
    subbasin = pathSplit[2]
    cPart = pathSplit[3]
    ePart = pathSplit[5]
    fPart = pathSplit[6]
    subbasinList.append(subbasin)
    # Remove d-part
    noDpartPath = f"//{subbasin}/{cPart}//{ePart}/{fPart}/"
    # Populate Pathname Lists
    if fPart == fpartA_structure:
        if cPart == "PRECIP-INC":
            DSSpathsA_incList.append(noDpartPath)
        elif cPart == "PRECIP-CUM":
            DSSpathsA_accumList.append(noDpartPath)
    elif fPart == fpartB_structure:
        if cPart == "PRECIP-INC":
            DSSpathsB_incList.append(noDpartPath)
        elif cPart == "PRECIP-CUM":
            DSSpathsB_accumList.append(noDpartPath)
   

# sort the lists alphabetically
subbasinList = sorted(list(set(subbasinList)))
DSSpathsA_incList = sorted(list(set(DSSpathsA_incList)))
DSSpathsA_accumList = sorted(list(set(DSSpathsA_accumList)))
DSSpathsB_incList = sorted(list(set(DSSpathsB_incList)))
DSSpathsB_accumList = sorted(list(set(DSSpathsB_accumList)))

n = len(DSSpathsA_incList)
n_columns = 2
subPlotTitleList =  [ele for ele in subbasinList for i in range(n_columns)]

fig = make_subplots(  rows=n, 
                                    cols=n_columns, 
                                    vertical_spacing=.1/(n-1),
                                    subplot_titles=subPlotTitleList)


zipList = zip(DSSpathsA_incList, DSSpathsA_accumList, DSSpathsB_incList, DSSpathsB_accumList)
# limit paths for testing.
# zipList = list(zipList)[0:60]

for i, (pathA_inc, pathA_accum, pathB_inc, pathB_accum) in enumerate(zipList):
    tsA_inc = dssFile.read_ts(pathA_inc,window=(startDate,endDate),trim_missing=True)
    tsA_accum = dssFile.read_ts(pathA_accum,window=(startDate,endDate),trim_missing=True)
    tsB_inc = dssFile.read_ts(pathB_inc,window=(startDate,endDate),trim_missing=True)
    tsB_accum = dssFile.read_ts(pathB_accum,window=(startDate,endDate),trim_missing=True)

    dfA = pd.DataFrame()
    dfA['Times'] = tsA_inc.pytimes
    dfA['Values'] = tsA_inc.values
    dfA['Missing'] = tsA_inc.nodata
    dfA.Values = np.where(dfA.Missing == True, np.NaN, dfA.Values)

    dfA_accum = pd.DataFrame()
    dfA_accum['Times'] = tsA_accum.pytimes
    dfA_accum['Values'] = tsA_accum.values
    dfA_accum['Missing'] = tsA_accum.nodata
    dfA_accum.Values = np.where(dfA_accum.Missing == True, np.NaN, dfA_accum.Values)

    

    dfB = pd.DataFrame()
    dfB['Times'] = tsB_inc.pytimes
    dfB['Values'] = tsB_inc.values
    dfB['Missing'] = tsB_inc.nodata
    dfB.Values = np.where(dfB.Missing == True, np.NaN, dfB.Values)

    dfB_accum = pd.DataFrame()
    dfB_accum['Times'] = tsB_accum.pytimes
    dfB_accum['Values'] = tsB_accum.values
    dfB_accum['Missing'] = tsB_accum.nodata
    dfB_accum.Values = np.where(dfB_accum.Missing == True, np.NaN, dfB_accum.Values)

    # sumA = dfA['Values'].sum()
    # sumB = dfB['Values'].sum()

    # sumdiffAB = sumA - sumB

    fig.append_trace(go.Scatter(
        x=dfA.Times, 
        y=dfA.Values,
        name = subbasinList[i] + " NWS ",
    ), row=i+1, col=1)

    fig.append_trace(go.Scatter(
        x=dfA_accum.Times, 
        y=dfA_accum.Values,
        name = subbasinList[i] + " NWS ",
    ), row=i+1, col=2)

    fig.append_trace(go.Scatter(
        x=dfB.Times, 
        y=dfB.Values,
        name = subbasinList[i] + " Vieux ",
    ), row=i+1, col=1)

    fig.append_trace(go.Scatter(
        x=dfB_accum.Times, 
        y=dfB_accum.Values,
        name = subbasinList[i] + " Vieux ",
    ), row=i+1, col=2)

    # fig.layout.annotations[i+1].update(text=f"{subbasin} NWS - Vieux = {sumdiffAB}")
    # fig.add_annotation(
    #         x=dfA['Times'].iloc[-3], 
    #         y=dfA['Values'].max,
    #         text=f"NWS - Vieux = {sumdiffAB}",
    #         showarrow=False)


fig.update_layout(height=n*800, 
                             width=2460, 
                             title_text="NWS vs Vieux",
                             template= "plotly_dark",
                             hoverlabel=dict(font=dict(family='sans-serif', size=22),
                                                         namelength= -1)
                            )
fig.show()
fig.write_html("precipCompare.html")
# write difference of Precip Totals table per subbasin
