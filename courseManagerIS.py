#!/usr/bin/env python
# coding=utf-8

from collections import Counter
from random import shuffle
import argparse
import inspect
import codecs
import random
import os
import re


parser = argparse.ArgumentParser(description='This script is used to create course templates in "qdef" format which are used to \
    create new FI.MUNI ROPOT.')
parser.add_argument('-n', '--coursename', required=True, help='Name of the course that will be added into application. e.g. "mchedruli".')
parser.add_argument('-wl', '--wordlist', required=True, help='Path to the corpus file. \
    Each line of this file should be in following format: "word","word frequency" separated by comma. E.g. რომელიც,143927')
parser.add_argument('-tt', '--transcriptiontable', required=True, help='File with transcription rules of every character from specified\
    alphabet including upper case (if alphabet contains such characters). Each line in file should be in following format: "non-latin character,latin character"\
    separated by comma. E.g. ბ,b')
parser.add_argument('-s', '--similar', help='File with similar characters groups, each line represents one group. \
    characters must be separated by comma. E.g. ღ,დ,ფ,თ')
parser.add_argument('-t', '--target', required=True, help='Path to the folder where templates for IS.MUNI ROPOT application will be created. \
    It also creates the folder if it does not already exists. E.g. /home/Documents/Mchedruli/')
parser.add_argument('-l', '--limit', type=int, default=10, help='Only words from corpus with frequency greater or equal to this value \
will be processed. Default value is 10.')

args = parser.parse_args()
name = args.coursename.lower()
wordlist = args.wordlist
table = args.transcriptiontable
limit = args.limit
similar = args.similar
target = args.target


def filterAlphabet(line, alphabet): 
    """This method takes single line from corpus file, which must be formatted like this:
    word,wordcount e.g. მხოლოდ,90098
    so the method can parse the line and check, if all characters in word are present in alphabet.
    If that condition is met, method returns True, otherwise returns False.

    Args:
        line (str): Single line from corpus file.
        alphabet (list): List of chars from specified alphabet.

    Returns:
        bool: True if word contains only characters from specified alphabet, otherwise False.
    """

    line = line.split(",")[0]
    for char in line:
        if char in alphabet:
            continue
        else:
            return False
    
    return True


def checkForUppercase(alphabet):
    """This method takes specified alphabet and checks if it supports upper case.

    Args:
        alphabet (list): List of chars from specified alphabet.

    Returns:
        bool: True if alphabet supports upper case, otherwise False.
    """

    for char in alphabet:
        if char.upper().isupper():
            return True

    return False


def translate(word, translateDict):
    """This method takes a word and transliterate it using transcription rules 
    which are provided in translateDict dictionary.

    Args:
        word (string): Word to be transliterated.
        translateDict (Dictionary): Dictionary in which keys and values represents 1:1 transliteration.

    Returns:
        string: Transliteration of input word.
    """

    translation = ""
    for char in word:
        translation += translateDict.get(char," ")

    return translation


def getTranslateDict():
    """When user runs this script, transcription table file must be provided as one of required arguments.
    Format of such file must be: non-latin char,latin char(s) e.g. ღ,gh
    so the method can parse this file and create a dictionary in which keys and values represents 1:1 transliteration.

    Returns:
        dictionary: Dictionary in which keys and values represents 1:1 transliteration.
    """

    translateDict = {}
    with codecs.open(table, 'r', 'utf-8') as tableFile:
        for line in tableFile:
            line = line.split(',')
            translateDict[line[0]] = line[1].rstrip()

            if line[0].upper().isupper(): 
                translateDict[line[0].upper()] = line[1].rstrip().upper()

    return translateDict


