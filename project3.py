from pymongo import MongoClient

#constants (Includes: number of students and database -> user output conversions)
NUMSTUDENTS = 1400
EDUCATION = {0 : "No HS Diploma", 1 : "HS Diploma", 2: "BS", 3: "MS", 4 : "PhD"}
SCHOOL = {True: "School: B (Poor)", False: "School: A (Wealthy)"}
GENDER = {True: "Gender: Female", False: "Gender: Male"}
COVIDPOS = {True: "Has had COVID", False: "Has never had COVID"}
FREELUNCH = {True: "Free or Reduced Lunch: Yes", False: "Free or Reduced Lunch: No"}

# Final step in finding the average of a list
# -> Divides the added total by the number of semesters
# Input: 
#   1) values: a list of tuples (int) - (pre-COVID avg for a subject, post-COVID avg for a subject)
#   2) numSem: the number of semesters (int)
# Returns a new list with the final averages 
def calcDivAvgList(values, numSem):
    avg = []
    for x in values:
        avg.append((x[0]/numSem, x[1]/numSem))
    return avg

# Finds the average
def avg(x,y):
    return (x + y)/2

# Finds the square root using approximation
# Input 
#   1) n: The original number
#   2) Guess: A guess
#   3) nearEnough: Margin of error
# Returns the square root
def sqrtAppr(n, guess, nearEnough):
    if(abs(((guess*guess) - n)) < nearEnough):
        return guess
    else:
        return sqrtAppr(n, avg((n/guess), guess), nearEnough)

# Uses Newton's Method to find the standard deviation
# Input
#   1) performances: The performances collection
#   2) avgList: A list of averages/mean
#   3) sem: The number of semesters
#  Returns a final array of the standard deviations for each subject
def calcStandardDeviation(performances, avgList, sem):
    #Check if semester is 0 (pre) or 1 (post)
    if(sem == 0): # Query: Find the performances for semesters 0 - 2 (pre)
        stmt = {"time_period":{"$lt" : 3}}
    else: # Query: Find the performances for semesters 3 - 5 (post)
        stmt = {"time_period":{"$gt" : 3}}
        
    performanceRes = performances.find(stmt)
    readingTotal = writingTotal = mathTotal = readingSLTotal = writingSLTotal = mathSLTotal = 0
    # Squares the difference between the reading score and the mean
    for perf in performanceRes:
        readingTotal += ((perf["reading"] - avgList[0]) ** 2)
        writingTotal += ((perf["writing"] - avgList[1]) ** 2)
        mathTotal += ((perf["math"] - avgList[2]) ** 2)
        readingSLTotal += ((perf["readingSL"] - avgList[3]) ** 2)
        writingSLTotal += ((perf["writingSL"] - avgList[4]) ** 2)
        mathSLTotal += ((perf["mathSL"] - avgList[5]) ** 2)

    numSem = 3 * NUMSTUDENTS #pre or post is only 3 semesters
    allStdDev = [sqrtAppr((readingTotal/numSem), 1, 0.001), sqrtAppr((writingTotal/numSem), 1, 0.001), sqrtAppr((mathTotal/numSem), 1, 0.001), sqrtAppr((readingSLTotal/numSem), 1, 0.001), sqrtAppr((writingSLTotal/numSem), 1, 0.001), sqrtAppr((mathSLTotal/numSem), 1, 0.001)]
    return allStdDev

# Finds the percent change for 1 subject
# Input
#   1) preAvg (int): Average of the pre-COVID grades
#   2) postAvg (int): Average of the post-COVID grades
def calcPercentChange(preAvg, postAvg):
    percentage = ((preAvg - postAvg)/preAvg) * 100
    percentageRounded = round(percentage, 2)
    return (percentageRounded)

# Finds the percent change for 1 subject based on the student
# Input
#   1) studentPerformance: Cursor to a student's grades
#   2) subject: The subject (string)
# Returns the percent change
def calcPercentChangeBySubject(studentPerformance, subject):
    i = 0
    preAvg = postAvg = 0
    for perf in studentPerformance:
        if i < 3:
            preAvg += perf[subject]
        else:
            postAvg += perf[subject]
        i += 1

    # Calculate avg
    numSem = 3
    preAvg /= numSem
    postAvg /= numSem

    # Calculate percent change
    percentChange = calcPercentChange(preAvg, postAvg)
    return percentChange

