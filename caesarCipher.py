"""

Author: Maksymilian Górski
Index number:259396
Course: Skryptowe Języki Programowania - Środa 11:15

"""

from time import time
from math import ceil
from random import randint

class CaesarCipher:

	cache = []
	
	def __init__(self, inputText_ = "", key_ = 0, dictionaryPath_="dict.txt", howManyBestDecryptionsToShow_ = 3, percentageToCheck_ = 100):
		self.inputText = inputText_
		self.key = int(key_) % 26
		self.dictionaryPath = dictionaryPath_
		self.howManyBestDecryptionsToShow = int(howManyBestDecryptionsToShow_)
		self.percentageToCheck = int(percentageToCheck_)

		CaesarCipher.updateCacheFromFile()

	def getInputText(self):
		return self.inputText

	def setInputText(self, inputText_ = ""):
		self.inputText = inputText_

	def getKey(self):
		return self.key

	def setKey(self, key_ = 0):
		self.key = key_ % 26

	def getHowManyBestDecryptions(self):
		return self.howManyBestDecryptionsToShow

	def setHowManyBestDecryptions(self, howManyBestDecryptionsToShow_ = 3):
		self.howManyBestDecryptionsToShow = howManyBestDecryptionsToShow_

	def getPercentageToCheck(self):
		return self.percentageToCheck

	def setPercentageToCheck(self, percentageToCheck_ = 100):
		self.percentageToCheck = percentageToCheck_

	@classmethod
	def saveCacheToFile(cls, outputFilePath="cache.txt"):
		cacheFileWordList = []
		for word in open(outputFilePath, "rt"):
			word = word.replace("\n", "")
			if word == "":
				continue
			cacheFileWordList.append(word)

		f = open(outputFilePath, "wt")
		for word in cls.cache:
			if word not in cacheFileWordList:
				line = word + "\n"
				f.write(line)
		f.close()

	@classmethod
	def updateCacheFromFile(cls, inputFilePath="cache.txt"):
		for word in open(inputFilePath):
			word = word.replace("\n", "")
			if word not in cls.cache:
				cls.cache.append(word)

	@classmethod
	def clearCacheFile(cls, cacheFilePath="cache.txt"):
		open(cacheFilePath, "w").close()


	def __str__(self):
		txt = ""

		txt += "-" * 20 +  "\n"
		txt += "Input Text:\n"
		if self.inputText == "":
			txt += "*Not inserted*\n"
		else:
			txt += f"{self.inputText}\n"
		
		txt += f"Key: {self.key}\n"

		txt += "-" * 20 +  "\n"
		return txt

	def getInputTextOrdList(self):
		ordList = []
		for char in self.inputText:
			ordList.append(ord(char))

		return ordList

	def shift(self, key = None):

		shiftedText = ""

		if key == None:
			key = self.key

		for char in self.inputText:

			charCode = ord(char)
			shiftedChar = ""

			if charCode >= ord("a") and charCode <= ord("z"):
				shiftedChar = chr( ((charCode - ord("a") ) + key ) % 26 + ord("a") )

			elif charCode >= ord("A") and charCode <= ord("Z"):
				shiftedChar = chr( ((charCode - ord("A") ) + key ) % 26 + ord("A") )

			else:
				shiftedChar = char

			shiftedText += shiftedChar

		return shiftedText

	def shiftAll(self):

		keys = range(26)
		resultList = []

		for key in keys:

			shiftedText = ""		

			for char in self.inputText:

				charCode = ord(char)

				if charCode >= ord("a") and charCode <= ord("z"):
					shiftedChar = chr( ((charCode - ord("a") ) - key ) % 26 + ord("a") )

				elif charCode >= ord("A") and charCode <= ord("Z"):
					shiftedChar = chr( ((charCode - ord("A") ) - key ) % 26 + ord("A") )

				else:
					shiftedChar = char

				shiftedText += shiftedChar

			resultList.append( (key, shiftedText) )

		return resultList


	def calculateConfidence(self, shiftedText=None):

		if shiftedText == None:
			shiftedText = self.inputText

		punctuationMarks = "\",./?!:;|[]{}()-=_+!@#$%^&*\\/"
		for mark in punctuationMarks:
			if mark in shiftedText:
				shiftedText = shiftedText.replace(mark, "")

		words = shiftedText.split(" ")

		indicesToCheck = None
		if self.percentageToCheck == 100:
			indicesToCheck = [i for i in range(len(words))]
		else:
			indicesToCheck = self.generateIndicesToCheck(len(words))

		foundCount = 0

		for i in indicesToCheck:
			word = words[i]

			found = False

			for value in CaesarCipher.cache:
				if word.lower() == value.lower():
					foundCount += 1
					found = True
					break
			
			if found:
				continue

			for value in open(self.dictionaryPath, "rt"):
				if word.lower() == value.replace("\n", "").lower():
					if word not in CaesarCipher.cache:
						CaesarCipher.cache.append(word.lower())
					foundCount += 1
					found = True
					break
		

		# confidence is given in %
		return foundCount/len(indicesToCheck) * 100

	def generateIndicesToCheck(self, wordsNumber):
		wordsToCheck = ceil(wordsNumber/100 * self.percentageToCheck)

		indices = [i for i in range(wordsNumber)]
		result = []
		while wordsToCheck > 0:
			randomIndex = randint(0,len(indices)-1)
			result.append(randomIndex)
			del indices[randomIndex]
			wordsToCheck -= 1
		
		return result


	def findBestDecryption(self, diplayInfo = False):

		# (key, shiftedText)
		shiftedMessageList = self.shiftAll()
		keyOrder = []

		startTime = time()

		for i in range(len(shiftedMessageList)):
			###print(f"Checking key: {key}")

			key = shiftedMessageList[i][0]
			message = shiftedMessageList[i][1]
			confidence = self.calculateConfidence(message)
			record = (key, confidence, message)
			
			if i == 0:
				keyOrder.append(record)
				continue

			for j in range(len(keyOrder)):
				if record[1] >= keyOrder[j][1]:
					keyOrder.insert(j, record)
					break

				if j == len(keyOrder)-1:
					keyOrder.append(record)

		
		endTime = time()


		bestDecryption = keyOrder[0][2]
		resultTxt = ""
		for i in range(self.howManyBestDecryptionsToShow):
			resultTxt += f"No {i+1}:\tKey: {keyOrder[i][0]}\tConfidence: {keyOrder[i][1]:.2f}%\n{keyOrder[i][2]}\n\n"

		CaesarCipher.saveCacheToFile()
		
		if diplayInfo != False:
			print(f"\nTotal confidence calculation took: {endTime - startTime}[s]...\nWord percentage to check: {self.percentageToCheck}\n")
		
		return (resultTxt,bestDecryption)

	def printBestDecryption(self, flag=False):
		print(self.findBestDecryption(flag)[0])

