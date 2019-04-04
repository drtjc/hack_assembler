import sys
import os
from collections import UserDict
from typing import Dict


# symbol table #########################################################
class SymbolTable(UserDict):

    def __init__(self):
        super().__init__()

        for i in range(16):
            self['R' + str(i)] = i

        self['SCREEN'] = 16384
        self['KBD'] = 24576

        self['SP'] = 0
        self['LCL'] = 1
        self['ARG'] = 2
        self['THIS'] = 3
        self['THAT'] = 4

        self.var_idx = 16

    def add_label(self, label: str, value: int):
        self[label] = value

    def add_variable(self, var: str):
        if var not in self:
            self[var] = self.var_idx
            self.var_idx += 1

########################################################################


# parser ###############################################################
class Parser():

    def __init__(self, symbol_table: SymbolTable):
        self.line = ""
        self.line_no = -1
        self.symbol_table = symbol_table
        self._first_pass = True

    @property
    def first_pass(self) -> bool:
        return self._first_pass

    @first_pass.setter
    def first_pass(self, fp: bool) -> None:
        if fp != self._first_pass:
            self.line_no = -1
        self._first_pass = fp
        
    def parse(self, line: str):

        # remove newline
        # remove leading and trailing spaces
        # remove comments
        self.line = line.rstrip('\n').strip().split('//')[0].rstrip()

        if self.line and self.line[0] == "(" and self.line[-1] == ")":
            # label symbol (which is not a line of code)
            label = self.line[1:-1]
            self.line = ""

            # add symbol to symbol table
            if self.first_pass:
                self.symbol_table.add_label(label, self.line_no + 1)
            
        # if line is not empty then increment line_no
        if self.line:
            self.line_no += 1

        if not self.first_pass:
            if self.line and self.line[0] == "@":
                # variable symbol or goto (a label symbol) or integer
                var = self.line[1:]
                if not var.isdigit():            
                    self.symbol_table.add_variable(var)
                    self.line = "@" + str(self.symbol_table[var])

        return self.line

########################################################################


# code #################################################################
class Code():

    A_SIZE = 15

    dest_table = {}
    dest_table[''] = '000'
    dest_table['M'] = '001'
    dest_table['D'] = '010'
    dest_table['MD'] = '011'
    dest_table['A'] = '100'
    dest_table['AM'] = '101'
    dest_table['AD'] = '110'
    dest_table['AMD'] = '111'
    
    comp_table = {}
    comp_table['0'] = ('0', '101010')
    comp_table['1'] = ('0', '111111')
    comp_table['-1'] = ('0', '111010')
    comp_table['D'] = ('0', '001100')
    comp_table['A'] = ('0', '110000')    
    comp_table['!D'] = ('0', '001101')
    comp_table['!A'] = ('0', '110001')
    comp_table['-D'] = ('0', '001111')
    comp_table['-A'] = ('0', '110011')
    comp_table['D+1'] = ('0', '011111')
    comp_table['A+1'] = ('0', '110111')
    comp_table['D-1'] = ('0', '001110')
    comp_table['A-1'] = ('0', '110010')
    comp_table['D+A'] = ('0', '000010')
    comp_table['D-A'] = ('0', '010011')
    comp_table['A-D'] = ('0', '000111')
    comp_table['D&A'] = ('0', '000000')
    comp_table['D|A'] = ('0', '010101')
    comp_table['M'] = ('1', '110000')
    comp_table['!M'] = ('1', '110001')
    comp_table['-M'] = ('1', '110011')
    comp_table['M+1'] = ('1', '110111')
    comp_table['M-1'] = ('1', '110010')
    comp_table['D+M'] = ('1', '000010')
    comp_table['D-M'] = ('1', '010011')
    comp_table['M-D'] = ('1', '000111')
    comp_table['D&M'] = ('1', '000000')
    comp_table['D|M'] = ('1', '010101')

    jump_table = {}
    jump_table[''] = '000'
    jump_table['JGT'] = '001'
    jump_table['JEQ'] = '010'
    jump_table['JGE'] = '011'
    jump_table['JLT'] = '100'
    jump_table['JNE'] = '101'
    jump_table['JLE'] = '110'
    jump_table['JMP'] = '111'
 
    @classmethod
    def dec_bin(cls, dec: int, digit: int) -> str:
        if dec >= 0:
            bin1 = bin(dec).split("0b")[1]
            while len(bin1) < digit:
                bin1 = '0' + bin1
            return bin1
        else:
            bin1 = str(-1 * dec)
            return bin(dec - pow(2, digit)).split("0b")[1]

    def code(self, instruction: str) -> str:
        if instruction[0] == "@": # A-instruction
            return self._a_instruction(instruction)
        else: # C-instruction
            return self._c_instruction(instruction)

    def _a_instruction(self, instruction: str) -> str:
            A_10 = int(instruction[1:])
            A_2 = self.dec_bin(A_10, self.A_SIZE)
            b = '0' + A_2
            return b

    def _c_instruction(self, instruction: str) -> str:
        dest = ""
        comp = ""
        jump = ""

        s1 = instruction.split('=')
        if len(s1) != 1: # there is a = sign
            dest = s1[0].strip()
            s2 = s1[1].strip()
        else:
            s2 = s1[0]

        s3 = s2.split(';')
        comp = s3[0].strip()
        if len(s3) != 1: # there is a ; sign
            jump = s3[1]
  
        b = "111" # C-instruction always starts with 111 
        b = b + self.comp_table[comp][0] + self.comp_table[comp][1]
        b = b + self.dest_table[dest]
        b = b + self.jump_table[jump] 

        return b

########################################################################


# main #################################################################
if __name__ == "__main__":

    filename_in = sys.argv[1]  
    filename_out = os.path.splitext(filename_in)[0] + ".hack"   

    p = Parser(SymbolTable())    
    c = Code()

    with open(filename_in, 'r') as f_in:
        for line in f_in:
            p.parse(line)

    p.first_pass = False
    with open(filename_in, 'r') as f_in:    
        with open(filename_out, 'w') as f_out:
            for line in f_in:
                l = p.parse(line)
                if l:
                    f_out.write(c.code(l) + '\n')

