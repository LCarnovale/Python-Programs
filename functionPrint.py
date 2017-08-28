# Written by Leo Carnovale
# Made yonks ago but done up properly on 24/08/2017

# Takes python source code and makes a file and optionally runs it with print
# statements after every function call, printing out the function's name and
# the given parameter values, so that every time any function is called
# the program tells you what's happening

# Usage of -t parameter: (Redundant)
#    -t '\t' or just -t \t will tell the program that tabs are used for indents.
#    -t 4 will tell the program that 4 spaces are used for indents. Use a different
#         integer to tell it to use other amounts.
# Usage of -m:
#    -m allows modules to be converted aswell.
#         To provide modules, list their paths after -m.
#         If you include -r when running with modules, the program will
#         temporarily change the names of each module so that the running program
#         uses the modified ones. They will be instantly reverted to their original
#         names once your program has finished, hopefully in the event of a crash/KeyboardInterrupt aswell.
# Usage of -s:
#     Provide a string of command line arguments after -s which will be run with
#         your program if you include -r. Enclose the arguments in quotes ('...')
#
# Put #NOFP after a function definition to tell this program to ignore it.
# The first function here uses it as an example.

import sys
import os

DEFAULT_INDENT = "\t"

if (len(sys.argv) < 2):
	print("Usage: %s <path> [-r (run)] [-t {'\t'|<n>}] [-s '<run arguments>'] [-m <path1> {<path2>}]" % (sys.argv[0]))
	exit()
else:
	RUN = False
	PATH = "default.py"
	if ("-r" in sys.argv): RUN = True
	# if ("-t" in sys.argv):
	# 	indentArg = sys.argv[sys.argv.index("-t") + 1]
	# 	if (indentArg in ['\t', "'\t'"]): indent = "\t"
	# 	if (indentArg.isnumeric()): indent = int(indentArg) * " "
	# else:
	# 	indent = DEFAULT_INDENT
	# Dont need this ^^ cause it handles indents automatically!
	PATH = sys.argv[1]
	COMMAND_ARGS = ""
	if ("-s" in sys.argv):
		COMMAND_ARGS = sys.argv[sys.argv.index("-s") + 1]
	MODULES = False
	if ("-m" in sys.argv):
		MODULES = (" ".join(sys.argv)).split("-m")[1].split(" ")
		MODULES = [M for M in MODULES if M]



# returns all whitespace before a non whitespace character on a line.
def getIndent(string):
	returnString = ""
	for c in string:
		if not c.isspace(): break
		returnString += c
	return returnString

# determines if a line is commented out
def isCommented(string): #NOFP - you can have text after but the characters '#NOFP' must be present
	whits = getIndent(string)
	if (not string): return False
	s = string
	if whits: s = string.split(whits)
	if s:
		if s[0] == "#": return True
	return False

# Takes a string and pulls out the comma separated arguments
def extractArgs(string):
	brackLevel = 0 # 1 when between open and closing brackets
	args = []

	# argsString = ""
	newString = '' # Will be a modified version of string to identify args better
	for c in string:
		if (c == "[" and brackLevel == 0):
			return None
		if c in ["(", "["]:
			brackLevel += 1
			if (brackLevel == 1): continue
		if c in [")", "]"]:
			brackLevel -= 1
			if (brackLevel == 1): continue
		if (brackLevel == 1):
			if (c == ','):
				newString += "###"
			else:
				newString += c

	if (not newString):
		return None
	# Now newstring contains only the args, no enclosing brackets, separated by ###'s
	preArgs = newString.split("###")
	preArgs = [x.split("=")[0] for x in preArgs]
	args = [[y for y in x.split(" ") if y][0] for x in preArgs]
	return args


f = open(PATH, "r")
File = f.read()
f.close()

FileLines = File.split("\n")
newFile = ""

# For each line, if not a function definition:
# 	Add the line to the newfile.
# If a function definition:
#	Add the line, plus a print statement.
classIndent = ""
FILE = PATH[:-3]
CLASS = ""
DONT_INSERT = False
for i, line in enumerate(FileLines):
	newFile += line + "\n"
	if (DONT_INSERT and ":" in line):
		# print("Inserting in line %d" % (i + 1))
		newFile += nextLine
		DONT_INSERT = False

	if (isCommented(line)): continue

	if (CLASS and len(getIndent(line)) <= len(classIndent)):
		print("Class %s ending at line %d, indent: '%s'" % (CLASS, i, getIndent(line)))
		classIndent = ""
		CLASS = ""

	if ("class" in line and ":" in line and (line.split("class")[0].isspace() or line[0:5] == "class")):
		CLASS = line.split("class ")[1].split(":")[0]
		classIndent = getIndent(line)

	if ("def " in line and (line.split("def")[0].isspace() or line[0:3] == 'def')):
		if "#NOFP" in line: continue
		if (":" not in line):
			DONT_INSERT = True
		# This line contains a function definition.
		funcArgs = extractArgs(line)

		funcName = (line.split("def ")[1].split("("))[0]

		# nextLine = FileLines[i + 1].split()[0] + "print(\"Function - '" + funcName + "': "

		# The following extracts the whitespace before code on the next line with code.
		funcWhiteSpace = line.split("def")[0] # Compares the target function and line we find the next indent whitespace
		for line2 in FileLines[i + 1:]:
			whitespace = ""
			if line2 and line2[-1] not in [",", "+", "-", "(", "["]:
				for c in line2:
					if not c.isspace():
						if (c == "#"): whitespace = "" # don't include commented lines
						break
					whitespace += c
				if (len(whitespace) <= len(funcWhiteSpace)):
					continue
				else:
					break

		funcTag = funcName
		if CLASS: funcTag = CLASS + "." + funcTag
		funcTag = FILE + "." + funcTag

		nextLine = whitespace + "print(\"Function - " + funcTag + ": "

		if (funcArgs == None):
			# A function with no args.
			nextLine += "<No arguments>\")"
		else:

			nextLine += funcArgs[0] + " = {}"
			if (len(funcArgs) > 1):
				for arg in funcArgs[1:]:
					nextLine += ", " + arg + " = {}"
			nextLine += '".format('
			nextLine += ",".join(funcArgs)
			nextLine += "))"
		nextLine += "\n"
		if not DONT_INSERT: newFile += nextLine

NEW_PATH = PATH[:-3] + "FunctionPrint.py"
f = open(NEW_PATH, "w")
f.write(newFile)
f.close()

if (RUN):
	if MODULES:
		print("Converting modules...")
		selfCallString = (sys.argv[0] if " " not in sys.argv[0] else sys.argv[0].split("\\")[-1])
		print(selfCallString)
		for M in MODULES:
			os.system("%s %s" %(selfCallString, M))
			os.rename(M, M[:-3] + "ORIGINAL.py")
			os.rename(M[:-3] + "FunctionPrint.py", M)
	print("Running: python %s %s" % (NEW_PATH, COMMAND_ARGS))
	try:
		os.system("python %s %s" % (NEW_PATH, COMMAND_ARGS))
	except KeyboardInterrupt:
		print("Aborting...")
	except Exception:
		print("Crashing...")
	if MODULES:
		print("Reverting modules...")
		for M in MODULES:
			os.rename(M, M[:-3] + "FunctionPrint.py")
			os.rename(M[:-3] + "ORIGINAL.py", M)
		print("Modules Restored.")
