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
from hydroeval import evaluator, nse

# Open file A & B to compare.

dssFile = r"C:\Users\Myles.McManus\Documents\Working\GLO\Met\ClearCreek\A100_OCT2020_HMS48\DSS OUTPUT\HarveyJustFlow.dss"
fileA = HecDss.Open(dssFile)

# NOTE: Assuming b-parts match between the two files. Assuming pathname strcture of both files.

NWS_structure =  '//Subbasin/Flow//15MIN/RUN:201708_HARVEY_NWS/'
Vieux_structure =  '//Subbasin/Flow//15MIN/RUN:201708_HARVEY/'
fpartA_structure = NWS_structure.split("/")[6]
fpartB_structure = Vieux_structure.split("/")[6]
startDate = "23Aug2017 00:15:00"
endDate = "01Sep2017 24:00:00"

# for each b-part get C=PRECIP-INC
# get b-parts
DSSpathsA = fileA.getPathnameList('*') 
# DSSpathsA = fileA.getCatalogedPathnames("/*/*/PRECIP-INC/*/*/*/")
# DSSpathsA_accum = fileA.getPathnameList('C=PRECIP-CUM')
subbasinList = []
DSSpathsA_List = []
DSSpathsB_List = []

# limit paths for testing.
# DSSpathsA = DSSpathsA[0:6]

for pathA in DSSpathsA:
    pathSplit = pathA.split("/")
    subbasin = pathSplit[2]
    cPart = pathSplit[3]
    ePart = pathSplit[5]
    fPart = pathSplit[6]
    subbasinList.append(subbasin)
    # Remove d-part
    noDpartPath = f"//{subbasin}/{cPart}//{ePart}/{fPart}/"
    if fPart == fpartA_structure:
        DSSpathsA_List.append(noDpartPath)
    elif fPart == fpartB_structure:
        DSSpathsB_List.append(noDpartPath)

# sort the lists alphabetically, and remove dups
subbasinList = sorted(list(set(subbasinList)))
DSSpathsA_List = sorted(list(set(DSSpathsA_List)))
DSSpathsB_List = sorted(list(set(DSSpathsB_List)))

# Plotly Subplot setup
n = len(DSSpathsA_List)
n_columns = 1
# subPlotTitleList =  [ele for ele in subbasinList for i in range(n_columns)]
subPlotTitleList  = subbasinList

fig = make_subplots(  rows=n, 
                                    cols=n_columns, 
                                    vertical_spacing=.1/(n-1),
                                    subplot_titles=subPlotTitleList)


nseList = []
for i, (pathA, pathB) in enumerate(zip(DSSpathsA_List, DSSpathsB_List)):
    tsA = fileA.read_ts(pathA,window=(startDate,endDate),trim_missing=True)
    tsB = fileA.read_ts(pathB,window=(startDate,endDate),trim_missing=True)
    pathSplit = pathA.split("/")
    subbasin = pathSplit[2]
    cPart = pathSplit[3]
    dPart = pathSplit[4]

    dfA = pd.DataFrame()
    dfA['Times'] = tsA.pytimes
    dfA['Values'] = tsA.values
    dfA['Missing'] = tsA.nodata
    dfA.Values = np.where(dfA.Missing == True, np.NaN, dfA.Values)    

    dfB = pd.DataFrame()
    dfB['Times'] = tsB.pytimes
    dfB['Values'] = tsB.values
    dfB['Missing'] = tsB.nodata
    dfB.Values = np.where(dfB.Missing == True, np.NaN, dfB.Values)

    # sumA = dfA['Values'].sum()
    # sumB = dfB['Values'].sum()

    # sumdiffAB = sumA - sumB

    my_nse = evaluator(nse, dfA['Values'], dfB['Values'], axis=1)
    nseList.append(round(my_nse[0],2))

    fig.append_trace(go.Scatter(
        x=dfA.Times, 
        y=dfA.Values,
        name = subbasin + " NWS ",
    ), row=i+1, col=1)

    fig.append_trace(go.Scatter(
        x=dfB.Times, 
        y=dfB.Values,
        name = subbasin + " Vieux ",
    ), row=i+1, col=1)

    fig.add_annotation(text="NSE = "+ str(round(my_nse[0],2)),
                  xref="x domain", yref="y domain",
                  x=0.9, y=0.9, showarrow=False,
                  row=i+1, col=1,
                  font=dict(family='sans-serif', size=22))



    # fig.layout.annotations[i+1].update(text=f"{subbasin} NWS - Vieux = {sumdiffAB}")
    # fig.add_annotation(
    #         x=dfA['Times'].iloc[-3], 
    #         y=dfA['Values'].max,
    #         text=f"NWS - Vieux = {sumdiffAB}",
    #         showarrow=False)

nse_max = max(nseList)
nse_min = min(nseList)
from statistics import mean
nse_avg= round(mean(nseList),2)

fig.update_layout(height=n*800, 
                             width=2540, 
                             title_text=f"NWS vs Vieux HMS Subbasin Flow, NSE Range [{nse_min}, {nse_max}], NSE avg = {nse_avg}",
                             template= "plotly_dark",
                             hoverlabel=dict(font=dict(family='sans-serif', size=22),
                                                         namelength= -1)
                            )
# fig.show()

fig.write_html("flowCompare.html")
# write difference of Precip Totals table per subbasin
