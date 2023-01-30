import io
import cv2
import datetime
import shutil
import tkinter as tk
from tkinter import simpledialog
from PIL import Image
from multiprocessing import Process, Queue
from Config import *
import numpy as np

def emptyTempDir():
    files_in_temp = [file for file in os.listdir(temp_ss_path) if os.path.isfile(os.path.join(temp_ss_path, file))]
    count = 0
    if len(files_in_temp) > 0:
        for file in files_in_temp:
            shutil.move(os.path.join(temp_ss_path, file), os.path.join(old_ss_path, file))
            print("Moved " + file)
            count += 1
        print(str(count) + " screenshots moved from temp.")
        print("------------------------------------------")

def deleteLastScreenshot(screenshots_indices):
    global current_page_number
    if len(screenshots_indices) > 0:
        last_page_number = int(screenshots_indices[-1])
        screenshots_indices.pop(-1)
        files_in_temp = [file for file in os.listdir(temp_ss_path) if os.path.isfile(os.path.join(temp_ss_path, file))]
        shutil.move(os.path.join(temp_ss_path, files_in_temp[-1]), os.path.join(old_ss_path, files_in_temp[-1]))
        if len(screenshots_indices) > 0:
            current_page_number = int(screenshots_indices[-1]) + 1
        else:
            current_page_number = DEFAULT_FIRST_IMAGE_INDEX
        print("Last screenshot deleted: " + str(last_page_number))
        print("Current screenshot index set to " + str(current_page_number))
    else:
        print("No screenshots to delete.")
    print("------------------------------------------")

