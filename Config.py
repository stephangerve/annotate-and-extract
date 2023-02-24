import os

drive_letter = "C:"
main_dir = drive_letter + "\\Users\\Stephan\\OneDrive\\W"
audit_dir = drive_letter + "\\Users\\Stephan\\OneDrive\\Worksheet Project\\Worksheets Audit"
blank_template_path = os.path.join(audit_dir, "Template.docx")
temp_ss_path = "C:\\Users\\Stephan\\Downloads\\Old Screenshots\\Temp"
old_ss_path = "C:\\Users\\Stephan\\Downloads\\Old Screenshots"
e_packs_dir = "C:\\Users\\Stephan\\OneDrive\\Exercise Packs"

HOSTNAME = "localhost"
USERNAME = "root"
DATABASENAME = "ls_data"
with open("C:\\Users\\Stephan\\Downloads\\db.txt") as file:
    PASSWORD = file.read()
    file.close()

open_txtbk_dir = False
open_txtbk = False
continue_from_last_ss_index = False
start_from_specific_worksheet = False
DEFAULT_FIRST_IMAGE_INDEX = 1
odds_only = False  # set to True and set DEFAULT_FIRST_IMAGE_INDEX to 2 for even-numbered

OP_SIMPLE = 1
OP_APP_TO_LAST = 2
OP_SET_HEADER = 3
OP_COMBINE_W_H = 4
OP_APP_TO_HEAD = 5
OP_GRID_MODE = 6

SHAPE_BBOX = 101
SHAPE_LINE = 111

STANDARD_OPs = [OP_SIMPLE,
                OP_APP_TO_LAST,
                OP_SET_HEADER,
                OP_COMBINE_W_H,
                OP_APP_TO_HEAD,
                OP_GRID_MODE]
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 168, 0)
NEON_GREEN = (20, 255, 57)
RED = (0, 0, 255)
PURPLE = (201, 6, 162)
BLUE = (240, 96, 7)
ORANGE = (5, 104, 252)
TURQUOISE = (229, 235, 52)
BBOX_COLOR = {
    OP_SIMPLE: RED,
    OP_APP_TO_LAST: PURPLE,
    OP_SET_HEADER: BLUE,
    OP_COMBINE_W_H: ORANGE,
    OP_APP_TO_HEAD: TURQUOISE,
}

COLUMN_LEFT = -0.1
COLUMN_RIGHT = 0.1

SCAN_RADIUS_BBOX = 30  # default: 20
SCAN_RADIUS_COL_LINE = 100  # default: 100
SCAN_RADIUS_GRID_RL = SCAN_RADIUS_BBOX  # default: 20
SCAN_RADIUS_GRID_COL = 150  # default: 150

SCAN_ROW_AVERAGE_COLOR_THRESHOLD = 255 #255 strongest intensity

# NUM_WHT_SPACE = 4

OVERWRITE_IMAGE = False
IGNORE_IF_ALREADY_EXTRACTED = False
IMAGE_TYPE = "Exercises"
#IMAGE_TYPE = "Solutions"
#####################################################
# category = 'Probability and Statistics'
# author = 'Keener'
# textbook = 'Theoretical Statistics'
# edition = '1st'

# category = "Calculus"
# author = "Stewart"
# textbook = "Calculus"
# edition = "8th"

# category = 'Probability and Statistics'
# author = 'Casella'
# textbook = 'Statistical Inference'
# edition = '2nd'

# category = "Probability and Statistics"
# author = "Peng"
# textbook = "STAT 528 Mathematical Statistics"
# edition = "1st"

# category = "Probability and Statistics"
# author = "Hogg"
# textbook = "Introduction to Mathematical Statistics"
# edition = "8th"

# category = "Mathematical Analysis and Proofs"
# author = "Chartrand"
# textbook = "Mathematical Proofs"
# edition = "4th"

# category = "Algorithms and Data Structures"
# author = "Levitin"
# textbook = "Introduction to the Design and Analysis of Algorithms"
# edition = "2nd"

category = "Algorithms and Data Structures"
author = "Cormen"
textbook = "Introduction to Algorithms"
edition = "4th"

# category = "Algorithms and Data Structures"
# author = "Neapolitan"
# textbook = "Foundations of Algorithms"
# edition = "5th"

# category = "Algorithms and Data Structures"
# author = "Levitin"
# textbook = "Introduction to the Design and Analysis of Algorithms"
# edition = "3rd"

# category = "Discrete Mathematics"
# author = "Jongsma"
# textbook = "Introduction to Discrete Mathematics Via Logic and Proof"
# edition = "1st"

# category = "Probability and Statistics"
# author = "DeGroot"
# textbook = "Probability and Statistics"
# edition = "4th"