def getSimilarChars():
    """When user runs this script, similar characters file may be provided as one of optional arguments.
    User creates similar character groups and put each group on a new line in file and separate those character by 
    comma. E.g. ჟ,უ,ქ,ჭ,ჰ
    so the method can parse this file and creates list of lists where sublists contain similar characters.

    Returns:
        list: List of lists, sublists contain similar characters.
    """

    similarCharsList = []

    if not similar: # if file with similar character was not provided
        return similarCharsList

    with codecs.open(similar, 'r', 'utf-8') as similarChars:
        for line in similarChars:
            similarCharsSublist = line.split(',')
            similarCharsList.append(similarCharsSublist)

    return similarCharsList


def findAndReplaceSimilarChar(word, optionsList, similarCharsList):
    """This method takes a word and replace a character with similar character if it is possible.
    The method also checks, if new created word is not already in optionsList argument to prevent duplicates.

    Args:
        word (string): Word in which some characters will be replaced with similar characters if possible.
        optionsList (list): List of words, these words will be used to create a level for quiz.
        similarCharsList (list): List of lists, sublists contain similar characters.

    Returns:
        string: Returns word in which a character was replaced by similar one.
        bool: If there is no possibility to replace a character in word, return False.
    """

    word = list(word)
     
    for i in range(len(word)):
        newWord = list(word) # create copy

        for sublist in similarCharsList:
            tmpCharlist = list(sublist) # create copy

            if word[i] in sublist:
                tmpCharlist.remove(word[i])
                
                for char in tmpCharlist:
                    randomChar = random.choice(tmpCharlist)
                    newWord[i] = randomChar
                    
                    if ''.join(newWord) not in optionsList:
                        return ''.join(newWord)

                    else:

                        tmpCharlist.remove(randomChar)

    return False


def getCharLevels(freqArray, filteredWordlist, supportsUppercase):
    """This method creates list of lists where every sublist contains characters from specified alphabet
    and based on this character division into list word groups are created for course levels.

    Args:
        freqArray (list): List of characters sorted by frequency of each character in whole word corpus.
        filteredWordlist (list): List of words which contains character only from specified alphabet.
        supportsUppercase (bool): True if alphabet supports upper case, False otherwise.

    Returns:
            list: List of lists, sublists contain characters from specified alphabet and it forms
            character groups for later creation of course levels.
    """

    charsetIndex = 1
    found = False
    wordsByLengthDict = {}

    while not found and charsetIndex <= len(freqArray):
        wordsByLengthDict = {}
        charset = freqArray[:charsetIndex]

        for word in filteredWordlist:
            if all(char in charset for char in word):
                wordsByLengthDict = wordsByLength(word, wordsByLengthDict)

        for key in wordsByLengthDict.keys():
            if len(wordsByLengthDict[key]) > 9:
                found = True
                break
        charsetIndex += 1

    charLevels = [freqArray[:charsetIndex]] + [freqArray[i:i+3] for i in range(charsetIndex, len(freqArray), 3)]

    # if last char level sublist contains only one char or less, append its value to the previous sublist and remove it 
    if len(charLevels[-1]) <= 1:
        charLevels[-2] += charLevels[-1]
        del charLevels[-1]

    if supportsUppercase:
        result = []
        for level in charLevels:
            result.append(level)
            result.append([char.upper() for char in level])

        return result

    return charLevels