def resetImageList(current_image_index, sets_list, current_set_index, cursor, cnx, textbookid):
    if str(sets_list[current_set_index][0][0]).isdigit():
        CN = str(int(sets_list[current_set_index][0][0]))
    else:
        CN = sets_list[current_set_index][0][0]
    if str(sets_list[current_set_index][0][1]).isdigit():
        SN = str(int(sets_list[current_set_index][0][1]))
    else:
        SN = sets_list[current_set_index][0][1]
    images = os.listdir(temp_ss_path)
    if IMAGE_TYPE == "Exercises":
        for image in images:
            if "M" in image:
                shutil.move(os.path.join(temp_ss_path, image), os.path.join(sets_list[current_set_index][1]["masked"], image))
                m_exercise_path = os.path.join(sets_list[current_set_index][1]["masked"], image)
                m_exercise_rel_path = " -- ".join(m_exercise_path.split("Exercise Packs\\")[-1].split("\\"))
            elif "U" in image:
                shutil.move(os.path.join(temp_ss_path, image), os.path.join(sets_list[current_set_index][1]["unmasked"], image))
                eid = ".".join(image.split(".")[:-2])
                EN = int(image.split(".")[2])
                u_exercise_path = os.path.join(sets_list[current_set_index][1]["unmasked"], image)
                u_exercise_rel_path = " -- ".join(u_exercise_path.split("Exercise Packs\\")[-1].split("\\"))
                add_row = (textbookid, eid, CN, SN, EN, None, u_exercise_rel_path, m_exercise_rel_path, None)
                insert_row_statement = ("INSERT INTO exercises "
                                        "(TextbookID, ExerciseID, ChapterNumber, SectionNumber, ExerciseNumber, SolutionExists, UnmaskedExercisePath, MaskedExercisePath, SolutionPath)"
                                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
                cursor.execute(insert_row_statement, add_row)
                cnx.commit()
                print("Inserted row: " + str(add_row))
                m_exercise_rel_path = None
    elif IMAGE_TYPE == "Solutions":
        query = ("SELECT ExerciseID, ExerciseNumber FROM exercises WHERE TextbookID = '" + textbookid + "' AND ChapterNumber = '" + CN + "' AND SectionNumber = '" + SN + "'")
        cursor.execute(query)
        exist_rows = cursor.fetchall()
        eids = [entry[0] for entry in exist_rows]
        exercise_numbers = [entry[1] for entry in exist_rows]
        for eid, EN in zip(eids, exercise_numbers):
            sol_image = ".".join([eid, 'S', 'png'])
            if sol_image in images:
                if OVERWRITE_IMAGE:
                    shutil.move(os.path.join(temp_ss_path, sol_image), os.path.join(sets_list[current_set_index][1], sol_image))
                    #eid = ".".join(image.split(".")[:-2])
                    #EN = int(sol_image.split(".")[2])
                    solution_path = os.path.join(sets_list[current_set_index][1], sol_image)
                    solution_rel_path = " -- ".join(solution_path.split("Exercise Packs\\")[-1].split("\\"))
                    update_row = (textbookid, eid, CN, SN, EN, str(True), "*unchanged*", "*unchanged*", solution_rel_path)
                    update_row_statement = ("UPDATE exercises "
                                            "SET SolutionExists = 'True',"
                                            "    SolutionPath = '" + solution_rel_path + "' "
                                            "WHERE TextbookID = '" + textbookid + "' "
                                            "AND ExerciseID = '" + eid + "'")
                    cursor.execute(update_row_statement)
                    cnx.commit()
                    # add_row = (textbookid, eid, CN, SN, EN, str(True), None, None, solution_rel_path)
                    # insert_row_statement = ("INSERT INTO exercises "
                    #                         "(TextbookID, ExerciseID, ChapterNumber, SectionNumber, ExerciseNumber, SolutionExists, UnmaskedExercisePath, MaskedExercisePath, SolutionPath)"
                    #                         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
                    # cursor.execute(insert_row_statement, add_row)
                    # cnx.commit()
                    # print("Inserted row: " + str(add_row))
            else:
                update_row = (textbookid, eid, CN, SN, EN, str(False), "*unchanged*", "*unchanged*", None)
                update_row_statement = ("UPDATE exercises "
                                        "SET SolutionExists = 'False' "
                                        "WHERE TextbookID = '" + textbookid + "' "
                                        "AND ExerciseID = '" + eid + "'")
                cursor.execute(update_row_statement)
                cnx.commit()
            print("Updated row: " + str(update_row))

    if IMAGE_TYPE == "Exercises":
        update_row_statement = ("Update sections "
                                "SET AllExercisesExtracted = 'True' "
                                "WHERE TextbookID = '" + textbookid + "' "
                                "AND ChapterNumber = '" + CN + "' "
                                "AND SectionNumber = '" + SN + "'")
    elif IMAGE_TYPE == "Solutions":
        update_row_statement = ("Update sections "
                                "SET AllSolutionsExtracted = 'True' "
                                "WHERE TextbookID = '" + textbookid + "' "
                                "AND ChapterNumber = '" + CN + "' "
                                "AND SectionNumber = '" + SN + "'")
    cursor.execute(update_row_statement)
    cnx.commit()
    current_set_index += 1
    if current_set_index == len(sets_list):
        print("Finished.")
        print("------------------------------------------")
        exit()
    else:
        if sets_list[current_set_index - 1][0][0] == sets_list[current_set_index][0][0]:
            if continue_from_last_ss_index is False:
                current_image_index = DEFAULT_FIRST_IMAGE_INDEX
        else:
            current_image_index = DEFAULT_FIRST_IMAGE_INDEX
        print("Starting image index: " + str(DEFAULT_FIRST_IMAGE_INDEX))
        print("Current image index: " + str(current_image_index))
        print("Current set: " + str(sets_list[current_set_index][0]))
        print(IMAGE_TYPE + " sets left: " + str(len(sets_list) - current_set_index))
        print("------------------------------------------")
    return current_image_index, current_set_index, {"current": []}

def extractImageRegions(queue_in):
    while True:
        if not queue_in.empty():
            image, bbox, mask, annotation, current_set = queue_in.get()
            if annotation["operation"] == OP_COMBINE_W_H and len(annotation["header"]) != 0:
                header_pngs = []
                for part_image in annotation["header"]:
                    image_region = cv2.cvtColor(part_image, cv2.COLOR_BGRA2RGBA)
                    buffer = io.BytesIO()
                    Image.fromarray(image_region, 'RGBA').save(buffer, format='png')
                    header_pngs.append(Image.open(buffer))
                width = max([bbox[1][0] - bbox[0][0]] + [header_png.size[0] for header_png in header_pngs])
                height = sum([bbox[1][1] - bbox[0][1]] + [header_png.size[1] for header_png in header_pngs])
                combined_image_regions = Image.new('RGBA', (width, height), (255, 255, 255))
                last_im_height = 0
                for header_png in header_pngs:
                    combined_image_regions.paste(header_png, (0, last_im_height))
                    last_im_height += header_png.size[1]
                if IMAGE_TYPE == "Exercises":
                    masked_image = combined_image_regions.copy()
                image_region_temp = image[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0]]
                image_region = cv2.cvtColor(image_region_temp, cv2.COLOR_BGRA2RGBA)
                buffer = io.BytesIO()
                Image.fromarray(image_region, 'RGBA').save(buffer, format='png')
                png_image = Image.open(buffer)
                combined_image_regions.paste(png_image, (0, last_im_height))
                if IMAGE_TYPE == "Exercises":
                    masked_region_temp = np.full((mask[1][1] - mask[0][1], mask[1][0] - mask[0][0], 4), 255, dtype=np.uint8)
                    masked_region = cv2.cvtColor(masked_region_temp, cv2.COLOR_BGRA2RGBA)
                    buffer_mask = io.BytesIO()
                    Image.fromarray(masked_region, 'RGBA').save(buffer_mask, format='png')
                    png_mask = Image.open(buffer_mask)
                    masked_image.paste(png_image, (0, last_im_height))
                    masked_image.paste(png_mask, (0, last_im_height))
            elif annotation["append_to_last_saved_image"]:
                if IMAGE_TYPE == "Exercises":
                    last_image_masked = setImageName(current_set, annotation["index"], "masked")
                    screenshot_top_masked = Image.open(os.path.join(temp_ss_path, last_image_masked))
                    width = max([bbox[1][0] - bbox[0][0]] + [screenshot_top_masked.size[0]])
                    height = sum([bbox[1][1] - bbox[0][1]] + [screenshot_top_masked.size[1]])
                    masked_image = Image.new('RGBA', (width, height), (255, 255, 255))
                    masked_image.paste(screenshot_top_masked, (0, 0))
                    last_im_height = screenshot_top_masked.size[1]
                    image_region_temp = image[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0]]
                    image_region = cv2.cvtColor(image_region_temp, cv2.COLOR_BGRA2RGBA)
                    buffer = io.BytesIO()
                    Image.fromarray(image_region, 'RGBA').save(buffer, format='png')
                    png_image = Image.open(buffer)
                    masked_image.paste(png_image, (0, last_im_height))
                #Unmasked
                last_image_unmasked = setImageName(current_set, annotation["index"], "unmasked")
                screenshot_top_unmasked = Image.open(os.path.join(temp_ss_path, last_image_unmasked))
                width = max([bbox[1][0] - bbox[0][0]] + [screenshot_top_unmasked.size[0]])
                height = sum([bbox[1][1] - bbox[0][1]] + [screenshot_top_unmasked.size[1]])
                combined_image_regions = Image.new('RGBA', (width, height), (255, 255, 255))
                combined_image_regions.paste(screenshot_top_unmasked, (0, 0))
                last_im_height = screenshot_top_unmasked.size[1]
                image_region_temp = image[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0]]
                image_region = cv2.cvtColor(image_region_temp, cv2.COLOR_BGRA2RGBA)
                buffer = io.BytesIO()
                Image.fromarray(image_region, 'RGBA').save(buffer, format='png')
                png_image = Image.open(buffer)
                combined_image_regions.paste(png_image, (0, last_im_height))
            else:
                width = bbox[1][0] - bbox[0][0]
                height = bbox[1][1] - bbox[0][1]
                combined_image_regions = Image.new('RGBA', (width, height), (255, 255, 255))
                image_region_temp = image[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0]]
                image_region = cv2.cvtColor(image_region_temp, cv2.COLOR_BGRA2RGBA)
                buffer_image = io.BytesIO()
                Image.fromarray(image_region, 'RGBA').save(buffer_image, format='png')
                png_image = Image.open(buffer_image)
                combined_image_regions.paste(png_image, (0, 0))
                if IMAGE_TYPE == "Exercises":
                    masked_region_temp = np.full((mask[1][1] - mask[0][1], mask[1][0] - mask[0][0], 4), 255, dtype=np.uint8)
                    masked_region = cv2.cvtColor(masked_region_temp, cv2.COLOR_BGRA2RGBA)
                    buffer_mask = io.BytesIO()
                    Image.fromarray(masked_region, 'RGBA').save(buffer_mask, format='png')
                    png_mask = Image.open(buffer_mask)
                    masked_image = Image.new('RGBA', (width, height), (255, 255, 255))
                    masked_image.paste(png_image, (0, 0))
                    masked_image.paste(png_mask, (0, 0))
            if IMAGE_TYPE == "Exercises":
                masked_image_name = setImageName(current_set, annotation["index"], "masked")
                masked_image.save(os.path.join(temp_ss_path, masked_image_name))
            unmasked_image_name = setImageName(current_set, annotation["index"], "unmasked")
            combined_image_regions.save(os.path.join(temp_ss_path, unmasked_image_name))
            print("Screenshot processed: " + str(annotation["index"]))
            print("------------------------------------------")