# Finds the percent change for all 6 subjects
# Input
#   1) avgList: A list of tuples (int) that contain the pre-COVID average and post-COVID average
# Returns list of percent change for each subject
def calcListPercentChange(avgList):
    percentChanges = []
    for topic in avgList:
        percentage = ((topic[0] - topic[1])/topic[0]) * 100
        percentageRounded = round(percentage, 2)
        if(percentageRounded < 0): #Difference is negative --> score improved
           percentageRounded = str(abs(percentageRounded)) + "% increase"
        else:
            percentageRounded = str(percentageRounded) + "% decrease"
        percentChanges.append(percentageRounded)
    return percentChanges

# Groups the students based on a criteria (household_income, family_size, ...)
# Input
#   1) students: Collection of students
#   2) criteria: string, Ex: household_income, family_size, ...
# Returns a cursor to a list of students grouped by the criteria
def aggregateStudents(students, criteria):
    search = "$" + criteria
    studentsRes = students.aggregate([
            {"$group": 
                {"_id": search, 
                "size":{"$count" : { }}
                }
            },
            {"$sort" : 
                {"_id" : 1}
            }
        ])
    return studentsRes 

# Gives info on a student (sid, gradelvl, gender, covidpos, freelunch, num_computers,
# family size, household income, parents' educations, and school type & their school performance for different periods)
# Input: sid (int)
# Output: Printing a the student info & a list of grades
def studentInfo(students, performances):
    # Get the sid
    sid = int(input("Enter a student id: "))

    # Check if the sid is valid (1 <= sid <= 1400)
    if(sid < 1 or sid > NUMSTUDENTS):
        print("Please enter a valid id")
        return

    # Query 1: Get student info
    stmt1 = {"_id" : sid}
    studentRes = students.find(stmt1)
    print("Student Info:")
    for sr in studentRes:
        print("\t Id:", sr["_id"])
        print("\t", SCHOOL[sr["school"]]) #1 is School B, 0 is School A
        print("\t Grade Level:", sr["gradelvl"])
        print("\t", GENDER[sr["gender"]]) #1 is male, 0 is female
        print("\t", COVIDPOS[sr["covidpos"]]) #1 is child had COVID
        print("\t Household Income: $", sr["household_income"])
        print("\t", FREELUNCH[sr["freelunch"]]) #1 is takes free lunch or reduced lunch
        print("\t Number of Computers:", sr["num_computers"])
        print("\t Family Size:", sr["family_size"])

        fatherEduc = "\t Father's Education: "
        print(fatherEduc + EDUCATION[sr["father_educ"]])

        motherEduc = "\t Mother's Education: "
        print(motherEduc + EDUCATION[sr["mother_educ"]])

    # Query 2: Get performance info
    stmt2 = {"sid" : sid}
    performanceRes = performances.find(stmt2, {"_id": 0, "sid":0}).sort("time_period", 1)
    print("\nPerformance:")
    # Print the performance info
    for pr in performanceRes:
        print("\t Semester:", pr["time_period"])
        print("\t\t Reading", pr["reading"])
        print("\t\t Writing", pr["writing"])
        print("\t\t Math:", pr["math"])
        print("\t\t Reading State Level (SL):", pr["readingSL"])
        print("\t\t Writing State Level (SL):", pr["writingSL"])
        print("\t\t Math State Level (SL):", pr["mathSL"])
    return