# category = "Graph Theory"
# author = "Chartrand"
# textbook = "Graphs and Digraphs"
# edition = "6th"

# category = "Calculus"
# author = "Hughes-Hallet"
# textbook = "Calculus"
# edition = "6th"

# category = "Calculus"
# author = "Stewart"
# textbook = "Calculus"
# edition = "8th"

# category = "Discrete Mathematics"
# author = "Epp"
# textbook = "Discrete Mathematics with Applications"
# edition = "3rd"


# category = "Probability, Statistics, and Random Processes"
# author = "Moulin"
# textbook = "Statistical Inference for Engineers and Data Scientists"
# edition = "1st"

# category = "Discrete Mathematics"
# author = "DeTemple"
# textbook = "Combinatorial Reasoning"
# edition = "1st"

# category = "Probability and Statistics"
# author = "Ramachandran"
# textbook = "Mathematical Statistics With Applications in R"
# edition = "1st"

# Probability
# Calculus
# Precalculus
# DSP
# Signals and Systems
# Time Series
# Stat. SP
# Linear Algebra
# Information Theory


########################################################################################################################
# category = "Calculus"
# author = "Salas"
# textbook = "Calculus"
# edition = "10th"

# category = "Calculus"
# author = "Anton"
# textbook = "Calculus Early Transcendentals"
# edition = "1st"

# category = "Calculus"
# author = "Sullivan"
# textbook = "Calculus Early Transcendentals"
# edition = "1st"

# category = "Discrete Mathematics"
# author = "Bender"
# textbook = "Foundations of Applied Discrete Mathematics"
# edition = "1st"

# category = "Discrete Mathematics"
# author = "Grimaldi"
# textbook = "Discrete and Combinatorial Mathematics"
# edition = "5th"

# category = "Calculus"
# author = "Stewart"
# textbook = "Calculus Early Transcendentals"
# edition = "9th"

# category = "Discrete Mathematics"
# author = "West"
# textbook = "Combinatorial Mathematics"
# edition = "1st"

# category = "Graph Theory"
# author = "West"
# textbook = "Introduction to Graph Theory"
# edition = "2nd"

# Linear Algebra
# Abstract math
# Topics in math

# category = "Pure and Abstract Mathematics"
# author = "Fraleigh"
# textbook = "A First Course in Abstract Algebra"
# edition = "7th"

# category = "Linear Algebra"
# author = "Anthony"
# textbook = "Linear Algebra"
# edition = "2nd"

# category = "Linear Algebra"
# author = "Anton"
# textbook = "Contemporary Linear Algebra"
# edition = "1st"

# category = "Linear Algebra"
# author = "Bretscher"
# textbook = "Linear Algebra with Applications"
# edition = "5th"

# category = "Topics in Mathematics"
# author = "Elaydi"
# textbook = "An Introduction to Difference Equations"
# edition = "3rd"

# category = "Topics in Mathematics"
# author = "Paulsen"
# textbook = "Asymptotic Analysis and Perturbation Theory"
# edition = "1st"

# category = "Discrete Mathematics"
# author = "Conradie"
# textbook = "Logic and Discrete Mathematics"
# edition = "1st"
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
# category = 'Probability and Statistics' #1-5, 7,8
# author = 'Abramovich'
# textbook = 'Statistical Theory'
# edition = '1st'

# category = 'Probability and Statistics' #1-9,12
# author = 'Akitras'
# textbook = 'Probability and Statistics with R For Engineers and Scientists'
# edition = '1st'

# category = 'Probability and Statistics' #1-10
# author = 'Anderson'
# textbook = 'Introduction to Probability'
# edition = '1st'

# category = 'Probability and Statistics' #1-5
# author = 'Bertsekas'
# textbook = 'Introduction to Probability'
# edition = '2nd'

# category = 'Probability and Statistics' #1-9
# author = 'Bonamente'
# textbook = 'Statistics and Analysis of Scientific Data'
# edition = '2nd'

# category = 'Probability and Statistics' #1-5
# author = 'Carlton'
# textbook = 'Probability with Applications'
# edition = '2nd'

# category = 'Probability and Statistics' #1-12
# author = 'Casella'
# textbook = 'Statistical Inference'
# edition = '2nd'

# category = 'Probability and Statistics' #1-9
# author = 'Chihara'
# textbook = 'Mathematical Statistics with Resampling and R'
# edition = '1st'

# category = 'Probability and Statistics' #1-9
# author = 'DeGroot'
# textbook = 'Probability and Statistics'
# edition = '4th'

# category = 'Probability and Statistics' #1-5
# author = 'Deshmukh'
# textbook = 'Asymptotic Statistical Inference'
# edition = '1st'

