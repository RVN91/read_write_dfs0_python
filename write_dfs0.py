# -*- coding: utf-8 -*-
"""
Reads and writes dfs0 files.

Be advised, DHI is retarded...

@author: Rasmus Vest Nielsen
"""

import datetime
import sys, os
import numpy as np
import matplotlib.dates as dates
import inspect

# Check system architecture
import struct
if struct.calcsize("P") * 8 == 64: # .NET compatibility
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "\clr64")
else:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "\clr")
import clr
import System

def write_dfs0(gauge_time, gauge_int, out_file, script_folder):
    """
    Writes data to dfs0 file
    
    Input:
        gauge_time: Array or list with time stamps
        gauge_int: Array or list with data
        out_file: File name for the dfs0 file
        script_folder: Folder containing this shit
        
    Output:
        None
    """
    gauge_time = gauge_time.tolist() # Convert arrays to lists
    gauge_int = gauge_int.tolist()   # Convert arrays to lists

    # Load MIKE SDK .NET
    clr.AddReference(script_folder + 
                     r"\dhi_sdk\MatlabDfsUtil.2016.dll")
    clr.AddReference(script_folder + 
                     r"\dhi_sdk\DHI.Generic.MikeZero.DFS.dll")
    clr.AddReference(script_folder + 
                     r"\dhi_sdk\DHI.Generic.MikeZero.EUM.dll")
    
    import MatlabDfsUtil 
    import DHI.Generic.MikeZero
    import DHI.Generic.MikeZero.DFS
    import DHI.Generic.MikeZero.DFS.dfs0
    import DHI.Generic.MikeZero.DFS.dfs123
    
    factory = DHI.Generic.MikeZero.DFS.DfsFactory()
    builder = DHI.Generic.MikeZero.DFS.DfsBuilder.Create('Rasmus is really cool',
                                                         'Python DFS',0);
    
    # Good luck figuring out what this does? 
    # https://stackoverflow.com/questions/29808421/how-do-i-convert-from-an
    # -ironpython-datetime-to-a-net-datetime
    starttimeDT = System.DateTime(*dates.num2date(
                                  gauge_time[0]).timetuple()[:6], 
                                  kind=System.DateTimeKind.Utc)

    timeMinutes = ((np.asarray(gauge_time)-gauge_time[0])*24*60).tolist()
    builder.SetDataType(0)
    # Not really needed...
    builder.SetGeographicalProjection(factory.CreateProjectionGeoOrigin(
                                      'UTM-33',12,54,2.6))
    
    # Set time axis
	builder.SetTemporalAxis(factory.CreateTemporalNonEqCalendarAxis(
                            DHI.Generic.MikeZero.eumUnit.eumUminute,
                            starttimeDT))
    
    # Create an item
	item1 = builder.CreateDynamicItemBuilder()
    dfsdataType = DHI.Generic.MikeZero.DFS.DfsSimpleType.Float;
    
    item1.Set('Rain_intensity', 
              DHI.Generic.MikeZero.eumQuantity(
              DHI.Generic.MikeZero.eumItem.eumIRainfallIntensity,
              DHI.Generic.MikeZero.eumUnit.eumUMicroMeterPerSecond), 
              dfsdataType)
    
    item1.SetValueType(DHI.Generic.MikeZero.DFS.DataValueType.Instantaneous)
    item1.SetAxis(factory.CreateAxisEqD0())
    builder.AddDynamicItem(item1.GetDynamicItemInfo())
    
    builder.CreateFile(out_file)
    dfs = builder.GetFile()
    
	# Populate C# array with time series
    gauge_intArr = System.Array.CreateInstance(float,len(gauge_int),1)
    for i,val in enumerate(gauge_int):
        gauge_intArr[i,0] = val
    
    DHI.Generic.MikeZero.DFS.dfs0.Dfs0Util.WriteDfs0DataDouble(dfs, 
                               System.Array[float](timeMinutes), gauge_intArr)

    dfs.Close()
    
    return

def read_dfs0(filename,script_folder):
    """
    Reads time serties from dfs0 file
    
    Input:
        file_name: Name of the input dfs0 file
        script_folder: Folder containing this shit
        
    Output:
        None
    """
    # Load MIKE SDK .NET
    clr.AddReference(script_folder + r"\dhi_sdk\DHI.Generic.MikeZero.DFS.dll")
    clr.AddReference(script_folder + r"\dhi_sdk\DHI.Generic.MikeZero.EUM.dll")
    import DHI.Generic.MikeZero.DFS
    import DHI.Generic.MikeZero.DFS.dfs0
    
    # Open and read DFS0-file
    dfs0_file = DHI.Generic.MikeZero.DFS.DfsFileFactory.DfsGenericOpen(filename)
    dd = DHI.Generic.MikeZero.DFS.dfs0.Dfs0Util.ReadDfs0DataDouble(dfs0_file)
    # System.Double[[time], [data]] # Time: Seconds since first time step 0. 
    # data: Whatever what is in the dfs0 file
    
    # Get start date to use to calculate the other time steps (yes, this is where
    # it gets retarded)
    start_date = datetime.datetime(dfs0_file.FileInfo.TimeAxis.StartDateTime.Year,
                                   dfs0_file.FileInfo.TimeAxis.StartDateTime.Month,
                                   dfs0_file.FileInfo.TimeAxis.StartDateTime.Day,
                                   dfs0_file.FileInfo.TimeAxis.StartDateTime.Hour,
                                   dfs0_file.FileInfo.TimeAxis.StartDateTime.Minute,
                                   dfs0_file.FileInfo.TimeAxis.StartDateTime.Second)
    dfs0_file.Close()
    
    # Convert the time series to a numpy array
    ddlist = np.array(list(dd))
    # Use the start date as a reference to the relative time found in the dfs0 file
    gauge_time = ddlist[range(0,len(ddlist),2)]/60/60/24 + dates.date2num(start_date)
    #toMicroMeterPerSecondFactor = DHI.Generic.MikeZero.eumUtil.ConvertToBase(dfs0_file.ItemInfo.__getitem__(0).Quantity.Unit,1.0)*1e6
    gauge_int = ddlist[range(1,len(ddlist),2)]
    
    return gauge_time, gauge_int

# Read data:
f_name = r'C:\Users\Rasmus\Desktop\write_dfs0\5625.dfs0'
s_folder = r'C:\Users\Rasmus\Desktop\write_dfs0'
time, data = read_dfs0(f_name, s_folder)
print(type(time), dates.num2date(time)[-1])
print(type(data), data)

write_dfs0(time, data, 'output.dfs0', s_folder)