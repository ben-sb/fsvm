from disassembler.disassembler import Instr, Mnemonic, Reg
from enum import Enum
from symbolic.symbols import *
from symbolic.cfg import Node, ConditionalNode
from typing import Self

class SymbolicExecutor:
    def __init__(self, instructions: list[Instr]) -> None:
        self.instructions = instructions
        self.instruction_map = self.build_instruction_map(instructions)
        self.last_id = 0
        self.root_state = State(self, 0)
        self.active_states = [self.root_state]
        self.finished_states = []

    def build_instruction_map(self, instructions: list[Instr]) -> dict[int, Instr]:
        map = {}
        for instr in instructions:
            map[instr.address] = instr
        return map

    def explore(self) -> None:
        while len(self.active_states) > 0:
            self.step()

    def step(self) -> None:
        for state in self.active_states[:]:
            instr = self.instructions[state.pos]
            state.step(instr)

            for new_state in state.successors:
                self.active_states.append(new_state)

            if state.status != Status.ACTIVE:
                self.finished_states.append(state)
                self.active_states.remove(state)

    def get_next_id(self) -> int:
        id = self.last_id
        self.last_id += 1
        return id
    
    def get_pseudocode(self) -> str:
        body = '\n\t'.join(self.root_state.cfg.codegen())
        return f'#include <stdio.h>\n\nint main(int argc, char* argv[]) {{\n\t{body}\n}}'
                
class Status(Enum):
    ACTIVE = 0
    TERMINATED = 1
    ERRORED = 2

