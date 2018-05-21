from project.models import *
from project import db, models
from .forms import  QuizForm

from flask import render_template, Blueprint, url_for, \
    redirect, flash, request
from flask_login import login_required, current_user
from operator import itemgetter
from bisect import insort, bisect_left
from datetime import datetime
from random import randint
from math import floor
import ast
import os
import json
import importlib
import inspect


main_blueprint = Blueprint('main', __name__,)

basedir = os.path.abspath(os.path.dirname(__file__))
projectDir = os.path.split(basedir)[0]
modelsFile = os.path.join(projectDir, 'models.py')
templatesDir = os.path.join(projectDir, 'templates', 'courses')


def loadIntroTemplates():

    introTemplatesDict = {}
    courses = getCoursesFromModels()

    for course in courses:
        with open(os.path.join(templatesDir, course.lower(), 'intro.json')) as jsondata:
            data = json.load(jsondata)
            introTemplatesDict[course.lower()] = data

    return introTemplatesDict


def loadLevelTemplates():

    levelTemplatesDict = {}
    courses = getCoursesFromModels()

    for course in courses:
        with open(os.path.join(templatesDir, course.lower(), 'level.json')) as jsondata:
            data = json.load(jsondata)
            levelTemplatesDict[course.lower()] = data

    return levelTemplatesDict  


def getCoursesFromModels():
    """This method imports and inspects Models.py file and adds name of its classes to the list.
    User class is skipped so it is not added into list of courses.

    Returns:
        list: List of string names of classes in Models.py file.
    """

    coursesList = []
    mod = importlib.import_module('project.models')
    for name, obj in inspect.getmembers(mod, inspect.isclass):
        if name != "User":
            coursesList.append(name.lower())

    coursesList.sort()

    return coursesList


def class_for_name(moduleName, className):
    """This method imports module using moduleName argument and then it gets its class representation using
    argument className.

    Args:
        moduleName (str): Name of the module.
        className (list): Name of the class.

    Returns:
        class: Returns class from module.
    """

    module = importlib.import_module(moduleName)
    clazz = getattr(module, className)

    return clazz


def getPercentage(value, total):
    """This method is used to get percentage progress of a course.

    Args:
        value (int): Current level of a course.
        total (int): Number of levels in a course.

    Returns:
        int: Return percentage progress of a course.
    """

    return floor(100 * float(value)/float(total))


def setCharStats(charStatsDict, words, correct):
    """This method selects non-latin word out of 'words' parameter and updates
    character statistic dictionary based on valueof parameter 'correct'.

    Args:
        charStatsDict (dict): Characters statistics.
        words (tuple): Tuple which contains two string words.
        correct (bool): True if answer was aswered correctly, false otherwise.

    Returns:
        string: Return String representation of characters statistics dictionary.
    """

    alphabet = charStatsDict.keys()

    if len(words) == 2:

        if all(char in alphabet for char in words[0]):
            candidate = words[0]

        elif all(char in alphabet for char in words[1]):
            candidate = words[1]

        else:
            return charStatsDict

    for char in candidate:
        charStatsDict[char]["total"] += 1

        if correct:
            charStatsDict[char]["correct"] += 1

        charStatsDict[char]['rate'] = getPercentage(charStatsDict[char]["correct"], charStatsDict[char]["total"])

    return str(charStatsDict)


def resetCharStats(charStatsDict):
    """This method resets user's characters statistics.

    Args:
        charStatsDict (dict): Characters statistics.

    Returns:
        string: Return String representation of characters statistics dictionary.
    """  

    for char in charStatsDict.keys():
        charStatsDict[char]['rate'] = ''
        charStatsDict[char]['correct'] = 0
        charStatsDict[char]['total'] = 0

    return str(charStatsDict)


