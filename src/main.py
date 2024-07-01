from disassembler.disassembler import Disassembler
from symbolic.symbolic_executor import SymbolicExecutor

bytecode = [int(x) for x in open('input/bytecode', 'rb').read()]

dis = Disassembler(bytecode)
instrs = dis.disassemble()

disassembly = dis.get_disassembly()
open('output/disassembly.txt', 'w').write(''.join(disassembly))

executor = SymbolicExecutor(instrs)
executor.explore()

pseudcode = executor.get_pseudocode()
open('output/pseudocode.c', 'w').write(pseudcode)