# Gives the percent change of an individual student's performance pre and post COVID
# Input
#   1) performances: Collection of performances
# Returns nothing
def studentPerfChange(performances):
    # Get the sid
    sid = int(input("Enter a student id: "))

    # Check if the sid is valid (1 <= sid <= 1400)
    if(type(sid) != int or sid < 1 or sid > 1400):
        print("Please enter a valid id")
        return

    # Query: Get performance info
    stmt = {"sid" : sid}
    performanceRes = performances.find(stmt, {"_id": 0, "sid": 0}).sort("time_period", 1)

    # Display performance for different semesters and get the pre and post covid grade totals (for avg)
    i = 0
    preReadingAvg = preWritingAvg = preMathAvg = preReadingSLAvg = preWritingSLAvg = preMathSLAvg = 0
    postReadingAvg = postWritingAvg = postMathAvg = postReadingSLAvg = postWritingSLAvg = postMathSLAvg = 0
    print("Performance:")
    # Print the performances info and get the total scores of each subject
    for perf in performanceRes:
        print("\t Semester: ", perf["time_period"])
        print("\t\t Reading Local Level: ", perf["reading"])
        print("\t\t Writing Local Level: ", perf["writing"])
        print("\t\t Math Local Level: ", perf["math"])
        print("\t\t Reading State Level (SL): ", perf["readingSL"])
        print("\t\t Writing State Level (SL): ", perf["writingSL"])
        print("\t\t Math State Level (SL): ", perf["mathSL"])
        if i < 3:
            preReadingAvg += perf["reading"]
            preWritingAvg += perf["writing"]
            preMathAvg += perf["math"]
            preReadingSLAvg += perf["readingSL"]
            preWritingSLAvg += perf["writingSL"]
            preMathSLAvg += perf["mathSL"]
        else:
            postReadingAvg += perf["reading"]
            postWritingAvg += perf["writing"]
            postMathAvg += perf["math"]
            postReadingSLAvg += perf["readingSL"]
            postWritingSLAvg += perf["writingSL"]
            postMathSLAvg += perf["mathSL"]
        i += 1
    
    print("\nPerformance Analysis (using pre- and post-COVID averages)\nPre-COVID: Semesters 0 - 2\nPost-COVID: Semesters 3 - 5")

    # Calculate avg
    numSem = 3
    avgList = [(preReadingAvg, postReadingAvg), (preWritingAvg, postWritingAvg), (preMathAvg, postMathAvg), (preReadingSLAvg, postReadingSLAvg), (preWritingSLAvg, postWritingSLAvg), (preMathSLAvg, postMathSLAvg)]
    avgList = calcDivAvgList(avgList, numSem)

    # Calculate percent change
    percentChange = calcListPercentChange(avgList)

    #Print percentages
    print("\tReading: ", percentChange[0])
    print("\tWriting: ", percentChange[1])
    print("\tMath: ", percentChange[2])
    print("\tReadingSL: ", percentChange[3])
    print("\tWritingSL: ", percentChange[4])
    print("\tMathSL: ", percentChange[5])
    return

# Displays
#   1) The overall percent change for each subject
#   2) The standard deviation of students pre and post COVID
# Input
#   1) performances: Collection of performances
# Returns nothing
def allStudentPerfChange(performances):
    # Query: Get performance info
    performanceRes = performances.find({})
    i = 0
    preReadingAvg = preWritingAvg = preMathAvg = preReadingSLAvg = preWritingSLAvg = preMathSLAvg = 0
    postReadingAvg = postWritingAvg = postMathAvg = postReadingSLAvg = postWritingSLAvg = postMathSLAvg = 0
    print("Performance: \n  Percent Change")
    # Get the total scores of each subject
    for perf in performanceRes:
        if i % 6 < 3:
            preReadingAvg += perf["reading"]
            preWritingAvg += perf["writing"]
            preMathAvg += perf["math"]
            preReadingSLAvg += perf["readingSL"]
            preWritingSLAvg += perf["writingSL"]
            preMathSLAvg += perf["mathSL"]
        else:
            postReadingAvg += perf["reading"]
            postWritingAvg += perf["writing"]
            postMathAvg += perf["math"]
            postReadingSLAvg += perf["readingSL"]
            postWritingSLAvg += perf["writingSL"]
            postMathSLAvg += perf["mathSL"]
        i += 1

    # Calculate avg
    numSem = 3 * 1400
    avgList = [(preReadingAvg, postReadingAvg), (preWritingAvg, postWritingAvg), (preMathAvg, postMathAvg), (preReadingSLAvg, postReadingSLAvg), (preWritingSLAvg, postWritingSLAvg), (preMathSLAvg, postMathSLAvg)]
    avgList = calcDivAvgList(avgList, numSem)

    # Calculate percent change
    percentChange = calcListPercentChange(avgList)
    
    #Print percentages
    topicList = ["\tReading: ", "\tWriting: ", "\tMath: ", "\tReadingSL: ", "\tWritingSL: ", "\tMathSL: "]
    i = 0
    for x in topicList:
        print(x, percentChange[i])
        i += 1

    # Calculate Standard Deviation
    print("\n  Standard Deviation")
    preAvgList = [preReadingAvg/numSem, preWritingAvg/numSem, preMathAvg/numSem, preReadingSLAvg/numSem, preWritingSLAvg/numSem, preMathSLAvg/numSem]
    postAvgList = [postReadingAvg/numSem, postWritingAvg/numSem, postMathAvg/numSem, postReadingSLAvg/numSem, postWritingSLAvg/numSem, postMathSLAvg/numSem]
    stdPre = calcStandardDeviation(performances, preAvgList, 0)
    stdPost = calcStandardDeviation(performances, postAvgList, 1)

    i = 0
    #Print standard deviations
    for x in topicList:
        print(x, "\n\t\tPre-COVID Mean: ", preAvgList[i])
        print("\t\tPost-COVID Mean: ", postAvgList[i])
        print("\t\tPre-COVID: ", stdPre[i])
        print("\t\tPost-COVID: ", stdPost[i])
        i += 1
    return

