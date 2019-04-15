# read_write_dfs0_python
Methods for reading and writing data from and to a DHI *.dfs0 file using MIKE SDK (https://www.mikepoweredbydhi.com/download/mike-2017/mike-sdk). This example reads and writes a rainfall time series.

Portable versions of Pythonnet are ALWAYS prefereable but one can use the Pythonnet packages from pip and just uncomment the lines:

```python
# Check system architecture
import struct
if struct.calcsize("P") * 8 == 64: # .NET compatibility
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "\clr64")
else:
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "\clr")
```

Documentation of the DHI MIKE .NET interface for python http://doc.mikepoweredbydhi.help/webhelp/2017/DHI_DFS/html/N_.htm