def makeWordOptions(charLevelsWordList, similarCharsList):
    """This method creates list of 3 sublists, each sublist contains 3-4 words suitable for level creation.

    Args:
        charLevelsWordList (list): Word which length will be measured and will be added into dictionary.
        similarCharsList (list): List of lists, sublists contain similar characters.

    Returns:
            list: List of 3 lists, sublists contain words suitable for level creation.
            None: Returns None if it is not possible to create 3 sublists.
    """

    wordsByLengthDict = {}
    selectedOptionsList = []

    for word in charLevelsWordList:
        wordsByLengthDict = wordsByLength(word, wordsByLengthDict)

    wordsByLengthDictKeys = wordsByLengthDict.keys()

    while (len(selectedOptionsList) < 3) and (len(wordsByLengthDictKeys) > 0):
        randomDictKey = random.choice(wordsByLengthDictKeys)
        randomDictValue = wordsByLengthDict[randomDictKey] # list of words of same length
        shuffle(randomDictValue)

        if len(randomDictValue) >= 3: # get 3 words and try to create 4th by swapping similir character
            randomDictValue = randomDictValue[:3]
            for word in randomDictValue:
                trickWord = findAndReplaceSimilarChar(word, randomDictValue, similarCharsList)
                if trickWord:
                    randomDictValue.append(trickWord)
                    break
    
            selectedOptionsList.append(randomDictValue)
            del wordsByLengthDict[randomDictKey][:3] 

        elif len(randomDictValue) == 2: # need to create 2 more words by swapping similar characters
            for word in randomDictValue:
                if len(randomDictValue) < 4 :
                    trickWord = findAndReplaceSimilarChar(word, randomDictValue, similarCharsList)
                    if trickWord:
                        randomDictValue.append(trickWord)

            selectedOptionsList.append(randomDictValue)
            wordsByLengthDictKeys.remove(randomDictKey)

        else:
            wordsByLengthDictKeys.remove(randomDictKey)
            continue

    if len(selectedOptionsList) == 3:
        return selectedOptionsList

    else:
        return None



def wordsByLength(word, dictionary):
    """This method takes a word and dictionary, measure a length of the word and adds it into dictionary,
    where keys are lengths and values are words of such length.

    Args:
        word (string): Word which length will be measured and will be added into dictionary.
        dictionary (Dictionary): Dictionary where keys are lengths and values are words of such length.

    Returns:
        Dictionary: Returns dictionary where keys are lengths and values are words of such length.
    """

    length = len(word)

    if dictionary.has_key(length):
        dictionary[length].append(word)
    
    else:
        dictionary[length] = [word]

    return dictionary


def wordsByLevel(word, charLevels, dictionary):
    """This method takes a word, charLevels and dictionary, and determinate a level that is suitable for the word
    based on characters which is word made of, add that word to the dictionary and return the dictionary.

    Args:
        word (string): Word which length will be measured and will be added into dictionary.
        charLevels (list): List of lists, sublists contain characters from specified alphabet.
        dictionary (Dictionary): Keys are levels and values are list of words suitable for such level.

    Returns:
        Dictionary: Returns dictionary where keys are levels and values are list of words suitable for such level.
    """

    currentIndex = 1 # cannot be 0 because of slicing below

    while currentIndex <= len(charLevels):
        subset = [j for i in charLevels[:currentIndex] for j in i]

        if all(letter in subset for letter in word):
            if dictionary.has_key(currentIndex):
                dictionary[currentIndex].append(word)

            else:
                dictionary[currentIndex] = [word]

            break
        else:
            currentIndex += 1

    return dictionary


def generateLevel(display, translateDict, options, filename):
    """This method takes a word made of non-latin character, transliteration dictionary and list of words in latin alphabet
    and creates single question for IS.MUNI ROPOT which is afterwards written/appended to template file.

    Args:
        display (string): Non-latin alphabet word which will be displayed to user to choose correct transliteration.
        translateDict (Dictionary): Dictionary in which keys and values represents 1:1 transliteration.
        options (list): List of words suitable for level creation.
        filename (string): Name of file where question for IS.MUNI ROPOT will be written/appended to.
    """

    transcriptedOptions = []
    correctAnswer = translate(display,translateDict)
    
    for option in options:
        transcriptedOptions.append(translate(option, translateDict))

    transcriptedOptions.remove(correctAnswer)

    with codecs.open(os.path.join(target,filename), 'a', "utf-8") as testTemplate:
        testTemplate.write(u"Vyberte správnou transkripci slova: " + display + "\n")
        
        for i in range(len(transcriptedOptions)):
            testTemplate.write("\t:r" + str(i) + " " + transcriptedOptions[i] + "\n")

        testTemplate.write("\t:r" + str(len(transcriptedOptions)) + " " + correctAnswer + "\n")
        testTemplate.write(":r" + str(len(transcriptedOptions)) + " ok" + "\n")
        testTemplate.write("--\n")


