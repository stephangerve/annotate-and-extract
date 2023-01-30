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

SCAN_RADIUS_BBOX = 50  # default: 20
SCAN_RADIUS_COL_LINE = 100  # default: 100
SCAN_RADIUS_GRID_RL = SCAN_RADIUS_BBOX  # default: 20
SCAN_RADIUS_GRID_COL = 150  # default: 150

# NUM_WHT_SPACE = 4

OVERWRITE_IMAGE = True
#IMAGE_TYPE = "Exercises"
IMAGE_TYPE = "Solutions"
#####################################################
# category = "Calculus"
# author = "Stewart"
# textbook = "Calculus"
# edition = "8th"

category = "Probability and Statistics"
author = "Peng"
textbook = "STAT 528 Mathematical Statistics"
edition = "1st"

# category = "Mathematical Analysis and Proofs"
# author = "Chartrand"
# textbook = "Mathematical Proofs"
# edition = "4th"

# category = "Algorithms and Data Structures"
# author = "Cormen"
# textbook = "Introduction to Algorithms"
# edition = "4th"

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

# category = "Algorithms and Data Structures"
# author = "Goodrich"
# textbook = "Algorithm Design and Applications"
# edition = "1st"

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

# category = "Combinatorics"
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

# category = "Combinatorics"
# author = "Bender"
# textbook = "Foundations of Applied Combinatorics"
# edition = "1st"

# category = "Combinatorics"
# author = "Grimaldi"
# textbook = "Discrete and Combinatorial Mathematics"
# edition = "5th"

# category = "Combinatorics"
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
