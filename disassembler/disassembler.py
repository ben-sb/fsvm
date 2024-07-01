from enum import Enum

class Mnemonic(Enum):
    REL_JMP = 'rel_jmp'
    IF_EQ_REL_JMP = 'if_eq_rel_jmp'
    IF_NEQ_REL_JMP = 'if_neq_rel_jmp'
    IF_LT_REL_JMP = 'if_lt_rel_jmp'
    CLEAR = 'clear'
    WRITE_LAST_CHAR_CODE = 'write_last_char_code'
    WRITE_CHAR = 'write_char'
    CONCAT_STRINGS = 'concat_strings'
    SET = 'set'
    ADD = 'add'
    APPEND = 'append'
    POP_LAST_CHAR = 'pop_last_char'
    INVERT_SIGN = 'invert_sign'
    PRINT = 'print'
    READ_STR = 'read_str'
    RET = 'ret'

# instructions that cause jumps/transfer control
BRANCH_MNEMONICS = {Mnemonic.RET, Mnemonic.REL_JMP, Mnemonic.IF_EQ_REL_JMP, Mnemonic.IF_NEQ_REL_JMP, Mnemonic.IF_LT_REL_JMP}

class Reg(Enum):
    REG_0 = 'reg0'
    REG_1 = 'reg1'
    REG_2 = 'reg2'
    REG_3 = 'reg3'
    REG_4 = 'reg4'
    REG_5 = 'reg5'
    REG_6 = 'reg6'
    REG_7 = 'reg7'

def get_reg(reg_id: int) -> Reg:
    if reg_id >= 0 and reg_id <= 7:
        return Reg[f'REG_{reg_id}']
    else:
        raise Exception(f'Unknown register with ID {reg_id}')
    
def operand_to_str(operand: Reg | str | int):
    if isinstance(operand, Reg):
        return operand.value
    else:
        return str(operand)

class Instr:
    def __init__(self, addr: int, mnemonic: Mnemonic, *operands) -> None:
        self.address = addr
        self.mnemonic = mnemonic
        self.operands = operands

    def __str__(self) -> str:
        operand_str = ', '.join([operand_to_str(o) for o in self.operands])
        num_spaces = 22 - len(self.mnemonic.value)
        return f'{hex(self.address)}:\t{self.mnemonic.value}{' '* num_spaces}{operand_str}'

class Disassembler:
    def __init__(self, bytecode: list[int]) -> None:
        self.bytecode = bytecode
        self.pos = 0
        self.instructions = []

    def read_byte(self):
        byte = self.bytecode[self.pos]
        self.pos += 1
        return byte
    
    def get_disassembly(self) -> list[str]:
        disassembly = []

        for instr in self.instructions:
            disassembly.append(str(instr) + '\n')
            if instr.mnemonic in BRANCH_MNEMONICS:
                disassembly.append('\n')

        return disassembly
    
    def disassemble(self) -> list[Instr]:
        while self.pos < len(self.bytecode):
            addr = self.pos
            opcode = self.read_byte()

            match opcode:

                # jumps to (pos + reg5)
                case 40:
                    offset = Reg.REG_5
                    self.instructions.append(Instr(addr, Mnemonic.REL_JMP, offset))

                # jumps to (pos + offset) if reg6 == reg7
                case 41:
                    # these registers are fixed in the handler
                    offset = Reg.REG_5
                    left = Reg.REG_6
                    right = Reg.REG_7
                    self.instructions.append(Instr(addr, Mnemonic.IF_EQ_REL_JMP, offset, left, right))

                # jumps to (pos + r5) if reg6 != reg7
                case 42:
                    # these registers are fixed in the handler
                    offset = Reg.REG_5
                    left = Reg.REG_6
                    right = Reg.REG_7
                    self.instructions.append(Instr(addr, Mnemonic.IF_NEQ_REL_JMP, offset, left, right))

                # jumps to (pos + reg5) if reg6 < reg7
                case 43:
                    # these registers are fixed in the handler
                    left = Reg.REG_6
                    right = Reg.REG_7
                    offset = Reg.REG_5 # loaded only if less than condition is true
                    self.instructions.append(Instr(addr, Mnemonic.IF_LT_REL_JMP, left, right, offset))

                # clear reg
                case 44 | 45 | 46 | 47 | 48| 49 | 50 | 51:
                    reg = get_reg(opcode - 44)
                    self.instructions.append(Instr(addr, Mnemonic.CLEAR, reg))

                # opcodes 52 - 60 don't exist

                # get char code of last char of string
                case 61:
                    src = get_reg(self.read_byte())
                    dest = get_reg(self.read_byte())
                    self.instructions.append(Instr(addr, Mnemonic.WRITE_LAST_CHAR_CODE, dest, src))

                # write char given by int in reg
                case 62:
                    src = get_reg(self.read_byte())
                    dest = get_reg(self.read_byte())
                    self.instructions.append(Instr(addr, Mnemonic.WRITE_CHAR, dest, src))

                # converts registers to strings/chars and concats them
                case 63:
                    left = get_reg(self.read_byte())
                    right = get_reg(self.read_byte())
                    dest = get_reg(self.read_byte())
                    self.instructions.append(Instr(addr, Mnemonic.CONCAT_STRINGS, dest, left, right))

                # set reg = '0'
                case 64 | 65 | 66 | 67 | 68 | 69 | 70 | 71:
                    reg = get_reg(opcode - 64)
                    self.instructions.append(Instr(addr, Mnemonic.SET, reg, '0'))

                # opcodes 72 - 80 don't exist

                # add
                case 81:
                    left = get_reg(self.read_byte())
                    right = get_reg(self.read_byte())
                    dest = get_reg(self.read_byte())
                    self.instructions.append(Instr(addr, Mnemonic.ADD, dest, left, right))

                # append '1' to reg
                case 82:
                    reg = get_reg(self.read_byte())
                    self.instructions.append(Instr(addr, Mnemonic.APPEND, reg, '1'))

                # pop last char of string (store in same reg)
                case 83:
                    reg = get_reg(self.read_byte())
                    self.instructions.append(Instr(addr, Mnemonic.POP_LAST_CHAR, reg))

                # invert sign of reg
                case 84:
                    reg = get_reg(self.read_byte())
                    self.instructions.append(Instr(addr, Mnemonic.INVERT_SIGN, reg))
                    pass

                # print string to stdout
                case 85:
                    self.instructions.append(Instr(addr, Mnemonic.PRINT, Reg.REG_4))

                # read string from stdin
                case 86:
                    self.instructions.append(Instr(addr, Mnemonic.READ_STR, Reg.REG_0))

                # exit
                case 87:
                    self.instructions.append(Instr(addr, Mnemonic.RET))

                case _:
                    raise Exception(f'Unknown opcode {opcode}')
        
        return self.instructions