def setChapterProgress(chapterProgressDict, chapter, correct, chapterToLevelMap=None):
    """This method sets chapter progress.

    Args:
        chapterProgressDict (dict): Chapter progress data.
        chapter (int): Number of the chapter.
        correct (bool): If True then increment correct value in chapter progress dict, if False then no action.
        chapterToLevelMap (dict): Optional argument, if not None then adjust the repeat level value.

    Returns:
        string: String representation of chapter progress dictionary.
    """

    current = chapterProgressDict[chapter]["progress"]["current"]
    total = chapterProgressDict[chapter]["progress"]["total"]
    repeatLevel = chapterProgressDict[chapter]["repeatLevel"]

    if current < total:
        chapterProgressDict[chapter]["progress"]["current"] += 1

    chapterProgressDict[chapter]["status"] = "In progress"

    if correct:
        chapterProgressDict[chapter]["correct"]["correct"] += 1

    chapterProgressDict[chapter]["correct"]["subtotal"] += 1
    chapterProgressDict[chapter]["correct"]["rate"] = getPercentage(chapterProgressDict[chapter]["correct"]["correct"], \
        chapterProgressDict[chapter]["correct"]["subtotal"])

    if chapterToLevelMap:
        if repeatLevel < chapterToLevelMap[chapter][1]:
            chapterProgressDict[chapter]["repeatLevel"] += 1

        else:
            chapterProgressDict[chapter]["repeatLevel"] += 1
            chapterProgressDict[chapter]["status"] = "Done"

    return str(chapterProgressDict)


def resetChapterProgress(chapterProgressDict, chapter, initRepeatLevel):
    """This method resets chapter progress and sets initial level for repeat routine.

    Args:
        chapterProgressDict (dict): Chapter progress data.
        chapter (int): Number of the chapter.
        initRepeatLevel (int): Initial level for repeat routine.

    Returns:
        dictionary: Return Reseted chapter progress dictionary with initial level set.
    """

    chapterProgressDict[chapter]["status"] = "Not started"
    chapterProgressDict[chapter]["progress"]["current"] = 0
    chapterProgressDict[chapter]["correct"] = {"correct":0, "subtotal":0, "rate":''}
    chapterProgressDict[chapter]["repeatLevel"] = initRepeatLevel

    return chapterProgressDict


def resetChapters(chapterProgressDict, introToLevelMap):
    """This method resets all chapters progress.

    Args:
        chapterProgressDict (dict): Chapter progress data.

    Returns:
        string: Return String representation of reseted chapters progress dictionary with initial level set.
    """

    for chapter in chapterProgressDict:
        chapterProgressDict[chapter]["status"] = "Not started"
        chapterProgressDict[chapter]["progress"]["current"] = 0
        chapterProgressDict[chapter]["correct"] = {"correct":0, "subtotal":0}
        chapterProgressDict[chapter]["repeatLevel"] = introToLevelMap[chapter][0]

    return str(chapterProgressDict)



def generateQuestion(course, level):
    """This method uses loaded levels dictionary and returns dictionary which represents single level using level argument.

    Args:
        course (str): Name of the course.
        level (int): Number of the level.

    Returns:
        dictionary: Return dictionary which represents single level from JSON course template.
    """

    return levelsDict[course][str(level)]


def introduceLetters(course, introLevel):
    """This method uses loaded character introduction dictionary and returns dictionary which represents single character
    introduction using introLevel argument.

    Args:
        course (str): Name of the course.
        introLevel (int): Number of the introduction level.

    Returns:
        dictionary: Return dictionary which represents single character introduction level from JSON template.
    """

    return introDict[course][str(introLevel)]


def storeWrongAnswer(wrongAnswers, level):
    """This method modifies list which contains wrong answers of an user.

    Args:
        wrongAnswers (list): List of levels, which were answered incorrectly.
        level (int): Number of the level.

    Returns:
        list: Returns list which contains user's wrong answers.
    """

    wrongAnswersList = ast.literal_eval(wrongAnswers) # from String to List representation

    if level not in wrongAnswersList:
        insort(wrongAnswersList, level)

    return str(wrongAnswersList)


def getWrongAnswer(wrongAnswers):
    """This method returns first item in list of user's wrong answers.

    Args:
        wrongAnswers (list): List of levels, which were answered incorrectly.

    Returns:
        int: Returns number of a level.
    """

    return wrongAnswers[0]


def removeWrongAnswer(wrongAnswers, questionNumber):
    """This method removes a wrong answer from user's list of wrong answers.

    Args:
        wrongAnswers (list): List of levels, which were answered incorrectly.
        questionNumber (int): Number of the level.

    Returns:
        string: Returns string representation of list which contains user's wrong answers.
    """

    if questionNumber in wrongAnswers:
        del wrongAnswers[bisect_left(wrongAnswers, questionNumber)]

    return str(wrongAnswers)


