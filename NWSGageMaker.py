from datetime import datetime
from pydsstools.heclib.dss import HecDss
from pydsstools.core import TimeSeriesContainer,UNDEFINED

# Gage: BB100_01_August_2017
#      Last Modified Date: 19 May 2021
#      Last Modified Time: 22:52:56
#      Reference Height Units: Feet
#      Reference Height: 32
#      Gage Type: Precipitation
#      Precipitation Type: Incremental
#      Units: IN
#      Data Type: PER-CUM
#      Data Source Type: External DSS
#      Variant: Variant-0
#        Last Variant Modified Date: 8 October 2020
#        Last Variant Modified Time: 21:27:17
#        Default Variant: Yes
#        DSS File Name: Dickinson_Bayou_TimeSeries.dss
#        DSS Pathname: //BB100_01/PRECIP-INC/01Aug2017/15MIN/VIEUXHIST/
#        Start Time: 23 August 2017, 00:15
#        End Time: 5 September 2017, 00:00
#      End Variant: Variant-0

# use subbasinList to create new gages
dssFile = r"C:\Users\Myles.McManus\Documents\Working\GLO\Met\ClearCreek\A100_OCT2020_HMS48\DSS INPUT\201708_Harvey_NWS.dss"
inputDssFilename = r"DSS INPUT\201708_Harvey_NWS.dss"
fileA = HecDss.Open(dssFile)
DSSpathsA = fileA.getPathnameList('*') 

subbasinList = []

for pathA in DSSpathsA:
    pathSplit = pathA.split("/")
    subbasin = pathSplit[2]
    subbasinList.append(subbasin)

# Remove duplicates from list
subbasinList = list(set(subbasinList))
# print (subbasinList)
with open("NWSgageFileText.txt", 'w') as out_file:

    for gage in subbasinList:
        gageStr = f"""
Gage: {gage}_Harvey_NWS
    Last Modified Date: 19 May 2021
    Last Modified Time: 22:52:56
    Reference Height Units: Feet
    Reference Height: 32
    Gage Type: Precipitation
    Precipitation Type: Incremental
    Units: IN
    Data Type: PER-CUM
    Data Source Type: External DSS
    Variant: Variant-0
        Last Variant Modified Date: 28 September 2020
        Last Variant Modified Time: 20:28:37
        Default Variant: Yes
        DSS File Name: {inputDssFilename}
        DSS Pathname: //{gage}/PRECIP-INC/01AUG2017/15MIN/NWS/
        Start Time: 23 August 2017, 00:15
        End Time: 31 August 2017, 00:00
    End Variant: Variant-0
End:
        """
        out_file.write(gageStr)