class State:
    def __init__(self, executor: SymbolicExecutor, pos: int) -> None:
        self.executor = executor
        self.id = executor.get_next_id()
        self.pos = pos
        self.regs = [''] * 8
        self.status = Status.ACTIVE
        self.cfg = Node()
        self.successors = []

    def clone(self) -> Self:
        s = State(self.executor, self.pos)
        for i in range(0, len(self.regs)):
            item = self.regs[i]
            copy = item.copy() if isinstance(item, Symbol) else item
            s.regs[i] = copy
        return s

    def get_reg_id(self, operand) -> int:
        if not isinstance(operand, Reg):
            raise Exception(f'Unknown operand, expected register')
        return int(operand.value[3])
    
    def get_str(self, operand: Symbol | str) -> str:
        if not isinstance(operand, str):
            raise Exception(f'Unknown operand, expected int')
        return operand
    
    def prepare_for_numeric_operation(self, operand: Symbol | str):
        if isinstance(operand, Symbol):
            return operand
        else:
            return str(int(operand))
        
    def prepare_for_str_comparison(self, operand: Symbol | str):
        if isinstance(operand, Symbol):
            return str(operand)
        else:
            return f'"{operand}"'
        
    def access_last_char(self, operand: Symbol | str) -> Symbol | str:
        if isinstance(operand, StringSymbol) and isinstance(operand.len, int):
                return MemberExpressionSymbol(operand.copy(), operand.len - 1)
        elif isinstance(operand, Symbol):
            length = MemberExpressionSymbol(operand.copy(), '"length"')
            return MemberExpressionSymbol(operand.copy(), BinaryExpressionSymbol('-', length, 1))
        else:
            return str[:-1]
        
    def pop_last_char(self, operand: Symbol | str) -> Symbol | str:
        if isinstance(operand, StringSymbol) and isinstance(operand.len, int):
            return StringSymbol(operand.name, operand.len - 1)
        if isinstance(operand, Symbol):
            return MemberExpressionSymbol(operand.copy(), ':-1')
        else:
            return str[:-1]

    def step(self, instr: Instr) -> None:
        self.pos += 1

        match instr.mnemonic:
            case Mnemonic.CLEAR:
                reg = self.get_reg_id(instr.operands[0])
                self.regs[reg] = ''

            case Mnemonic.SET:
                reg = self.get_reg_id(instr.operands[0])
                val = self.get_str(instr.operands[1])
                self.regs[reg] = val

            case Mnemonic.APPEND:
                reg = self.get_reg_id(instr.operands[0])
                val = self.get_str(instr.operands[1])
                self.regs[reg] += val

            case Mnemonic.ADD:
                dest_id = self.get_reg_id(instr.operands[0])
                left = self.regs[self.get_reg_id(instr.operands[1])]
                right = self.regs[self.get_reg_id(instr.operands[2])]

                if left == '' or right == '':
                    result = left if right == '' else right
                elif isinstance(left, Symbol) or isinstance(right, Symbol):
                    result = BinaryExpressionSymbol(
                        '+', 
                        self.prepare_for_numeric_operation(left), 
                        self.prepare_for_numeric_operation(right)
                    )
                else:
                    result = str(int(left) + int(right))

                self.regs[dest_id] = result

            case Mnemonic.CONCAT_STRINGS:
                dest_id = self.get_reg_id(instr.operands[0])
                left = self.regs[self.get_reg_id(instr.operands[1])]
                right = self.regs[self.get_reg_id(instr.operands[2])]

                if left == '' or right == '':
                    result = left if right == '' else right
                elif isinstance(left, Symbol) or isinstance(right, Symbol):
                    result = BinaryExpressionSymbol('+', left, right)
                else:
                    result = left + right

                self.regs[dest_id] = result

            case Mnemonic.INVERT_SIGN:
                reg_id = self.get_reg_id(instr.operands[0])
                val = self.regs[reg_id]

                if isinstance(val, Symbol):
                    result = UnaryExpressionSymbol('-', val)
                else:
                    result = str(-1 * int(val))

                self.regs[reg_id] = result

            case Mnemonic.WRITE_CHAR:
                dest = self.get_reg_id(instr.operands[0])
                src = self.get_reg_id(instr.operands[1])
                char_code = int(self.regs[src])
                self.regs[dest] = chr(char_code)

            case Mnemonic.WRITE_LAST_CHAR_CODE:
                dest_id = self.get_reg_id(instr.operands[0])
                val = self.regs[self.get_reg_id(instr.operands[1])]

                self.regs[dest_id] = self.access_last_char(val)

            case Mnemonic.POP_LAST_CHAR:
                reg_id = self.get_reg_id(instr.operands[0])
                val = self.regs[reg_id]

                self.regs[reg_id] = self.pop_last_char(val)

            case Mnemonic.PRINT:
                val = self.regs[self.get_reg_id(instr.operands[0])]
                self.cfg.add_statement(f'puts("{str(val)}");')

            case Mnemonic.READ_STR:
                reg_id = self.get_reg_id(instr.operands[0])
                flag_len = 29 # hardcoded for this sample
                self.regs[reg_id] = StringSymbol('flag', flag_len)
                self.cfg.add_statement(f'char flag[{flag_len}];')
                self.cfg.add_statement('scanf("%s", flag);')

            # TODO: other jumps (not used)

            case Mnemonic.JNE:
                offset = self.regs[self.get_reg_id(instr.operands[0])]
                left = self.regs[self.get_reg_id(instr.operands[1])]
                right = self.regs[self.get_reg_id(instr.operands[2])]

                if isinstance(offset, Symbol):
                    print('Jump to symbolic value, cannot follow')
                    consequent_node = Node()
                    consequent_node.add_statement('// unknown path')
                    self.status = Status.ERRORED
                else:
                    offset = int(offset)
                    consequent_addr = instr.address + 1 + offset
                    if consequent_addr in self.executor.instruction_map:
                        target = self.executor.instruction_map[consequent_addr]
                        consequent = self.clone()
                        consequent.pos = self.executor.instructions.index(target)
                        consequent_node = consequent.cfg
                        self.successors.append(consequent)
                        self.status = Status.TERMINATED
                    else:
                        print('Could not find consequent branch of conditional')
                        consequent_node = Node()
                        consequent_node.add_statement('// unknown path')
                        self.status = Status.ERRORED

                    alternate = self.clone()
                    self.successors.append(alternate)

                    test = f'{self.prepare_for_str_comparison(left)} != {self.prepare_for_str_comparison(right)}'
                    conditional = ConditionalNode(test, consequent_node, alternate.cfg)
                    self.cfg.next = conditional

            case Mnemonic.RET:
                self.status = Status.TERMINATED
                self.cfg.add_statement('return 0;')

            case _:
                raise Exception(f'Unsupported mnemonic {instr.mnemonic}')