def storeToAnswersHistory(answersHistory, questionNumber, correct):
    """This method stores whole user progress in application so far.

    Args:
        answersHistory (dictionary): Key represents number of a question, value is dictionary which contains
            number of a level, date when question was answered and corectness of an answer.
        questionNumber (int): Number of the question.
        correct (bool): True if answer was answered correctly, otherwise False.

    Returns:
        dictionary: Returns dictionary which contains whole user progress of application so far.
    """

    answersHistory = ast.literal_eval(answersHistory) # from String to Dictionary representation
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if answersHistory: # if not empty
        answerIndex = max(answersHistory) + 1
    
    else:
        answerIndex = 1

    answersHistory[answerIndex] = {"level":questionNumber, "date":date ,"correct":correct}

    return str(answersHistory)


#routes
@main_blueprint.route('/')
#@login_required
def home():
    """This method represents route to the 'index.html' page.

    Returns:
        render_template: Returns rendered index.html template.
    """

    return render_template('main/index.html')


@main_blueprint.route('/courses', methods=['GET','POST'])
@login_required
def courses():
    """This method represents route to the 'courses.html' page where overview of courses is displayed with
    user's progress of each course. Also users can navigate to courses from there.
    This method handles both GET and POST requests.

    Returns:
        render_template: Returns rendered 'index.html' template.
    """

    courses = getCoursesFromModels()
    coursesDict = {}

    for course in courses:
        courseClass = class_for_name("project.models", course.capitalize())
        userData = courseClass.query.filter_by(email=current_user.email).first()
        currentLevel = userData.get_level()
        maxLevel = userData.get_maxLevel()
        percentageProgress = getPercentage(currentLevel, maxLevel)
        coursesDict[course] = percentageProgress
    
    sortedCourses = sorted(coursesDict.items(), key=itemgetter(1), reverse=True)

    return render_template('courses/courses.html', sortedCourses=sortedCourses)


@main_blueprint.route('/courses/<course>', methods=['GET','POST'])
@login_required
def courseOverview(course):
    """This method represents route to 'courses/<course>.html' template where is overview of a single course.
    Users can start, continue or reset progress of selected course here. This method handles both GET and POST requests.

    Args:
        course (string): Name of the course.

    Returns:
        render_template: Returns rendered 'courses/<course>.html' template.
    """

    courseClass = class_for_name("project.models", course.capitalize())
    userData = courseClass.query.filter_by(email=current_user.email).first()
    currentLevel = userData.get_level()
    maxLevel = userData.get_maxLevel()
    answersHistory = userData.get_answersHistory()
    chapterProgress = userData.get_chapterProgress()
    charStats = userData.get_charStats()
    introToLevelMap = userData.get_introToLevelMap()
    percentageProgress = getPercentage(currentLevel, maxLevel)

    answersHistoryDict = ast.literal_eval(answersHistory)
    chapterProgressDict = ast.literal_eval(chapterProgress)
    charStatsDict = ast.literal_eval(charStats)
    introToLevelMapDict = ast.literal_eval(introToLevelMap)

    charStatsKeys = sorted(charStatsDict, key=lambda k: charStatsDict[k]['rate'])

    if request.method == 'POST' and 'Reset' in request.form:
        userData.level = 1
        userData.introLevel = 1
        userData.wrongAnswers = '[]'
        userData.answersHistory = '{}'
        userData.chapterProgress = resetChapters(chapterProgressDict, introToLevelMapDict)
        userData.charStats = resetCharStats(charStatsDict)
        db.session.commit()
        flash("Your progress has been reseted", 'success')
        return redirect(url_for('main.courseOverview', course=course))

    return render_template('courses/course.html'.format(course), currentLevel=currentLevel, \
        maxLevel=maxLevel, percentageProgress=percentageProgress, course=course, 
        answersHistory=answersHistoryDict, charStats=charStatsDict, charStatsKeys=charStatsKeys,
        chapterData=chapterProgressDict, introToLevelMapDict=introToLevelMapDict) 