def generateLevelAlternative(wordList, translateDict, similarCharsList, filename):
    """This method takes a word made of latin character, transliteration dictionary and list of words in non-latin alphabet
    and creates single question for IS.MUNI ROPOT which is afterwards written/appended to template file.

    Args:
        wordList (list): List of words suitable for level creation.
        translateDict (Dictionary): Dictionary in which keys and values represents 1:1 transliteration.
        similarCharsList (list): List of lists, sublists contain similar characters.
        filename (string): Name of file where question for IS.MUNI ROPOT will be written/appended to.
    """

    wordList = wordList[:3]
    levelDict = {}

    for word in wordList:
        trickWord = findAndReplaceSimilarChar(word, wordList, similarCharsList)
        if trickWord:
            wordList.append(trickWord)
            break

    for word in wordList:
        display = translate(word, translateDict)

        if re.match('^[a-zA-Z]+$', display) is not None: # check if word contains only latin alphabet characters
            levelDict["display"] = display
            levelDict["correct"] = word
            levelDict["options"] = wordList
            break

    if not levelDict: # if levelDict is empty, return False to prevent creation of empty level
        return None
    
    correctAnswer = levelDict["correct"]
    display = levelDict["display"]
    wordList.remove(correctAnswer)

    with codecs.open(os.path.join(target,filename), 'a', "utf-8") as testTemplate:
        testTemplate.write(u"Vyberte správnou transkripci slova: " + display + "\n")
        
        for i in range(len(wordList)):
            testTemplate.write("\t:r" + str(i) + " " + wordList[i] + "\n")

        testTemplate.write("\t:r" + str(len(wordList)) + " " + correctAnswer + "\n")
        testTemplate.write(":r" + str(len(wordList)) + " ok" + "\n")
        testTemplate.write("--\n")



def generateUppercaseLevel(display, translateDict, wordList, filename):
    """This method takes a word made of non-latin character, transliteration dictionary and list of words in latin alphabet
    and creates single question for IS.MUNI ROPOT which is afterwards written/appended to template file.

    Args:
        display (string): Non-latin alphabet word which will be displayed to user to choose correct transliteration.
        translateDict (Dictionary): Dictionary in which keys and values represents 1:1 transliteration.
        wordList (list): List of words suitable for level creation.
        filename (string): Name of file where question for IS.MUNI ROPOT will be written/appended to.
    """

    transcriptedOptions = []
    for word in wordList:
        transcriptedOptions.append(translate(word, translateDict))

    levelDict = {}
    display = display.upper()
    correctAnswer = translate(display,translateDict).upper()
    options = [option.upper() for option in transcriptedOptions]

    options.remove(correctAnswer)

    with codecs.open(os.path.join(target,filename), 'a', "utf-8") as testTemplate:
        testTemplate.write(u"Vyberte správnou transkripci slova: " + display + "\n")
        
        for i in range(len(options)):
            testTemplate.write("\t:r" + str(i) + " " + options[i] + "\n")

        testTemplate.write("\t:r" + str(len(options)) + " " + correctAnswer + "\n")
        testTemplate.write(":r" + str(len(options)) + " ok" + "\n")
        testTemplate.write("--\n")

    return levelDict


def generateEndOfQuiz(filename):
    """This method takes a name of file and appends '++' to the very end of the file which is recognised as
    end of template by IS.MUNI ROPOT parser.

    Args:
        filename (string): Name of file where end of template for IS.MUNI ROPOT will be appended to its very end.
    """

    with codecs.open(os.path.join(target,filename), 'a', "utf-8") as testTemplate:
        testTemplate.write("++")


