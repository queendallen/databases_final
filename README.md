# databases_final

## Problem

I studied the effect COVID-19 lockdowns had on student grades. I analyzed grades before and after COVID lockdowns under conditions known to influence education, such as household income, family size, parent education levels, and availability of technology. The dataset used is [COVID-19 Effect on Grades by Dylan Bollard](https://www.kaggle.com/dylanbollard/covid19-effect-on-grades-constructed-dataset). The dataset covers six semesters: the first three recorded before COVID-19 lockdowns and the latter three recorded after lockdowns. There are six subjects tracked in this dataset: Reading, Writing, Math, Reading State- Level, Writing State-Level, and Math State-Level. The first three subjects cover grades for school exams, while the latter three are their grades for state exams.

## Software Design and Implementation

I used MongoDB, Python, and MongoClient to implement my software. My software has three sections: Student Information, Student Performance, and Overall Analysis.
First, Student Information provides details about specific students and the general student population. Showing a specific student will display their id, school, grade, gender, household income, number of computers in their home, family size, parent education levels, free lunch status, previous COVID-19 status (whether they’ve contracted COVID), and their grades across the six subjects for the six semesters. On the other hand, displaying the general student population will show the percentage of students based on several categories: family size, household income, parent education levels, school, number of computers, and grade.
Then, Student Performance similarly separates a specific student from the general student population. This section, however, will display the percent change of student grades before and after COVID-19 lockdowns. Displaying the overall performance of students includes a standard deviation of grades for each subject.
Finally, Overall Analysis allows the user to view the performance of all students based on their subject and several criteria (family size, household income, parent education levels, school, number of computers, free/reduced lunch). In addition, it includes the percent change of grades for all subjects for the entire student population.