@main_blueprint.route('/courses/<course>/quiz',methods=['GET','POST'])
@login_required
def quiz(course):
    """This method represents route to 'courses/<course>/quiz.html' where the actual quiz is rendered.
    This method handles both GET and POST requests.

    Args:
        course (string): Name of the course.

    Returns:
        render_template: Returns rendered 'courses/<course>/quiz.html' template.
    """

    courseClass = class_for_name("project.models", course.capitalize())
    userData = courseClass.query.filter_by(email=current_user.email).first()
    currentLevel = userData.get_level()
    introLevel = userData.get_introLevel()
    maxLevel = userData.get_maxLevel()
    percentageProgress = getPercentage(currentLevel, maxLevel)
    wrongAnswers = userData.get_wrongAnswers()
    answersHistory = userData.get_answersHistory()
    introToLevelMap = userData.get_introToLevelMap()
    chapterProgress = userData.get_chapterProgress()
    charStats = userData.get_charStats()
    
    chapterProgressDict = ast.literal_eval(chapterProgress)
    introToLevelMapDict = ast.literal_eval(introToLevelMap)
    charStatsDict = ast.literal_eval(charStats)
    chapterLevelCount = introToLevelMapDict[introLevel][1] - introToLevelMapDict[introLevel][0] + 1

    if currentLevel == maxLevel:
        return redirect(url_for('main.repeatWrongAnswers', course=course))

    if currentLevel > introToLevelMapDict[introLevel][1]: 

        return redirect(url_for('main.repeatWrongAnswers', course=course))
    
    dic = generateQuestion(course, currentLevel)
    display = dic["display"]
    correct = dic["correct"]
    options = dic["options"]

    form = QuizForm(request.form)
    form.quizform.choices = [(option, option) for option in options]

    if form.validate_on_submit():
        quizForm = form.quizform.data

        userData.answersHistory = storeToAnswersHistory(answersHistory, currentLevel, quizForm == correct)
        userData.chapterProgress = setChapterProgress(chapterProgressDict, introLevel, quizForm == correct)
        userData.charStats = setCharStats(charStatsDict, (display, correct), quizForm == correct)

        if quizForm == correct:
            if currentLevel == maxLevel:
                db.session.commit()
                flash("Nice job", 'success')
                return redirect(url_for('main.repeatWrongAnswers', course=course))

            else:
                userData.level += 1
                db.session.commit()
                flash("Nice job", 'success')
                return redirect(url_for('main.quiz', course=course))

        else:
            userData.wrongAnswers = storeWrongAnswer(wrongAnswers,currentLevel)
            flash("Wrong answer " + "(" + display + " - " + correct + ")", 'danger')

            if (currentLevel == maxLevel):
                db.session.commit()
                return redirect(url_for('main.repeatWrongAnswers', course=course))

            else:
                userData.level += 1
                db.session.commit()
                return redirect(url_for('main.quiz', course=course))

    return render_template('courses/level.html', form=form, display=display, currentLevel=currentLevel, \
        maxLevel=maxLevel, percentageProgress=percentageProgress)


@main_blueprint.route('/courses/<course>/intro',methods=['GET','POST'])
@login_required
def introduction(course):
    """This method represents route to 'courses/<course>/intro.html' where the character introduction is rendered.
    This method handles both GET and POST requests.

    Args:
        course (string): Name of the course.

    Returns:
        render_template: Returns rendered 'courses/<course>/intro.html' template.
    """

    courseClass = class_for_name("project.models", course.capitalize())
    introLevel = courseClass.query.filter_by(email=current_user.email).first().get_introLevel()
    letters = introduceLetters(course, introLevel)

    return render_template('courses/introduction.html', letters=letters, course=course)


@main_blueprint.route('/courses/<course>/repeat',methods=['GET','POST'])
@login_required
def repeatWrongAnswers(course):
    """This method represents route to 'courses/<course>/repeat.html' where users re-answer levels,
    which were answered incorrectly. This method handles both GET and POST requests.

    Args:
        course (string): Name of the course.

    Returns:
        render_template: Returns rendered 'courses/<course>/repeat.html' template.
    """

    courseClass = class_for_name("project.models", course.capitalize())
    userData = courseClass.query.filter_by(email=current_user.email).first()
    currentLevel = userData.get_level()
    maxLevel = userData.get_maxLevel()
    introLevel = userData.get_introLevel()
    wrongAnswers = userData.get_wrongAnswers()    
    answersHistory = userData.get_answersHistory()
    chapterProgress = userData.get_chapterProgress()
    charStats = userData.get_charStats()
    
    wrongAnswersList = ast.literal_eval(wrongAnswers)
    chapterProgressDict = ast.literal_eval(chapterProgress)
    charStatsDict = ast.literal_eval(charStats)


    if wrongAnswersList: # check if list is non-empty
        questionNumber = getWrongAnswer(wrongAnswersList)
        dic = generateQuestion(course, questionNumber)
        display = dic["display"]
        correct = dic["correct"]
        options = dic["options"]
        form = QuizForm(request.form)
        form.quizform.choices = [(option, option) for option in options]

        if form.validate_on_submit():
            quizForm = form.quizform.data

            userData.answersHistory = storeToAnswersHistory(answersHistory, currentLevel, quizForm == correct)
            userData.chapterProgress = setChapterProgress(chapterProgressDict, introLevel, quizForm == correct)
            userData.charStats = setCharStats(charStatsDict, (display, correct), quizForm == correct)

            # removes wrong answer from database if new answer is correct
            if quizForm == correct:
                userData.wrongAnswers = removeWrongAnswer(wrongAnswersList,questionNumber)
                db.session.commit()
                flash("Nice job", 'success')
                return redirect(url_for('main.repeatWrongAnswers', course=course))

            else:
                db.session.commit()
                flash("Wrong answer " + "(" + display + " - " + correct + ")", 'danger')
                return redirect(url_for('main.repeatWrongAnswers', course=course))

    else: # list is empty, no wrong answer left
        if currentLevel < maxLevel:
            chapterProgressDict[introLevel]["status"] = "Done"
            userData.chapterProgress = str(chapterProgressDict)
            userData.introLevel += 1
            db.session.commit()
            return redirect(url_for('main.introduction', course=course)) # continue to next lesson

        return redirect(url_for('main.practice', course=course)) # course is completed, continue to practice mode

    return render_template('courses/repeat.html', form=form, display=display)


