#!/usr/bin/env python
# coding=utf-8

from project import db, models
from project.models import User

from collections import Counter
from random import shuffle
import importlib, sys
import subprocess
import argparse
import codecs
import random
import inspect
import types
import json
import re
import os


parser = argparse.ArgumentParser(description='This script is used to add a new course to the Interactive alphabet learning application. \
    Make sure that you provide valid input data (arguments are described below) otherwise the script may fail and then it may require \
    to manually revert last changes made by this faulty run. \
    This script creates folder with course templates in project/templates/courses/<courseName>, modifies database file in project/ folder and \
    it also creates a class for new course in project/models.py file.')
parser.add_argument('-n', '--coursename', required=True, help='Name of the course that will be added into application. e.g. "mchedruli"')
parser.add_argument('-wl', '--wordlist', required=True, help='Path to the corpus file. \
    Each line of this file should be in following format: "word","word frequency" separated by comma. E.g. რომელიც,143927')
parser.add_argument('-tt', '--transcriptiontable', required=True, help='File with transcription rules of every character from specified\
    alphabet including upper case (if alphabet contains such characters). Each line in file should be in following format: "non-latin character,latin character"\
    separated by comma. E.g. ბ,b')
parser.add_argument('-s', '--similar', help='File with similar characters groups, each line represents one group. \
    characters must be separated by comma. E.g. ღ,დ,ფ,თ')
parser.add_argument('-l', '--limit', type=int, default=10, help='Only words from corpus with frequency greater or equal to this value \
will be processed. Default value is 10.')

args = parser.parse_args()
name = args.coursename.lower()
wordlist = args.wordlist
table = args.transcriptiontable
limit = args.limit
similar = args.similar

basedir = os.path.abspath(os.path.dirname(__file__))
modelsFile = os.path.join(basedir,'project','models.py')
templatesDir = os.path.join(basedir,'project', 'templates', 'courses')
destinationFolder = os.path.join(templatesDir, name)

introToLevelMap = {} # Relation between introduction levels and quiz levels

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


def getAlphabet():
    """When user runs this script, transcription table file must be provided as one of required arguments.
    Format of such file must be: non-latin char,latin char(s) e.g. ღ,gh
    so the method can parse this file and create list of non-latin characters from specified alphabet.

    Returns:
        list: List of character from specified alphabet.
    """

    alphabet = []
    with codecs.open(table, 'r', 'utf-8') as tableFile:
        for line in tableFile:
            alphabet.append(line.split(',')[0])

    return alphabet


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


def getCharStats(charLevels):
    """This method takes a list of lists which represents character levels and returns
    dictionary template representing character statistics to be stored into database and
    updated later on with real data.

    Args:
        charLevels (list): List of lists, sublists contain characters from specified alphabet and it forms
            character groups.

    Returns:
        dict: Character statistics dictionary.
    """

    charStats = {}

    for i in range(len(charLevels)):
        for char in charLevels[i]:
            charStats[char] = {}
            charStats[char]["chapter"] = i + 1
            charStats[char]["correct"] = 0
            charStats[char]["total"] = 0
            charStats[char]["rate"] = ''

    return charStats


def getChapterProgress():
    """This method creates dictionary which stores data about each chapter in course.
    This dictionary suites as a default template which will be stored into database and updated
    during course progress with real user data.

    Returns:
        dict: Chapter progress dictionary.
    """

    chapterProgress = {}

    for chapter in introToLevelMap:
        chapterProgress[chapter] = {}
        chapterProgress[chapter]["status"] = "Not started"
        chapterProgress[chapter]["progress"] = {'current':0, 'total':(introToLevelMap[chapter][1] - introToLevelMap[chapter][0] + 1)}
        chapterProgress[chapter]["correct"] = {'subtotal':0, 'correct':0, 'rate':''}
        chapterProgress[chapter]["repeatLevel"] = introToLevelMap[chapter][0]

    return chapterProgress



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
            similarCharsSublist = line.strip().split(',')
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

        # Merge last two sublists together so the final level contains both lowercase and uppercase characters
        #result = result[:len(result) - 2] + [result[len(result) - 2] + result[len(result) - 1]]

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
    selectedOptionList = []

    for word in charLevelsWordList:
        wordsByLengthDict = wordsByLength(word, wordsByLengthDict)

    wordsByLengthDictKeys = wordsByLengthDict.keys()

    while (len(selectedOptionList) < 5) and (len(wordsByLengthDictKeys) > 0):
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
    
            selectedOptionList.append(randomDictValue)
            del wordsByLengthDict[randomDictKey][:3] 

        elif len(randomDictValue) == 2: # need to create 2 more words by swapping similar characters
            for word in randomDictValue:
                if len(randomDictValue) < 4 :
                    trickWord = findAndReplaceSimilarChar(word, randomDictValue, similarCharsList)
                    if trickWord:
                        randomDictValue.append(trickWord)

            selectedOptionList.append(randomDictValue)
            wordsByLengthDictKeys.remove(randomDictKey)

        else:
            wordsByLengthDictKeys.remove(randomDictKey)
            continue

    if len(selectedOptionList) >= 3:
        return selectedOptionList

    else:
        return None


