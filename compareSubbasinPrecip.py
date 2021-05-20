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

dssFile = r"C:\py\dssHarveyDickinsonBayouCompare\Harvey_Metvue_Hyet.dss"
fileA = HecDss.Open(dssFile)

dssFile = r"C:\py\dssHarveyDickinsonBayouCompare\Dickinson_Bayou_TimeSeries_Vieux.dss"
fileB = HecDss.Open(dssFile)

# NOTE: Assuming b-parts match between the two files. ASsuming pathname strcture of both files.

fileA_structure =  '//Subbasin/PRECIP-INC//1HOUR//'
fileB_structure =  '//Subbasin/PRECIP-INC//15MIN/VIEUXHIST/'
startDate = "22Aug2017 23:00:00"
endDate = "31Aug2017 23:00:00"
# for each b-part get C=PRECIP-INC
# get b-parts
DSSpathsA = fileA.getPathnameList('*') 
# DSSpathsA = fileA.getCatalogedPathnames("/*/*/PRECIP-INC/*/*/*/")
# DSSpathsA_accum = fileA.getPathnameList('C=PRECIP-CUM')
subbasinList = []
DSSpathsA_incList = []
DSSpathsA_accumList = []
for pathA in DSSpathsA:
    pathSplit = pathA.split("/")
    subbasin = pathSplit[2]
    cPart = pathSplit[3]
    subbasinList.append(subbasin)
    if cPart == "PRECIP-INC":
        DSSpathsA_incList.append(pathA)
    elif cPart == "PRECIP-CUM":
        DSSpathsA_accumList.append(pathA)

# sort the lists alphabetically
subbasinList = sorted(subbasinList)
DSSpathsA_incList = sorted(DSSpathsA_incList)
DSSpathsA_accumList = sorted(DSSpathsA_accumList)

n = len(DSSpathsA_incList)
n_columns = 2
subPlotTitleList =  [ele for ele in subbasinList for i in range(n_columns)]

fig = make_subplots(  rows=n, 
                                    cols=n_columns, 
                                    vertical_spacing=.1/(n-1),
                                    subplot_titles=subPlotTitleList)

# limit paths for testing.
# DSSpathsA = DSSpathsA[0:2]

for i, (pathA, pathA_accum) in enumerate(zip(DSSpathsA_incList, DSSpathsA_accumList)):
    tsA = fileA.read_ts(pathA,window=(startDate,endDate),trim_missing=True)
    tsA_accum = fileA.read_ts(pathA_accum,window=(startDate,endDate),trim_missing=True)
    pathSplit = pathA.split("/")
    subbasin = pathSplit[2]
    cPart = pathSplit[3]
    dPart = pathSplit[4]
    pathB = f'//{subbasin}/PRECIP-INC/{dPart}/15MIN/VIEUXHIST/'
    pathB_accum = f'//{subbasin}/PRECIP-CUM/{dPart}/15MIN/VIEUXHIST/'
    tsB = fileB.read_ts(pathB,window=(startDate,endDate),trim_missing=True)
    tsB_accum = fileB.read_ts(pathB_accum,window=(startDate,endDate),trim_missing=True)

    dfA = pd.DataFrame()
    dfA['Times'] = tsA.pytimes
    dfA['Values'] = tsA.values
    dfA['Missing'] = tsA.nodata
    dfA.Values = np.where(dfA.Missing == True, np.NaN, dfA.Values)

    dfA_accum = pd.DataFrame()
    dfA_accum['Times'] = tsA_accum.pytimes
    dfA_accum['Values'] = tsA_accum.values
    dfA_accum['Missing'] = tsA_accum.nodata
    dfA_accum.Values = np.where(dfA_accum.Missing == True, np.NaN, dfA_accum.Values)

    

    dfB = pd.DataFrame()
    dfB['Times'] = tsB.pytimes
    dfB['Values'] = tsB.values
    dfB['Missing'] = tsB.nodata
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
        name = subbasin + " NWS ",
    ), row=i+1, col=1)

    fig.append_trace(go.Scatter(
        x=dfA_accum.Times, 
        y=dfA_accum.Values,
        name = subbasin + " NWS ",
    ), row=i+1, col=2)

    fig.append_trace(go.Scatter(
        x=dfB.Times, 
        y=dfB.Values,
        name = subbasin + " Vieux ",
    ), row=i+1, col=1)

    fig.append_trace(go.Scatter(
        x=dfB_accum.Times, 
        y=dfB_accum.Values,
        name = subbasin + " Vieux ",
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