@main_blueprint.route('/courses/<course>/repeatChapter',methods=['GET','POST'])
@login_required
def repeatChapter(course):
    """This method represents route to 'courses/<course>/level.html' where users re-answer selected
    chapter. This method handles both GET and POST requests.

    Args:
        course (string): Name of the course.

    Returns:
        render_template: Returns rendered 'courses/<course>/level.html' template.
    """

    courseClass = class_for_name("project.models", course.capitalize())
    userData = courseClass.query.filter_by(email=current_user.email).first()
    introToLevelMap = userData.get_introToLevelMap()  
    answersHistory = userData.get_answersHistory()
    chapterProgress = userData.get_chapterProgress()
    charStats = userData.get_charStats()
    chapter = int(request.args.get('chapter'))

    introToLevelMapDict = ast.literal_eval(introToLevelMap)
    chapterProgressDict = ast.literal_eval(chapterProgress)
    charStatsDict = ast.literal_eval(charStats)

    currentLevel = chapterProgressDict[chapter]["repeatLevel"]
    currentDisplay = chapterProgressDict[chapter]["repeatLevel"] - introToLevelMapDict[chapter][0]
    maxLevel = introToLevelMapDict[chapter][1] - introToLevelMapDict[chapter][0] + 1

    if chapterProgressDict[chapter]["status"] == "Done":
        
        if chapterProgressDict[chapter]["repeatLevel"] == introToLevelMapDict[chapter][0]:
            chapterProgressDict = resetChapterProgress(chapterProgressDict, chapter, introToLevelMapDict[chapter][0])

        elif chapterProgressDict[chapter]["repeatLevel"] > introToLevelMapDict[chapter][1]:
            chapterProgressDict[chapter]["repeatLevel"] = introToLevelMapDict[chapter][0]
            userData.chapterProgress = str(chapterProgressDict)
            db.session.commit()
            flash("Chapter repetition has ended, check your results", 'success')
            return redirect(url_for('main.courseOverview', course=course))

    percentageProgress = getPercentage(currentDisplay, maxLevel)
    dic = generateQuestion(course, currentLevel)
    display = dic["display"]
    correct = dic["correct"]
    options = dic["options"]
    form = QuizForm(request.form)
    form.quizform.choices = [(option, option) for option in options]

    if form.validate_on_submit():
        quizForm = form.quizform.data

        userData.answersHistory = storeToAnswersHistory(answersHistory, currentLevel, quizForm == correct)
        userData.chapterProgress = setChapterProgress(chapterProgressDict, chapter, quizForm == correct, introToLevelMapDict)
        userData.charStats = setCharStats(charStatsDict, (display, correct), quizForm == correct)

        if quizForm == correct:
            db.session.commit()
            flash("Nice job", 'success')
            return redirect(url_for('main.repeatChapter', course=course, chapter=chapter))

        else:
            db.session.commit()
            flash("Wrong answer " + "(" + display + " - " + correct + ")", 'danger')
            return redirect(url_for('main.repeatChapter', course=course, chapter=chapter))

    return render_template('courses/level.html', form=form, display=display, currentLevel=currentDisplay, \
        maxLevel=maxLevel, percentageProgress=percentageProgress)


