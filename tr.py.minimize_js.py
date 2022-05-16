#!/usr/bin/env python3
# Enable to pre minimize for another minimizer by renaming variables and functions
# Parameters eg : >py tr.py.minimize_js.py 



# Author:   Renan Lavarec
# Nickname: Ti-R
# Website:  www.ti-r.com
# License MIT


# -----------------------------+ HELP +-----------------------------

# 

import os
import argparse
import re

###########	   TO SET	  ##############

#debug level
DEBUG = True

########### TO SET - optional ##############

# Encoding if needed, should work with latin-1
encodingFile="utf-8"

###########################################################################
############### Clean svg file of unsed ref link


# args
parser = argparse.ArgumentParser()
parser.add_argument('--js', help='javascript name', required=True)
parser.add_argument('--excludeVarName', help='exclude var name from rename', required=False, nargs='*', default=[])
parser.add_argument('--restoreFirstLine', help='exclude var name from rename', action='store_true', required=False, default=False)
args = parser.parse_args()


def debug(*arg):
	if DEBUG:
		print(arg)


print('Start minimizing js...')
print('js file to minimize:', args.js)

jsFilenameMin = args.js.replace(".js", ".min.js")

###################################################### IF COPYING only the first line, open js, open .min.js, copy first line to .min
if(args.restoreFirstLine == True):
	with open (args.js, 'r' ) as f:
		firstLine = f.readline()
			
	with open (jsFilenameMin, 'r' ) as f:
		fileContent = f.read()

	with open(jsFilenameMin, 'w') as f:
		f.write(firstLine + fileContent)
	
	print('Restore first line for licence -> DONE')

	exit(0)

###################################################### READ FILE
print('Exclude from rename:', args.excludeVarName)

# Open and read the file
with open (args.js, 'r' ) as f:
	fileContent = f.read()

###################################################### Get all vars names to rename (let,const,var and member var), function are not included (will be do inside the next minimizer)
allVars = re.findall('(let|const|var)\s+(\w+?)\s*[,;)=]',fileContent)
allVars = allVars + re.findall('(\.)(\w+?)\s*[,;)=]',fileContent)

allVarsNames = []

for var in allVars:
	if(var[1] not in args.excludeVarName):
		allVarsNames.append(var[1])
#	else:
#		print("Those var won't be replace ", var[1])

allVarsNames = sorted(set(allVarsNames))

###################################################### PARSE JAVASCRIPT
javascriptKeyWords = ['abstract','arguments','boolean','break','byte','case','catch','char','const','continue','debugger','default','delete','do','double','else','eval','false','final','finally','float','for','function','goto','if','implements','in','instanceof','int','interface','let','long','native','new','null','package','private','protected','public','return','short','static','switch','synchronized','this','throw','throws','transient','true','try','typeof','var','void','volatile','while','with','class','enum','export','extends','import','super', 'length']


allStringsDoubleQuote = []

commentStarted = False
commentStartedOneLine = False
stringStarted = False
regexStarted = False
stringNoText = ''
stringWidthText = ''
stringRegEx = ''

StateNone='n'
StateRegEx='r'
StateString='s'
StateCommentOneLine='co'
StateCommentOneMultiLine='cm'
lastChar = ''
currentState = StateNone


# Check if the current char is escaped or not
#  True is escape, this char can't be used
def isEscape(stringBefore):
	escapeCount = 0	

	# inverse the string and look back if there is escape, count it, if pair, not escape, else escape
	for charToTest in stringBefore[::-1]:
		if(charToTest == "\\"):
			escapeCount = escapeCount+1
		else:
			break

	# pair -> no escape, the string stopped
	if(escapeCount%2 == 0):
		return False
	return True

def isRegEx(stringBefore):

	# / is not escape... could be a regex
	if not isEscape(stringNoText):
		# inverse the string and look back 
		for charToTest in stringBefore[::-1]:
			# we fond a space... before, ok continue
			if(charToTest == " " or charToTest == "\t"):
				continue

			# we found a parenthesis.... seems like a regex
			if(charToTest == "("):
				return True
			# we found a equal.... seems like a regex
			if(charToTest == "="):
				return True

			# Something else.... humm ok not a Regex
			return False
	return False

index = -1
lengthfileContent = len(fileContent)-1