# Gives distribution of all students based on their family size, income,
# parents' educations, and school type in percentages
# Input
#   1) students: Collection of students
# Returns nothing
def studentDemographic(students):
    print("Which student percentage would you like to see?")
    print("1) Percent of students based on family size")
    print("2) Percent of students based on household income")
    print("3) Percent of students based on parents' educations")
    print("4) Percent of students based on school type")
    print("5) Percent of students based on grade level")
    print("6) Percent of students based on number of computers")

    choice = int(input("Choice: "))
    if(choice == 1): # Family Size
        studentsRes = aggregateStudents(students, "family_size")
        for sr in studentsRes:
            print("\t",round((sr["size"]/NUMSTUDENTS) * 100, 2), "% of students have a family size of ", sr["_id"])
    elif(choice == 2): # Household Income
        studentsRes = students.aggregate([
                {"$group": 
                    {
                        "_id": {
                            "$cond" : [
                                        {"$lte" : ["$household_income", 50000]}, "<50000", {
                                            "$cond" : [
                                                {"$lte" : ["$household_income", 60000]}, "50000 - 59999", {
                                                    "$cond" : [
                                                        {"$lte" : ["$household_income", 70000]}, "60000 - 69999", {
                                                            "$cond" : [
                                                                {"$lte" : ["$household_income", 80000]}, "70000 - 79999", {
                                                                    "$cond" : [
                                                                        {"$lte" : ["$household_income", 90000]}, "80000 - 89999", {
                                                                            "$cond" : [
                                                                                {"$lte" : ["$household_income", 100000]}, "90000 - 99999", ">100000"
                                                                            ]
                                                                        }
                                                                    ]
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                ]
                        }, 
                    "size":{"$count" : { }}
                    }
                },
                {"$sort" : 
                    {"_id" : 1}
                }
            ])
        for sr in studentsRes:
            print("\t", round((sr["size"]/NUMSTUDENTS) * 100,2), "% of students have a household income of", sr["_id"])
    elif(choice == 3): # Parents' Educations
        print("Father: ")
        studentsRes = aggregateStudents(students, "father_educ") 
        for sr in studentsRes:
            print("\t", round((sr["size"]/NUMSTUDENTS) * 100, 2), "% of students have a father who has", EDUCATION[sr["_id"]]) 

        print("Mother: ")
        studentsRes = aggregateStudents(students, "mother_educ")
        for sr in studentsRes:
            print("\t", round((sr["size"]/NUMSTUDENTS) * 100, 2), "% of students have a mother who has", EDUCATION[sr["_id"]]) 
    elif(choice == 4): # School
        studentsRes = aggregateStudents(students, "school")
        for sr in studentsRes:
            print("\t", round((sr["size"]/NUMSTUDENTS) * 100, 2), "% of students are in", SCHOOL[sr["_id"]]) 
    elif(choice == 5): # Grade Level
        studentsRes = aggregateStudents(students, "gradelvl")
        for sr in studentsRes:
            print("\t",round((sr["size"]/NUMSTUDENTS) * 100, 2), "% of students are in grade", sr["_id"])
    elif(choice == 6): # Number of Computers
        studentsRes = aggregateStudents(students, "num_computers")
        for sr in studentsRes:
            print("\t",round((sr["size"]/NUMSTUDENTS) * 100, 2), "% of students have", sr["_id"], "computers")
    else:
        print("Please state a valid input")
    return

# Displays the percent change for a subject in deciles
# Input
#   1) subject: Collection of performances for a specific subject
#   2) subjectName: subject's name (string)
#   3) criteria: criteria to group subject on (string)
# Returns nothing
def showChangeByX(subject, subjectName, criteria):
    NUMSTUDENTS = 1400

    # Print percent change by subject - studentsRes is a cursor
    studentsRes = subject.aggregate([
                {"$group": 
                    {
                        "_id": {
                            "$cond" : [
                                        {"$lte" : ["$change", 0]}, "increased", {
                                            "$cond" : [
                                                {"$lte" : ["$change", 10]}, "decreased by 0 - 9%", {
                                                    "$cond" : [
                                                        {"$lte" : ["$change", 20]}, "decreased by 10 - 19%", {
                                                            "$cond" : [
                                                                {"$lte" : ["$change", 30]}, "decreased by 20 - 29%", {
                                                                    "$cond" : [
                                                                        {"$lte" : ["$change", 40]}, "decreased by 30 - 39%", {
                                                                            "$cond" : [
                                                                                {"$lte" : ["$change", 50]}, "decreased by 40 - 49%", {
                                                                                    "$cond" : [
                                                                                        {"$lte" : ["$change", 60]}, "decreased by 50 - 59%", "decreased by >= 60%"
                                                                                    ]
                                                                                }
                                                                            ]
                                                                        }
                                                                    ]
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                ]
                        }, 
                    "size":{"$count" : { }}
                    }
                },
                {"$sort" : 
                    {"_id" : 1}
                }
            ])
    decileSize = {} # Stores number of students in each percentile
    for sr in studentsRes:
        decileSize[sr["_id"]] = sr["size"]
        print("\t The", subjectName ,"percent change of", round((sr["size"]/NUMSTUDENTS) * 100,2), "% of students", sr["_id"])


    # Print demographic based on criteria
    search = "$" + criteria
    if(criteria != "household_income"):
        ofStudents = subject.aggregate([
                    {"$group": 
                        {
                            "_id": {
                                "change" : {"$cond" : [
                                            {"$lte" : ["$change", 0]}, "increased", {
                                                "$cond" : [
                                                    {"$lte" : ["$change", 10]}, "decreased by 0 - 9%", {
                                                        "$cond" : [
                                                            {"$lte" : ["$change", 20]}, "decreased by 10 - 19%", {
                                                                "$cond" : [
                                                                    {"$lte" : ["$change", 30]}, "decreased by 20 - 29%", {
                                                                        "$cond" : [
                                                                            {"$lte" : ["$change", 40]}, "decreased by 30 - 39%", {
                                                                                "$cond" : [
                                                                                    {"$lte" : ["$change", 50]}, "decreased by 40 - 49%", {
                                                                                        "$cond" : [
                                                                                            {"$lte" : ["$change", 60]}, "decreased by 50 - 59%", " decreased by >= 60%"
                                                                                        ]
                                                                                    }
                                                                                ]
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                    ]},
                                "criteria" : search
                            }, 
                        "size":{"$count" : { }}
                        }
                    },
                    {"$sort" : 
                        {"_id" : 1}
                    }
                ])
    else: # Handles household income ranges
        ofStudents = subject.aggregate([
                {"$group": 
                    {
                        "_id": {
                            "change" : {"$cond" : [
                                        {"$lte" : ["$change", 0]}, "increased", {
                                            "$cond" : [
                                                {"$lte" : ["$change", 10]}, "decreased by 0 - 9%", {
                                                    "$cond" : [
                                                        {"$lte" : ["$change", 20]}, "decreased by 10 - 19%", {
                                                            "$cond" : [
                                                                {"$lte" : ["$change", 30]}, "decreased by 20 - 29%", {
                                                                    "$cond" : [
                                                                        {"$lte" : ["$change", 40]}, "decreased by 30 - 39%", {
                                                                            "$cond" : [
                                                                                {"$lte" : ["$change", 50]}, "decreased by 40 - 49%", {
                                                                                    "$cond" : [
                                                                                        {"$lte" : ["$change", 60]}, "decreased by 50 - 59%", " decreased by >= 60%"
                                                                                    ]
                                                                                }
                                                                            ]
                                                                        }
                                                                    ]
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                ]},
                            "criteria" : {"$cond" : [
                                    {"$lte" : ["$household_income", 50000]}, "<50000", {
                                        "$cond" : [
                                            {"$lte" : ["$household_income", 60000]}, "50000 - 59999", {
                                                "$cond" : [
                                                    {"$lte" : ["$household_income", 70000]}, "60000 - 69999", {
                                                        "$cond" : [
                                                            {"$lte" : ["$household_income", 80000]}, "70000 - 79999", {
                                                                "$cond" : [
                                                                    {"$lte" : ["$household_income", 90000]}, "80000 - 89999", {
                                                                        "$cond" : [
                                                                            {"$lte" : ["$household_income", 100000]}, "90000 - 99999", ">100000"
                                                                        ]
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                            ]}
                        }, 
                    "size":{"$count" : { }}
                    }
                },
                {"$sort" : 
                    {"_id" : 1}
                }
            ])
    print("\nOf these students")
    temp = ""
    # Prints out the info
    for sr in ofStudents:
        if(temp != sr["_id"]["change"]):
            print("")
            print(sr["_id"]["change"])
            temp = sr["_id"]["change"]
        if(criteria == "freelunch"):
            print("\t", round((sr["size"]/decileSize[sr["_id"]["change"]]) * 100,2), "% of students have a", criteria ,"of", FREELUNCH[sr["_id"]["criteria"]])
        elif(criteria == "father_educ" or criteria == "mother_educ"):
            print("\t", round((sr["size"]/decileSize[sr["_id"]["change"]]) * 100,2), "% of students have a", criteria ,"of", EDUCATION[sr["_id"]["criteria"]])
        else:
            print("\t", round((sr["size"]/decileSize[sr["_id"]["change"]]) * 100,2), "% of students have a", criteria ,"of", sr["_id"]["criteria"])    
    return

# Prints overall percent change and offers the user the option to view the percent changes based on subject and criteria
# Input
#   1) db: main database
# Returns nothing 
def overallAnalysis(db):
    # Get collections
    performances = db.performances
    students = db.students

     # Query: Get performance info
    performanceRes = performances.find({})
    i = 0
    preReadingAvg = preWritingAvg = preMathAvg = preReadingSLAvg = preWritingSLAvg = preMathSLAvg = 0
    postReadingAvg = postWritingAvg = postMathAvg = postReadingSLAvg = postWritingSLAvg = postMathSLAvg = 0
    print("Performance: \n  Overall Percent Change")
    # Get the total scores for each subject
    for perf in performanceRes:
        if i % 6 < 3: #pre-COVID
            preReadingAvg += perf["reading"]
            preWritingAvg += perf["writing"]
            preMathAvg += perf["math"]
            preReadingSLAvg += perf["readingSL"]
            preWritingSLAvg += perf["writingSL"]
            preMathSLAvg += perf["mathSL"]
        else: #post-COVID
            postReadingAvg += perf["reading"]
            postWritingAvg += perf["writing"]
            postMathAvg += perf["math"]
            postReadingSLAvg += perf["readingSL"]
            postWritingSLAvg += perf["writingSL"]
            postMathSLAvg += perf["mathSL"]
        i += 1

    # Calculate avg
    numSem = 3 * NUMSTUDENTS
    avgList = [(preReadingAvg, postReadingAvg), (preWritingAvg, postWritingAvg), (preMathAvg, postMathAvg), (preReadingSLAvg, postReadingSLAvg), (preWritingSLAvg, postWritingSLAvg), (preMathSLAvg, postMathSLAvg)]
    avgList = calcDivAvgList(avgList, numSem)

    # Calculate percent change
    percentChange = calcListPercentChange(avgList)
    
    #Print percentages overall
    topicList = ["reading", "writing", "math", "readingSL", "writingSL", "mathSL"]
    i = 0
    for x in topicList:
        print("\t", x[0].upper() + x[1:] , ":", percentChange[i])
        i += 1

    #Print percentages per subject and separated into deciles
    print("  Percent Changes by Subject (separated into deciles)")
    # User input
    choice = -1
    while(choice != "quit"):
        print("Which would you like to see? Choose a subject and criteria. Enter like '1a' or '2b'")
        print("1) Reading")
        print("2) Writing")
        print("3) Math")
        print("4) ReadingSL")
        print("5) WritingSL")
        print("6) MathSL\n")
        print("a) Family Size")
        print("b) Household Income")
        print("c) Free or Reduced Lunch")
        print("d) Father's Education")
        print("e) Mother's Education")
        print("f) Number of Household Computers")
        print("To quit, enter 'quit'")
        choice = input("Choice: ")

        if(len(choice) < 2 or ((choice[0] < '1' or choice[0] > '6' or choice[1] < 'a' or choice[1] > 'f') and choice != "quit")): # Check user input
            print("Please state a valid input\n")
        else: #Choose a subject
            if(choice[0] == '1'):
                print("Reading Change: ")
                col = db.reading
                name = "reading"
            elif(choice[0] == '2'):
                print("Writing Change: ")
                col = db.writing
                name = "writing"
            elif(choice[0] == '3'):
                print("Math Change: ")
                col = db.math
                name = "math"
            elif(choice[0] == '4'):
                print("ReadingSL Change: ")
                col = db.readingSL
                name = "readingSL"
            elif(choice[0] == '5'):
                print("WritingSL Change: ")
                col = db.writingSL
                name = "writingSL"
            elif(choice[0] == '6'):
                print("MathSL Change: ")
                col = db.mathSL
                name = "mathSL"
            
            # Choose a criteria
            if(choice[1] == 'a'):
                criteria = "family_size"
            elif(choice[1] == 'b'):
                criteria = "household_income"
            elif(choice[1] == 'c'):
                criteria = "freelunch"
            elif(choice[1] == 'd'):
                criteria = "father_educ"
            elif(choice[1] == 'e'):
                criteria = "mother_educ"
            elif(choice[1] == 'f'):
                criteria = "num_computers"
            if(choice != "quit"):
                showChangeByX(col, name, criteria)

    # Populate collections
    #for subj in topicList:
        #col = db[subj]
        #for i in range(1,1401):
            #student = students.find({"_id" : i})
            #studentPerformance = performances.find({"sid" : i}, {"_id": 0, "sid": 0}).sort("time_period", 1)
            #change = calcPercentChangeBySubject(studentPerformance, subj)
            #for s in student:
                #col.insert_one({"_id" : i, "school" : s["school"], "gender" : s["gender"], "household_income" : s["household_income"], "freelunch" : s["freelunch"], "num_computers" : s["num_computers"], "family_size" : s["family_size"], "father_educ" : s["father_educ"], "mother_educ" : s["mother_educ"] ,"change": change})
        #print("Finished", col)
    return

def main():
    # connect to MongoDB
    client = MongoClient("mongodb://localhost:27017")
    db = client.covid19stud

    # Get collections from database (or create if they don't exist)
    students = db.students
    performances = db.performances

    # Get population size - performances has multiple values for students -> use students
    population = students.estimated_document_count()

    # User input
    choice = -1
    while(choice != 0):
        print("Which would you like to see? Enter 0 to exit")
        print("1) Student Info")
        print("2) Performance Changes")
        print("3) Overall Analysis")
        choice = int(input("Choice: "))

        if(choice == 1): # Choose a student info option
            print("a) Specific Student (IDs range from 1 - 1400)")
            print("b) Student Demographic (Data will be displayed as percentages)")
            studentChoice = input("Choice: ")

            if(studentChoice == 'a'):
                studentInfo(students, performances)
            elif(studentChoice == 'b'):
                studentDemographic(students)
            else:
                print("Please state a valid input")
        elif(choice == 2): # Choose a student performance option
            print("a) Specific Student (IDs range from 1 - 1400)")
            print("b) All Students")
            studentChoice = input("Choice: ")

            if(studentChoice == 'a'):
                studentPerfChange(performances)
            elif(studentChoice == 'b'):
                allStudentPerfChange(performances)
            else:
                print("Please state a valid input")
        elif(choice == 3): # Overall analysis
            overallAnalysis(db)
        elif(choice != 0):
            print("Please state a valid input")

# Execute main
if __name__ == "__main__":
    main()
