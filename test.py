"""
Reads and writes a dfs0 file
"""

import dfs0_utils

# Read data:
f_name = r'C:\Users\MIKE\Desktop\write_dfs0\5625.dfs0'
s_folder = r'C:\Users\MIKE\Desktop\write_dfs0'

time, data = dfs0_utils.read_dfs0(f_name, s_folder)

# Help for picking the correct input formats
print(type(time), time)
print(type(time[0]), time[0])
print(type(data), data)
print(type(data[0]), data[0])

dfs0_utils.write_dfs0(time, data, 'output.dfs0', s_folder)