def generateIntroJson(course, charLevels, translateDict):
    """This method creates JSON template which contains character introduction.

    Args:
        course (string): Name of the course.      
        charLevels (list): List of lists, sublists contain characters from specified alphabet.
        translateDict (Dictionary): Dictionary in which keys and values represents 1:1 transliteration.
    """

    introductionLevel = 1
    levelsDict = {}

    for level in charLevels:
        levelsDict[introductionLevel] = {}

        for character in level:
            levelsDict[(introductionLevel)][character] = translate(character, translateDict)

        introductionLevel += 1

    jsonized = json.dumps(levelsDict, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
    
    with codecs.open(destinationFolder + '/intro.json',"w", "utf-8") as out:
        out.write(jsonized)

    print "Introduction levels file has been created in:",destinationFolder + '/intro.json'


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


def generateLevel(display, translateDict, options):
    """This method takes a word made of non-latin character, transliteration dictionary and list of words in latin alphabet
    and creates dictionary which represents one level in quiz.

    Args:
        display (string): Non-latin alphabet word which will be displayed to user to choose correct transliteration.
        translateDict (Dictionary): Dictionary in which keys and values represents 1:1 transliteration.
        options (list): List of words suitable for level creation.

    Returns:
        Dictionary: Returns dictionary where keys are levels and values are list of words suitable for such level.
    """

    shuffledOptions = []
    for option in options:
        shuffledOptions.append(translate(option, translateDict))

    shuffle(shuffledOptions)
    levelDict = {}
    levelDict["display"] = display
    levelDict["correct"] = translate(display,translateDict)
    levelDict["options"] = shuffledOptions

    return levelDict


def generateLevelAlternative(wordList, translateDict, similarCharsList):
    """This method takes a word made of latin character, transliteration dictionary and list of words in non-latin alphabet
    and creates dictionary which represents one level in quiz.

    Args:
        wordList (list): List of words suitable for level creation.
        translateDict (Dictionary): Dictionary in which keys and values represents 1:1 transliteration.
        similarCharsList (list): List of lists, sublists contain similar characters.

    Returns:
        Dictionary: Returns dictionary where keys are levels and values are list of words suitable for such level.
        bool: It may happen that this operation is not succesful and level is not created, in this scenario returns False.
    """

    wordList = wordList[:3]
    shuffle(wordList)
    levelDict = {}

    for word in wordList:
        trickWord = findAndReplaceSimilarChar(word, wordList, similarCharsList)
        if trickWord:
            break

    for word in wordList:
        translatedWord = translate(word, translateDict)

        if re.match('^[a-zA-Z]+$', translatedWord) is not None: # check if word contains only latin alphabet characters
            if trickWord:
                wordList.append(trickWord)

            levelDict["display"] = translatedWord
            levelDict["correct"] = word
            levelDict["options"] = wordList
            break

    if not levelDict: # if levelDict is empty, return False to prevent creation of empty level
        return False
    
    return levelDict


def generateUppercaseLevel(display, translateDict, options):
    """This method takes a word made of non-latin character, transliteration dictionary and list of words in latin alphabet
    and creates dictionary which represents one level in quiz.

    Args:
        display (string): Non-latin alphabet word which will be displayed to user to choose correct transliteration.
        translateDict (Dictionary): Dictionary in which keys and values represents 1:1 transliteration.
        options (list): List of words suitable for level creation.

    Returns:
        Dictionary: Returns dictionary where keys are levels and values are list of words in upper case suitable for such level.
    """

    shuffledOptions = []
    for option in options:
        shuffledOptions.append(translate(option, translateDict))

    shuffle(shuffledOptions)
    levelDict = {}
    levelDict["display"] = display.upper()
    levelDict["correct"] = translate(display,translateDict).upper()
    levelDict["options"] = [option.upper() for option in shuffledOptions]

    return levelDict


def generateLevelJson(course, wordlist, charLevels, translateDict, similarCharsList, supportsUppercase):
    """This method creates JSON template which contains levels for course.

    Args:
        course (string): Name of the course.      
        wordlist (list): List of words suitable for level creation.
        charLevels (list): List of lists, sublists contain characters from specified alphabet.
        translateDict (Dictionary): Dictionary in which keys and values represents 1:1 transliteration.
        similarCharsList (list): List of lists, sublists contain similar characters.
        supportsUppercase (bool): True if alphabet supports upper case, False otherwise.

    Returns:
        int: Number of levels.
    """

    levelsDict= {}
    level = 1
    stageByNumber = 1 # represents key of wordsByLevelDict to get wordlist value
    wordsByLengthDict = {}
    wordsByLevelDict = {}
    swappedTranslateDict = dict((v,k) for k,v in translateDict.iteritems()) # Keys are latin, values non-latin

    for word in wordlist:
        wordsByLengthDict = wordsByLength(word, wordsByLengthDict)
        wordsByLevelDict = wordsByLevel(word, charLevels, wordsByLevelDict)

    for stage in charLevels:

        if not wordsByLevelDict.has_key(stageByNumber): # Skip the uppercase stages in charLevels
            break

        charLevelsWordList = wordsByLevelDict[stageByNumber] # contains list of words suitable for current stage
        selectedOptions = makeWordOptions(charLevelsWordList, similarCharsList) # List of 3 sublists containing options or None

        if selectedOptions is not None:

            firstLevel = level

            for i in range(len(selectedOptions)):
                    levelsDict[level] = generateLevel(random.choice(selectedOptions[i]), translateDict, selectedOptions[i])
                    level += 1

                    alternativeLevel = generateLevelAlternative(selectedOptions[i], translateDict, similarCharsList)
                    if alternativeLevel: # alternative level might be empty when mapping latin character to non-latin is not 1:1
                        levelsDict[level] = alternativeLevel
                        level += 1

            introToLevelMap[stageByNumber] = (firstLevel, level - 1) # Relation of character introduction levels and quiz levels

        stageByNumber += 1

        if supportsUppercase and selectedOptions is not None:
            
            firstLevel = level
            for i in range(len(selectedOptions)):

                        levelsDict[level] = generateUppercaseLevel(random.choice(selectedOptions[i]), translateDict, selectedOptions[i])
                        level += 1

            introToLevelMap[stageByNumber] = (firstLevel, level - 1)
            stageByNumber += 1

    for i in range(30):
        selectedWords = wordsByLengthDict[random.choice(wordsByLengthDict.keys())]
        if len(selectedWords) >= 3:
            quizRandomSelection = random.sample(selectedWords,3) # take random 4 items from list

            for word in quizRandomSelection:
                trickWord = findAndReplaceSimilarChar(word, quizRandomSelection, similarCharsList)
                if trickWord:
                    quizRandomSelection.append(trickWord)
                    break

            levelsDict[level] = generateLevel(random.choice(quizRandomSelection), translateDict, quizRandomSelection)
            level += 1

            alternativeLevel = generateLevelAlternative(quizRandomSelection, translateDict, similarCharsList)
            if alternativeLevel: # alternative level might be empty when mapping latin character to non-latin is not 1:1
                levelsDict[level] = alternativeLevel
                level += 1

            if supportsUppercase:
                levelsDict[level] = generateUppercaseLevel(random.choice(quizRandomSelection), translateDict, quizRandomSelection)
                level += 1

    level -= 1
    introToLevelMap[stageByNumber - 1] = (introToLevelMap[stageByNumber - 1][0], level)

    dicToJson = json.dumps(levelsDict,sort_keys=True,ensure_ascii=False, indent=4, separators=(',', ': '))
    with codecs.open(destinationFolder + '/level.json',"w", "utf-8") as out:
        out.write(dicToJson)

    print "Levels file has been created in:", destinationFolder + '/level.json'

    return level


def class_for_name(className):
    """This method return Class from Models.py file based on string name of such class.

    Args:
        className (string): Name of class in Models.py file.

    Returns:
        Class: Class from Models.py file.
    """

    reload(models)
    module = importlib.import_module("project.models")
    clazz = getattr(module, className)

    return clazz


def migrateUsers(courseClass):
    """This method takes all existing users in database and migrates them to the specific course table
    accesible by class from Models.py, where every course table has its own class representation.

    Args:
        courseClass (Class): Class from models.py file.
    """

    userEmails = db.session.query(User.email).all()

    for email in userEmails:
        registerCourse = courseClass(email = email[0])
        db.session.add(registerCourse)

    db.session.commit()


def appendModels(numberOfLevels, characterStatistics, chapterProgress):
    """This method appends new class to Models.py file, which is very important to Flask application structure.
    Also when migration is invoked by Flask-migrate and Alembic tools, the database is affected by changes done in 
    Models.py file so appending new class representing specific course to this file results in creating table in
    database for this course and helps to automate this process.

    Args:
        numberOfLevels (int): The number of levels in specific course.
        characterStatistics (dict): 
        chapterProgress (dict):
    """

    numberOfLevels = str(numberOfLevels)

    with open (modelsFile, 'a') as models:
        models.write("\n\n")
        models.write("class " + name.capitalize() + "(db.Model):\n")
        models.write('\t__tablename__ = "' + name + '"\n')
        models.write("\t__table_args__ = {'extend_existing':True}\n\n")
        models.write("\temail = db.Column(db.String, primary_key=True, unique=True, nullable=False)\n")
        models.write("\tlevel = db.Column(db.Integer,nullable=False, default=1)\n")
        models.write("\tmaxLevel = db.Column(db.Integer, nullable=False, default=" + numberOfLevels + ")\n")
        models.write("\tintroLevel = db.Column(db.Integer,nullable=False, default=1)\n")
        models.write("\tintroToLevelMap = db.Column(db.String, nullable=False, default='" + str(introToLevelMap) + "')\n")
        models.write('\tcharStats = db.Column(db.String, nullable=False, default="' + str(characterStatistics) + '")\n')
        models.write('\tchapterProgress = db.Column(db.String, nullable=False, default="' + str(chapterProgress) + '")\n')
        models.write("\tanswersHistory = db.Column(db.String, nullable=False, default='{}')\n")
        models.write("\twrongAnswers = db.Column(db.String, nullable=False, default='[]')\n\n")
        models.write('\tdef __init__(self, email, wrongAnswers="[]", answersHistory="{}", level=1, introLevel=1, maxLevel=' + \
            numberOfLevels + ', introToLevelMap="' + str(introToLevelMap) + '",\\\n\t\t\t\tcharStats="' + str(characterStatistics) + \
             '",\\\n\t\t\t\tchapterProgress="' + str(chapterProgress) + '"):\n')
        models.write("\t\tself.email = email\n")
        models.write("\t\tself.level = level\n")
        models.write("\t\tself.introLevel = introLevel\n")
        models.write("\t\tself.maxLevel = maxLevel\n")
        models.write("\t\tself.introToLevelMap = introToLevelMap\n")
        models.write("\t\tself.charStats = charStats\n")
        models.write("\t\tself.chapterProgress = chapterProgress\n")
        models.write("\t\tself.wrongAnswers = wrongAnswers\n")
        models.write("\t\tself.answersHistory = answersHistory\n\n")
        models.write("\tdef get_level(self):\n")
        models.write("\t\treturn self.level\n\n")
        models.write("\tdef get_introLevel(self):\n")
        models.write("\t\treturn self.introLevel\n\n")
        models.write("\tdef get_maxLevel(self):\n")
        models.write("\t\treturn self.maxLevel\n\n")
        models.write("\tdef get_introToLevelMap(self):\n")
        models.write("\t\treturn self.introToLevelMap\n\n")
        models.write("\tdef get_charStats(self):\n")
        models.write("\t\treturn self.charStats\n\n")
        models.write("\tdef get_chapterProgress(self):\n")
        models.write("\t\treturn self.chapterProgress\n\n")
        models.write("\tdef get_wrongAnswers(self):\n")
        models.write("\t\treturn self.wrongAnswers\n\n")
        models.write("\tdef get_answersHistory(self):\n")
        models.write("\t\treturn self.answersHistory\n\n")


def main():

    print "Starting automated course integration procedure"
    print "This operation may take several minutes to complete"

    count = Counter()
    translateDict = getTranslateDict()
    similarCharsList = getSimilarChars()
    alphabet = translateDict.keys()
    filteredWordlist = []

    with codecs.open(wordlist,"r","utf-8") as wordlistFile:

        print "Analyzing corpus file..."

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

        # Check for destination folder, create if not exists
        if not os.path.exists(destinationFolder):
            os.makedirs(destinationFolder)
            print "Destination folder was created in:", destinationFolder

        generateIntroJson(name, charLevels, translateDict)
        numberOfLevels = generateLevelJson(name, filteredWordlist, charLevels, translateDict, similarCharsList, supportsUppercase)
        characterStatistics = getCharStats(charLevels)
        chapterProgress = getChapterProgress()
        appendModels(numberOfLevels, characterStatistics, chapterProgress)
        subprocess.call(['python', 'manage.py', 'db', 'migrate'])
        subprocess.call(['python', 'manage.py', 'db', 'upgrade'])
        courseClass = class_for_name(name.capitalize())
        migrateUsers(courseClass)
        print "Operation was successful."   



if __name__ == "__main__":
    main()