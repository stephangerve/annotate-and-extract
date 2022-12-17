import keyboard
import time
import pandas as pd
from LibAnnotate import *
from LibProcessImages import *
from LibDataframe import *
from Config import *








if __name__ == "__main__":

    one_column_boundary_set = False
    two_columns_boundary_set = False
    image_indices = []
    inc_wksht_df = pd.read_excel(os.path.join(audit_dir, "Incompleted Worksheets.xlsx"), engine='openpyxl', converters={'CN':str,'SN':str})
    sets_list, e_packs_txtbk_dir = addSetsList(category, author, textbook, edition, inc_wksht_df)
    if len(os.listdir(temp_ss_path)) == 0:
        current_set_index = 0
        current_image_index = DEFAULT_FIRST_IMAGE_INDEX
    else:
        chapter = os.listdir(temp_ss_path)[0].split(" -- ")[0].split(".")[0]
        if len(os.listdir(temp_ss_path)[0].split(" -- ")[0].split(".")) > 1:
            chapter = os.listdir(temp_ss_path)[0].split(" -- ")[0].split(".")[0]
            section = os.listdir(temp_ss_path)[0].split(" -- ")[0].split(".")[1]
        else:
            section = "00"
        if IMAGE_TYPE == "Exercises":
            set_dir = os.path.join(e_packs_txtbk_dir, "Exercises Images", chapter)
            current_set_index = sets_list.index([[chapter, section], os.path.join(e_packs_txtbk_dir, "Exercises Images", chapter)])
            if odds_only:
                current_image_index = int(os.listdir(temp_ss_path)[-1].split(" -- Exercise ")[1].split(".png")[0]) + 2
            else:
                current_image_index = int(os.listdir(temp_ss_path)[-1].split(" -- Exercise ")[1].split(".png")[0]) + 1
        elif IMAGE_TYPE == "Solutions":
            set_dir = os.path.join(e_packs_txtbk_dir, "Solutions Images", chapter)
            current_set_index = sets_list.index([[chapter, section], os.path.join(e_packs_txtbk_dir, "Solutions Images", chapter)])
            if odds_only:
                current_image_index = int(os.listdir(temp_ss_path)[-1].split(" -- Solution ")[1].split(".png")[0]) + 2
            else:
                current_image_index = int(os.listdir(temp_ss_path)[-1].split(" -- Solution ")[1].split(".png")[0]) + 1
    print("Starting image index: " + str(DEFAULT_FIRST_IMAGE_INDEX))
    print("Current image index: " + str(current_image_index))
    print("Current set: " + str(sets_list[current_set_index][0]))
    print(IMAGE_TYPE + " sets left: " + str(len(sets_list) - current_set_index))
    print("------------------------------------------")
    if edition != "1st":
        txtbk_dir = os.path.join(main_dir, category, " - ".join([author, textbook, edition]))
    else:
        txtbk_dir = os.path.join(main_dir, category, " - ".join([author, textbook]))
    files = os.listdir(os.path.join(txtbk_dir, "Textbook"))
    pdf_files = [file for file in files if ".pdf" in file]
    if open_txtbk_dir:
        os.startfile(os.path.join(txtbk_dir))
    if len(pdf_files) > 0:
        os.startfile(os.path.join(txtbk_dir, "Textbook", pdf_files[0]))
    header = {}
    print("Shortcuts active")
    print("------------------------------------------")
    outer_boundary = None
    while True:
        if keyboard.is_pressed('ctrl+shift+alt+1'):
            time.sleep(0.01)
            if two_columns_boundary_set:
                two_columns_boundary_set = False
            condition, image, bboxes, annotations, current_image_index, header = annotateOneColumn(OP_SIMPLE, one_column_boundary_set, two_columns_boundary_set, current_image_index, header, outer_boundary)
            if condition:
                processImageWithBBoxes(image, bboxes, annotations, sets_list[current_set_index])
        elif keyboard.is_pressed('ctrl+shift+alt+2'):
            time.sleep(0.01)
            if two_columns_boundary_set:
                two_columns_boundary_set = False
            if len(os.listdir(temp_ss_path)) != 0:
                condition, image, bboxes, annotations, current_image_index, header = annotateOneColumn(OP_APP_TO_LAST, one_column_boundary_set, two_columns_boundary_set, current_image_index, header, outer_boundary)
                if condition:
                    processImageWithBBoxes(image, bboxes, annotations, sets_list[current_set_index])
        elif keyboard.is_pressed('ctrl+shift+alt+3'):
            time.sleep(0.01)
            if two_columns_boundary_set:
                two_columns_boundary_set = False
            condition, image, bboxes, annotations, current_image_index, header = annotateOneColumn(OP_SET_HEADER, one_column_boundary_set, two_columns_boundary_set, current_image_index, header, outer_boundary)
            if condition:
                processImageWithBBoxes(image, bboxes, annotations, sets_list[current_set_index])
        elif keyboard.is_pressed('ctrl+shift+alt+4'):
            time.sleep(0.01)
            if two_columns_boundary_set:
                two_columns_boundary_set = False
            if len(header) != 0:
                condition, image, bboxes, annotations, current_image_index, header = annotateOneColumn(OP_COMBINE_W_H, one_column_boundary_set, two_columns_boundary_set, current_image_index, header, outer_boundary)
                if condition:
                    processImageWithBBoxes(image, bboxes, annotations, sets_list[current_set_index])
        elif keyboard.is_pressed('ctrl+shift+alt+5'):
            time.sleep(0.01)
            if two_columns_boundary_set:
                two_columns_boundary_set = False
            if len(header) != 0:
                condition, image, bboxes, annotations, current_image_index, header = annotateOneColumn(OP_APP_TO_HEAD, one_column_boundary_set, two_columns_boundary_set, current_image_index, header, outer_boundary)
                if condition:
                    processImageWithBBoxes(image, bboxes, annotations, sets_list[current_set_index])
        elif keyboard.is_pressed('ctrl+shift+alt+6'):
            time.sleep(0.01)
            if two_columns_boundary_set:
                two_columns_boundary_set = False
            condition, image, bboxes, annotations, current_image_index, header = annotateOneColumn(OP_GRID_MODE, one_column_boundary_set, two_columns_boundary_set, current_image_index, header, outer_boundary)
            if condition:
                processImageWithBBoxes(image, bboxes, annotations, sets_list[current_set_index])
        elif keyboard.is_pressed('ctrl+shift+alt+7'):
            time.sleep(0.01)
            if one_column_boundary_set:
                one_column_boundary_set = False
            condition, image, bboxes, annotations, current_image_index, header = annotateTwoColumns(7, one_column_boundary_set, two_columns_boundary_set, current_image_index, header, outer_boundary)
            if condition:
                processImageWithBBoxes(image, bboxes, annotations, sets_list[current_set_index])
        elif keyboard.is_pressed('ctrl+shift+alt+A'):
            time.sleep(0.01)
            if one_column_boundary_set:
                one_column_boundary_set = False
                outer_boundary = None
                print("Outer Boundary reset.")
            else:
                condition, outer_boundary, one_column_boundary_set, two_columns_boundary_set = setOneColumn()
                if condition is True:
                    one_column_boundary_set = True
                    two_columns_boundary_set = False
        elif keyboard.is_pressed('ctrl+shift+alt+B'):
            time.sleep(0.01)
            if two_columns_boundary_set:
                two_columns_boundary_set = False
            else:
                condition, one_column_boundary_set, two_columns_boundary_set = setTwoColumns()
                if condition is True:
                    two_columns_boundary_set = True
                    one_column_boundary_set = False
        elif keyboard.is_pressed('ctrl+shift+alt+z'):
            time.sleep(0.01)
            current_image_index, current_set_index, header = resetImageList(sets_list, current_set_index)



