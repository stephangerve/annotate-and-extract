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
PASSWORD = ""

open_txtbk_dir = False
open_txtbk = False
continue_from_last_ss_index = False
start_from_specific_worksheet = False
DEFAULT_FIRST_IMAGE_INDEX = 1
odds_only = False

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


IMAGE_TYPE = "Exercises"
#IMAGE_TYPE = "Solutions"
#####################################################
# category = "Calculus"
# author = "Stewart"
# textbook = "Calculus"
# edition = "8th"

# category = "Calculus"
# author = "Salas"
# textbook = "Calculus"
# edition = "10th"

# category = "Calculus"
# author = "Adams"
# textbook = "Calculus"
# edition = "9th"

# category = "Calculus"
# author = "Anton"
# textbook = "Calculus Early Transcendentals"
# edition = "1st"

# category = "Calculus"
# author = "Hughes-Hallet"
# textbook = "Calculus"
# edition = "6th"

# category = "Algorithms and Data Structures"
# author = "Cormen"
# textbook = "Introduction to Algorithms"
# edition = "4th"

category = "Discrete Mathematics"
author = "Rosen"
textbook = "Discrete Mathematics and Its Applications"
edition = "7th"

# Probability
# Discrete Math
# Algorithms
# Calculus
# Combinatorics
# Graph Theory
# Number Theory
# Sums/ Recurrence Relations
# Precalculus
# DSP
# Signals and Systems
# Time Series
# Stat. SP
# Linear Algebra
# Information Theory