def generateISTemplates(course, wordlist, charLevels, translateDict, similarCharsList, supportsUppercase):
    """This method creates multiple files in target folder specified by user as one of script arguments. Each file
    represents a template for a single IS.MUNI ROPOT in 'qdef' format.

    Args:
        course (string): Name of the course.      
        wordlist (list): List of words suitable for level creation.
        charLevels (list): List of lists, sublists contain characters from specified alphabet.
        translateDict (Dictionary): Dictionary in which keys and values represents 1:1 transliteration.
        similarCharsList (list): List of lists, sublists contain similar characters.
        supportsUppercase (bool): True if alphabet supports upper case, False otherwise.
    """

    levelsDict= {}
    stageByNumber = 1 # represents key of wordsByLevelDict to get wordlist value
    wordsByLengthDict = {}
    wordsByLevelDict = {}
    swappedTranslateDict = dict((v,k) for k,v in translateDict.iteritems()) # Keys are latin, values non-latin

    for word in wordlist:
        wordsByLengthDict = wordsByLength(word, wordsByLengthDict)
        wordsByLevelDict = wordsByLevel(word, charLevels, wordsByLevelDict)

    for stage in charLevels:

        if not wordsByLevelDict.has_key(stageByNumber): # Skip the uppercase stages in charLevels
            stageByNumber += 1
            continue

        charLevelsWordList = wordsByLevelDict[stageByNumber] # contains list of words suitable for current stage
        selectedOptions = makeWordOptions(charLevelsWordList, similarCharsList) # List of 3 sublists containing options or None

        if selectedOptions is not None:

            for i in range(len(selectedOptions)):
                    generateLevel(random.choice(selectedOptions[i]), translateDict, selectedOptions[i], name+str(stageByNumber)+".qdef")
                    generateLevelAlternative(selectedOptions[i], translateDict, similarCharsList, name+str(stageByNumber)+".qdef")

                    if supportsUppercase:
                        generateUppercaseLevel(random.choice(selectedOptions[i]), translateDict, selectedOptions[i], name+str(stageByNumber)+".qdef")

        generateEndOfQuiz(name+str(stageByNumber)+".qdef")
        stageByNumber += 1

    # generate practice levels
    for i in range(30):
        selectedWords = wordsByLengthDict[random.choice(wordsByLengthDict.keys())]
        if len(selectedWords) >= 3:
            quizRandomSelection = random.sample(selectedWords,3) # take random 4 items from list

            for word in quizRandomSelection:
                trickWord = findAndReplaceSimilarChar(word, quizRandomSelection, similarCharsList)
                if trickWord:
                    quizRandomSelection.append(trickWord)
                    break

            generateLevel(quizRandomSelection[0], translateDict, quizRandomSelection, name+"Practice.qdef")
            generateLevelAlternative(quizRandomSelection, translateDict, similarCharsList, name+"Practice.qdef")

            if supportsUppercase:
                generateUppercaseLevel(quizRandomSelection[0], translateDict, quizRandomSelection, name+"Practice.qdef")

    generateEndOfQuiz(name+"Practice.qdef")


def main():

    count = Counter()
    translateDict = getTranslateDict()
    similarCharsList = getSimilarChars()
    alphabet = translateDict.keys()
    filteredWordlist = []

    with codecs.open(wordlist,"r","utf-8") as wordlistFile:
        for line in wordlistFile:
            word = line.split(',')[0].lower()
            wordFreq = line.split(',')[-1]

            if not filterAlphabet(line, alphabet):
                continue
            try:
                wordFreq = int(wordFreq)

                if wordFreq < limit:
                    break

            except ValueError:
                pass

            filteredWordlist.append(word)
            count += Counter(word.strip())
            for char in word:
                count[char] += int(wordFreq)

        supportsUppercase = checkForUppercase(alphabet) # True if alphabet has uppercase characters, otherwise False
        freqArray = sorted(count, key=count.get, reverse=True)
        charLevels = getCharLevels(freqArray, filteredWordlist, supportsUppercase)

        #Check for destination folder, create if not exists
        if not os.path.exists(target):
            os.makedirs(target)
            print "Destination folder was created in:", target

        generateISTemplates(name, filteredWordlist, charLevels, translateDict, similarCharsList, supportsUppercase)



if __name__ == "__main__":
    main()