# category = 'Probability and Statistics' #1-10
# author = 'Devore'
# textbook = 'Modern Mathematical Statistics with Applications'
# edition = '3rd'

# category = 'Probability and Statistics' #1, 2
# author = 'Durrett'
# textbook = 'Probability'
# edition = '2nd'

# category = 'Probability and Statistics' #1-9, 11
# author = 'Epps'
# textbook = 'Probability and Statistical Theory'
# edition = '1st'

# category = 'Probability and Statistics' #1-9
# author = 'Grinstead'
# textbook = 'Introduction to Probability'
# edition = '1st'

# category = 'Probability and Statistics' #1-9
# author = 'Gubner'
# textbook = 'Probability and Random Process for ECE'
# edition = '1st'

# category = 'Probability and Statistics' #1-4, 6, 7
# author = 'Hardle'
# textbook = 'Basics of Modern Mathematical Statistics Exercises and Solutions'
# edition = '1st'

# category = 'Probability and Statistics'
# author = 'Hastings'
# textbook = 'Introduction to Probability with Mathematica'
# edition = '2nd'

# category = 'Probability and Statistics'
# author = 'Heumann'
# textbook = 'Introduction to Statistics and Data Analysis'
# edition = '1st'

# category = 'Probability and Statistics'
# author = 'Hogg'
# textbook = 'Introduction to Mathematical Statistics'
# edition = '8th'

# category = 'Probability and Statistics'
# author = 'Ibe'
# textbook = 'Fundamentals of Applied Probability and Random Processes'
# edition = '2nd'

# category = 'Probability and Statistics' #10, 11, 18, 19
# author = 'Kobayashi'
# textbook = 'Probability, Random Processes, and Statistical Analysis'
# edition = '1st'

# category = 'Probability and Statistics' #1-6
# author = 'Kupper'
# textbook = 'Statistical Theory'
# edition = '1st'

# category = 'Probability and Statistics' #1-7
# author = 'Larsen'
# textbook = 'Introduction to Mathematical Statistics and Its Application'
# edition = '5th'

# category = 'Probability and Statistics' #1-8
# author = 'Leon-Garcia'
# textbook = 'Probability, Statistics, and Random Processes for EE'
# edition = '3rd'

# category = 'Probability and Statistics' #1-11
# author = 'Mendenhall'
# textbook = 'Statistics for Engineering and the Sciences'
# edition = '1st'

# category = 'Probability and Statistics'
# author = 'Meyer'
# textbook = 'Probability and Mathematical Statistics'
# edition = '1st'

# category = 'Probability and Statistics' #1-8, 10-13
# author = 'Miller'
# textbook = 'Freunds Mathematical Statistics with Applications'
# edition = '8th'

# category = 'Probability and Statistics' #1-11
# author = 'Montgomery'
# textbook = 'Applied Statistics and Probability for Engineers'
# edition = '3rd'

# category = 'Probability and Statistics' #1-8
# author = 'Navidi'
# textbook = 'Statistics for Engineers and Scientists'
# edition = '1st'

# category = 'Probability and Statistics' #1-8
# author = 'Navidi'
# textbook = 'Principles of Statistics for Engineers and Scientists'
# edition = '1st'

# category = 'Probability and Statistics' #1-8
# author = 'Papoulis'
# textbook = 'Probability, Random Variables, and Stochastic Processes'
# edition = '4th'

# category = 'Probability and Statistics'
# author = 'Peng'
# textbook = 'STAT 528 Mathematical Statistics'
# edition = '1st'

# category = 'Probability and Statistics' #1-4, 8
# author = 'Rasch'
# textbook = 'Applied Statistics'
# edition = '1st'

# category = 'Probability and Statistics' #1-9
# author = 'Ross'
# textbook = 'Introduction to Probability and Statistics'
# edition = '6th'

# category = 'Probability and Statistics' #1-13
# author = 'Roussas'
# textbook = 'An Introduction to Probability'
# edition = '2nd'

# category = 'Probability and Statistics' #1-13
# author = 'Roussas'
# textbook = 'An Introduction to Probability and Statistical Inference'
# edition = '2nd'

# category = 'Probability and Statistics' #1-9
# author = 'Ryan '
# textbook = 'Modern Engineering Statistics'
# edition = '1st'

# category = 'Probability and Statistics' #1-4, 6
# author = 'Shao'
# textbook = 'Mathematical Statistics'
# edition = '2nd'

# category = 'Probability and Statistics' #1-10
# author = 'Wackerly'
# textbook = 'Mathematical Statistics with Applications'
# edition = '7th'

# category = 'Probability and Statistics' #1-12
# author = 'Walpole'
# textbook = 'Probability & Statistics for Engineers and Scientists'
# edition = '9th'




