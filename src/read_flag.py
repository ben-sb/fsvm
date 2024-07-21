import re

code = open('output/pseudocode.c', 'r').read()
result = re.findall("\\+ (\\d+)", code)

flag = ''.join([chr(int(x)) for x in result])
print(flag)

"""
openECSC{supereasyvmc4e87c4d}
"""