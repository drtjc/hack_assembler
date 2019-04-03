import sys
import os
from typing import Dict


# symbol table #########################################################
symbol_table = {}
var_idx = 16

for i in range(15):
    symbol_table['R' + str(i)] = i

symbol_table['SCREEN'] = 16384
symbol_table['KBD'] = 24576

symbol_table['SP'] = 0
symbol_table['LCL'] = 1
symbol_table['ARG'] = 2
symbol_table['THIS'] = 3
symbol_table['THAT'] = 4

def add_label(label: str, value: int):
    symbol_table[label] = value

def add_variable(var: str):
    if var not in symbol_table:
        symbol_table[var] = var_idx
        var_idx += 1


########################################################################

from pprint import pprint

class Parser():

    def __init__(self, symbol_table: Dict):
        self.line = ""
        self.line_no = 0
        self.symbol_table = symbol_table

    def parse(self, line: str, first_pass: bool = True):

        if not first_pass:
            self.line_no = 0

        # remove newline
        # remove leading and trailing spaces
        # remove comments
        self.line = line.rstrip('\n').strip().split('\\')[0].rstrip()
        pprint(self.line)

        if self.line and self.line[0] == "(" and self.line[-1] == ")":
            # label symbol (which is not a line of code)
            label = self.line[1:-1]
            self.line = ""

            # add symbol to symbol table
            if first_pass:
                self.symbol_table[label] = self.line_no
            
            print("label symbol:" + self.line)

        # if line is not then increment line_no
        if self.line:
            self.line_no += 1
        else:
            print("not code")
            return

        if not first_pass:
            if self.line[0] == "@":
                # variable symbol or goto (a label symbol)
                var = self.line[1:]
            
                if var not in self.symbol_table:
                    symbol_table[var] = 16




        #else: # else if garbage code then raise error
        #    raise ValueError("garbage code")

        #print(f'line_no = {self.line_no}')
        # if valid line, do stuff, add to line_no
        
        # if label symbol
        # add_symbol('test', 35)


p = Parser(symbol_table)
p.parse("   abc   ")
p.parse("   abc   \n")
p.parse("   abc   \\ hi there\n")
p.parse("  \\ abc   ")
p.parse("     \n")
p.parse("  (STOP)  \\ \n")
p.parse("@i", False)




print(f'st={symbol_table}')

    
filename_in = sys.argv[1]  
filename_out = os.path.splitext(filename_in)[0] + ".hack"   




lines = []

with open(filename_in, 'r') as f_in:

    # initialize the

    with open(filename_out, 'w') as f_out:
        for line in f_in:
            line = line.rstrip('\n')
            lines.append(line)
            print(line)
            f_out.write(line + '\n')

print(lines)