@main_blueprint.route('/courses/<course>/repeatLevel',methods=['GET','POST'])
@login_required
def repeatLevel(course):
    """This method represents route to 'courses/<course>/repeat.html' where users re-answer levels,
    which were answered incorrectly. This method handles both GET and POST requests.

    Args:
        course (string): Name of the course.

    Returns:
        render_template: Returns rendered 'courses/<course>/repeat.html' template.
    """

    courseClass = class_for_name("project.models", course.capitalize())
    userData = courseClass.query.filter_by(email=current_user.email).first()
    answersHistory = userData.get_answersHistory()
    charStats = userData.get_charStats()
    level = request.args.get('level')

    charStatsDict = ast.literal_eval(charStats)

    dic = generateQuestion(course, level)
    display = dic["display"]
    correct = dic["correct"]
    options = dic["options"]
    form = QuizForm(request.form)
    form.quizform.choices = [(option, option) for option in options]

    if form.validate_on_submit():
        quizForm = form.quizform.data

        userData.answersHistory = storeToAnswersHistory(answersHistory, level, quizForm == correct)
        userData.charStats = setCharStats(charStatsDict, (display, correct), quizForm == correct)

        db.session.commit()
        if quizForm == correct:
            flash("Nice job", 'success')
            return redirect(url_for('main.courseOverview', course=course))

        else:
            flash("Wrong answer " + "(" + display + " - " + correct + ")", 'danger')
            return redirect(url_for('main.courseOverview', course=course))

    return render_template('courses/repeat.html', form=form, display=display)



@main_blueprint.route('/courses/<course>/practice',methods=['GET'])
@login_required
def practice(course):
    """This method represents route to 'courses/<course>/practice.html' where users whose have already completed
    the course can practice by answering random question from the course. This method handles GET requests.

    Args:
        course (string): Name of the course.

    Returns:
        render_template: Returns rendered 'courses/<course>/practice.html' template.
    """

    courseClass = class_for_name("project.models", course.capitalize())
    userData = courseClass.query.filter_by(email=current_user.email).first()
    maxLevel = userData.get_maxLevel()
    wrongAnswers = userData.get_wrongAnswers()
    
    wrongAnswersList = ast.literal_eval(wrongAnswers)

    if len(wrongAnswersList) > 3:
        return redirect(url_for('main.repeatWrongAnswers', course=course))

    randomLevel = randint(0,maxLevel-1)

    dic = generateQuestion(course, randomLevel)
    display = dic["display"]
    correct = dic["correct"]
    options = dic["options"]

    form = QuizForm(request.form)
    form.quizform.choices = [(option, option) for option in options]

    return render_template('courses/practice.html', form=form, display=display, currentLevel=randomLevel, course=course)


@main_blueprint.route('/courses/<course>/practice',methods=['POST'])
@login_required
def practicePostHandler(course):
    """This method represents route to 'courses/<course>/practice.html' where users whose have already completed
    the course can practice by answering random question from the course. This method handles POST requests.

    Args:
        course (string): Name of the course.

    Returns:
        render_template: Returns rendered 'courses/<course>/practice.html' template.
    """

    courseClass = class_for_name("project.models", course.capitalize())
    userData = courseClass.query.filter_by(email=current_user.email).first()
    maxLevel = userData.get_maxLevel()
    wrongAnswers = userData.get_wrongAnswers()
    answersHistory = userData.get_answersHistory()
    charStats = userData.get_charStats()
    currentLevel = int(request.args.get('currentLevel'))

    charStatsDict = ast.literal_eval(charStats)

    dic = generateQuestion(course, currentLevel)
    display = dic["display"]
    correct = dic["correct"]
    options = dic["options"]

    form = QuizForm(request.form)
    form.quizform.choices = [(option, option) for option in options]

    if form.validate_on_submit():
        quizForm = form.quizform.data

        userData.answersHistory = storeToAnswersHistory(answersHistory, currentLevel, quizForm == correct)
        userData.charStats = setCharStats(charStatsDict, (display, correct), quizForm == correct)
        
        if quizForm == correct:
            flash("Nice job", 'success')
            return redirect(url_for('main.practice', course=course))

        else:
            userData.wrongAnswers = storeWrongAnswer(wrongAnswers,currentLevel)
            db.session.commit()
            flash("Wrong answer " + "(" + display + " - " + correct + ")", 'danger')
            return redirect(url_for('main.practice', course=course))

    return render_template('courses/practice.html', form=form, display=display)



# Load course templates into memory
introDict = loadIntroTemplates()
levelsDict = loadLevelTemplates()