## Inside the javascript, will remove all string, comments and regex to rename the var outside of those scope
while index < lengthfileContent:
	index=index+1
	char = fileContent[index]
	# None - looking for a state
	if currentState == StateNone:
		if(char == "'"):
			if not isEscape(stringNoText):
				endChar = "'"
				currentState = StateString
				stringWidthText="'"
				#print("String START '")
				continue

		if(char == '"'):
			if not isEscape(stringNoText):
				endChar = '"'
				currentState = StateString
				stringWidthText='"'
				#print("String START \"")
				continue

		# '//' -> Comment single line
		if(char == '/' and fileContent[index+1]=='/'):
			currentState = StateCommentOneLine
			index=index+1
			#print("Comment START //")
			continue

		# '//' -> Comment multi line
		if(char == '/' and fileContent[index+1]=='*'):
			currentState = StateCommentOneMultiLine
			index=index+1
			#print("Comment START /*")
			continue

		# '/' -> Regex
		if(char == '/'):
			if isRegEx(stringNoText):
				currentState = StateRegEx
				stringRegEx = '/'
				#print("RegEx START")
				continue

		stringNoText = stringNoText + char

	# String
	elif currentState == StateString:
		# end of string can be ' or ", cannot be \' or \", can be \\' or \\", cannot be \\\' or \\\" ....
		if(char == endChar):

			if not isEscape(stringWidthText):
				# stop the string
				currentState = StateNone
				#print("String END " + endChar)
				allStringsDoubleQuote.append(stringWidthText + endChar)
				stringNoText = stringNoText + '¤¤1'
			else:
				stringWidthText = stringWidthText + char
		else:
			stringWidthText = stringWidthText + char
			
	# Comment - Oneline
	elif currentState == StateCommentOneLine:
		# If end of line continue as before
		if(char == "\n"):
			currentState = StateNone
			stringNoText = stringNoText + "\n\n"
			#print("Comment END " + '//')
			continue

	# Comment - Multiline
	elif currentState == StateCommentOneMultiLine:
		# Wait to the end of multiline to continue
		if(char == '/' and lastChar == '*'):
			currentState = StateNone
			lastChar = ''
			#print("Comment END " + '*/')
			continue
		
		lastChar = char

	# Regex
	elif currentState == StateRegEx:
		# big mystake, we found a div....
		if(char == '/'):
			if not isEscape(stringRegEx):
				allStringsDoubleQuote.append(stringRegEx + char)
				#print("RegEx: ", stringRegEx + char)
				#print("RegEx END")
				stringRegEx = ''
				stringNoText = stringNoText + '¤¤1'
				currentState = StateNone
				continue

		stringRegEx = stringRegEx + char


fileContent = stringNoText


###################################################### REPLACE VARS

tVarRegExStart = '([\!\[{\^\.\s\(\)><\-\+;:,=])('
tVarRegExEnd = ')([\.\[\],;:$\/\s=\(\)|><\-\+}])'

tListVarStats = []
for var in allVarsNames:
	tFound = re.findall(tVarRegExStart+ var + tVarRegExEnd,fileContent)
	tListVarStats.append({"stats":len(tFound), "var":var})

tListVarStats = reversed(sorted(tListVarStats, key=lambda x: x['stats']))


tVarLetter = 'a'
for data in tListVarStats:
	var = data['var']
#	fileContent = re.sub('[\^\.\s\(]('+ var + ')[,;$\s=\)]', tVarLetter, fileContent)
	if(var not in javascriptKeyWords):
		fileContent = re.sub(tVarRegExStart+ var + tVarRegExEnd, lambda x: x.group(1) + tVarLetter + x.group(3), fileContent)
		#print("Rename var from", var, " to ", tVarLetter)


		while(True):
			
			# Try to find a valid name between a-z and A-Z
			lastLetter = ord(tVarLetter[len(tVarLetter)-1])

			# if last letter == z, add another one, 'a' to do 'za'
			if(lastLetter==ord('z') or lastLetter==ord('Z')):

				tFoundALetterNotZ = False
				tNewVarLetter = []
				# Reverse string
				tReverseVarLetter = tVarLetter[::-1]
				for letter in tReverseVarLetter:
					if(not tFoundALetterNotZ):
						if(ord(letter)<ord('z') and ord(letter)>=ord('a')):
							tNewVarLetter.append(chr(ord(letter)+1))
							tFoundALetterNotZ = True
						else:
							if(ord(letter)>ord('a')):
								tNewVarLetter.append('A')
								tFoundALetterNotZ = True

							elif(ord(letter)<ord('Z')):
								tNewVarLetter.append(chr(ord(letter)+1))
								tFoundALetterNotZ = True
					else:
						tNewVarLetter.append(letter)

				tNewVarLetter = list(reversed(tNewVarLetter))
				if( not tFoundALetterNotZ):
					tNewVarLetter = []
					for letter in tVarLetter:
						tNewVarLetter.append('a')
					tVarLetter = ''.join(tNewVarLetter) +'a'
				else:
					tLen = len(tVarLetter)
					tVarLetter = ''.join(tNewVarLetter)
					while(len(tVarLetter)<tLen):
						tVarLetter = tVarLetter +'a'
			else:
				# Increment last letter 'a' to 'b' or 'A' to 'B'
				if(len(tVarLetter)>1):
					tVarLetter = tVarLetter[0:len(tVarLetter)-1] + chr(ord(tVarLetter[len(tVarLetter)-1])+1)
				else:
					tVarLetter = chr(ord(tVarLetter[len(tVarLetter)-1])+1)

			# Filter generated word to do not be keywords
			if(tVarLetter not in javascriptKeyWords):
				break
			else:
				print("JS Keyword - reject minimized var name: ", tVarLetter)
	else:
		print("JS Keyword - reject var name: ", var)


###################################################### RESTORE STRING + REGEX

#   Restore all string "", '' and Regex
for string in allStringsDoubleQuote:
	fileContent = fileContent.replace('¤¤1', string, 1)

###################################################### SAVE FILE

with open(jsFilenameMin, 'w') as f:
	f.write(fileContent)

print('Minimize -> DONE')