def testDecryption(inputText, key, shiftedText):

	shiftResult = CaesarCipher(shiftedText, -key).shift()
	testSuccessful = shiftResult == inputText
	
	if testSuccessful == False:
		print(f"Test failed!")
		print(f"Expected:\n{inputText}")
		print(f"Decrypted:\n{shiftResult}\n")

	return testSuccessful

def testFromFile(inputFilePath = "input.txt"):
	success = 0
	fail= 0

	for line in open(inputFilePath, "rt"):
		line = line.replace("\n", "")

		line = line.split("\t")

		testSuccessful = testDecryption(line[0], int(line[1]), line[2])

		if testSuccessful:
			success += 1
		else:
			fail += 1

	print(f"Test summary:\nSuccess: {success} \tFail: {fail}")

if __name__ == "__main__":
	CaesarCipher.updateCacheFromFile()

	inputText = "Uijt jt ufo qfsdfou mvdl Gjguffo qfsdfou dpodfousbufe qpxfs pg xjmm Gjwf qfsdfou qmfbtvsf Gjguz qfsdfou qbjo Boe b ivoesfe qfsdfou sfbtpo up sfnfncfs uif obnf If epfto'u offe ijt obnf vq jo mjhiut If kvtu xbout up cf ifbse xifuifs ju't uif cfbu ps uif njd..."
	key = 12

	cc = CaesarCipher(inputText, key)
	cc.printBestDecryption(True)

	### Test performance for different percentages
	for i in range(10, 110, 10):
		start = time()
		cc.setPercentageToCheck(i)
		cc.printBestDecryption(True)
		end = time()
		print(f"Looptime: {end-start}[s]...")

	### Test shifting on given input file (default "input.txt")
	testFromFile()