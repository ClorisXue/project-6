import sys
import re
import os
from sys import argv

class DECODE():
    COMP_MNEMONIC_BITS={
        '0' : '0101010',
        '1' : '0111111',
        '-1': '0111010',
        'D' : '0001100',
        'A' : '0110000',
        '!D': '0001101',
        '!A': '0110001',
        '-D': '0001111',
        '-A': '0110011',
        'D+1': '0011111',
        'A+1': '0110111',
        'D-1': '0001110',
        'A-1': '0110010',
        'D+A': '0000010',
        'D-A': '0010011',
        'A-D': '0000111',
        'D&A': '0000000',
        'D|A': '0010101',
        'null': '0000000',
        'M'  : '1110000',
        '!M': '1110001',
        '-M': '1110011',
        'M+1': '1110111',
        'M-1': '1110010',
        'D+M': '1000010',
        'D-M': '1010011',
        'M-D': '1000111',
        'D&M': '1000000',
        'D|M': '1010101'
    }

    DESTINATION_BITS={
        'null' : '000',
        'M'  : '001',
        'D'  : '010',
        'MD' : '011',
        'A'  : '100',
        'AM' : '101',
        'AD' : '110',
        'AMD': '111'
    }

    JUMP_BITS={
        'null' : '000',
        'JGT': '001',
        'JEQ': '010',
        'JGE': '011',
        'JLT': '100',
        'JNE': '101',
        'JLE': '110',
        'JMP': '111'
    }

    LABLE={
        'SP'    : '0',
        'LCL'   : '1',
        'ARG'   : '2',
        'THIS'  : '3',
        'THAT'  : '4',
        'R0'  : 0,
        'R1'  : 1,
        'R2'  : 2,
        'R3'  : 3,
        'R4'  : 4,
        'R5'  : 5,
        'R6'  : 6,
        'R7'  : 7,
        'R8'  : 8,
        'R9'  : 9,
        'R10' : 10,
        'R11' : 11,
        'R12' : 12,
        'R13' : 13,
        'R14' : 14,
        'R15' : 15,
        'SCREEN': 16384,
        'KBD'   : 24576
    }

#open the file need to be transferred
def openFile(fileName):
    with open(fileName, 'r') as hackFile:
        commands = hackFile.readlines()
    return (commands)

#write the transferred binary code in to a hack file
def writeFile(list, fileName):
    hackFile = fileName[:fileName.find('.') + 1] + 'hack'
    with open(hackFile, 'w') as file:
        for item in list:
            file.write("%s\n" % item)

#determine which type of instruction is read
def determineCommandType(command):
    if '=' in command or ';' in command:
        return ('C_Type')
    elif command.startswith('@'):
        return ('A_Type')

#if the code is A type
def AParser(command):
    num = int(command[1:])
    return(bin(num)[2:].zfill(16))

def CParser(command):
    if '=' in command or ';' in command:
        if '=' in command and ';' in command:
            comp = command[command.find('=')+1: command.find(';')]
            dest = command[0:command.find('=')]
            jump = command[command.find(';')+1:]
        elif ';' not in command:
            comp = command[command.find('=')+1:]
            dest = command[0:command.find('=')]
            jump = 'null'
        elif '=' not in command:
            comp = command[0: command.find(';')]
            dest = 'null'
            jump = command[command.find(';') + 1:]
    return(tableConvert(comp, dest, jump))

def tableConvert(comp, dest, jump):
    compBinary = DECODE.COMP_MNEMONIC_BITS[comp]
    destBinary = DECODE.DESTINATION_BITS[dest]
    jumpBianry = DECODE.JUMP_BITS[jump]
    return ('111' + compBinary + destBinary + jumpBianry)


def readCommands(commandList):
    binaryCommands = []
    for command in commandList:
        if determineCommandType(command) == 'A_Type':
            binaryCommands.append(AParser(command))
        elif determineCommandType(command) == 'C_Type':
            binaryCommands.append(CParser(command))
        else:
            pass
    return (binaryCommands)

def is_symbol(s):
	try:
		int(s)
		return False
	except ValueError:
		return True

def firstPass(symbol, commandList):
    count = 0
    for command in commandList:
        if '=' or ';' in command or command.startswith('@'):
            count += 1
        else:
            symbol[command.strip('()')]=str(count)
    return (symbol)

def secondPass(symbol, commandList):
    ramaddress = 16
    for i in range(len(commandList)):
        command = commandList[i]
        if command.startswith('@') and is_symbol(command[1:]):
            try:
                s=str(command[1:])
                commandList[i] = '@' + str(symbol[s])
            except KeyError:
                symbol[command[1:]] = str(ramaddress)
                ramaddress += 1
                commandList[i] = '@' + symbol[command[1:]]
    return (symbol)


def removecomments(commandList):
    commandList = list(map(commentline, commandList))
    commandList = [i.strip('\n') for i in commandList]
    commandList = [i.strip(' ') for i in commandList]
    commandList = list(filter(lambda x: x != '', commandList))
    commandList = list(filter(lambda x: x != '\n', commandList))
    return (commandList)


# removes comments from one line
def commentline(line):
    op = '//'
    index = line.find(op)
    if index == -1:
        return (line)
    elif index == 0:
        return ('')
    else:
        line = line[:(index - 1)]
    return line


fileName = 'RectL.asm'
commandList = removecomments(openFile(fileName))
symboltable = secondPass(firstPass(DECODE.LABLE, commandList), commandList)
writeFile(readCommands(commandList), fileName)