def setImageName(current_set, index, mask_type):
    if IMAGE_TYPE == "Exercises":
        if mask_type == "masked":
            image_type = "M"
        elif mask_type == "unmasked":
            image_type = "U"
    elif IMAGE_TYPE == "Solutions":
        image_type = "S"
    if current_set[0][1] == "00":
        image_name = ".".join([str(current_set[0][0]), "00", str(index).zfill(3), image_type, "png"])
    else:
        image_name = ".".join([current_set[0][0], current_set[0][1], str(index).zfill(3), image_type, "png"])
    return image_name



queue = Queue(256)
process = Process(target=extractImageRegions, args=(queue,))
def processImageWithBBoxes(image, bboxes, masks, annotations, current_set):
    try:
        process.start()
    except:
        pass
    for key, annotation in zip(annotations.keys(), annotations.values()):
        if annotation["shape"] != SHAPE_LINE:
            if annotation["operation"] in [OP_SIMPLE, OP_COMBINE_W_H]:
                if IMAGE_TYPE == "Exercises":
                    queue.put([image, bboxes[key], masks[key], annotation, current_set])
                else:
                    queue.put([image, bboxes[key], None, annotation, current_set])
            elif annotation["operation"] == OP_APP_TO_LAST:
                queue.put([image, bboxes[key], None, annotation, current_set])
    return


