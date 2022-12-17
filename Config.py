import os


drive_letter = "C:"
main_dir = drive_letter + "\\Users\\Stephan\\OneDrive\\W"
audit_dir = drive_letter + "\\Users\\Stephan\\OneDrive\\Worksheet Project\\Worksheets Audit"
blank_template_path = os.path.join(audit_dir, "Template.docx")
temp_ss_path = "C:\\Users\\Stephan\\Downloads\\Old Screenshots\\Temp"
old_ss_path = "C:\\Users\\Stephan\\Downloads\\Old Screenshots"
e_packs_dir = "C:\\Users\\Stephan\\OneDrive\\Exercise Packs"

open_txtbk_dir = False
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
category = "Linear Algebra"
author = "Boyd"
textbook = "Introduction to Applied Linear Algebra"
edition = "1st"
#Leon-Garcia - Probability, Statistics, and Random Processes for EE - 3rd
