import io
import cv2
import datetime
import shutil
import tkinter as tk
from tkinter import simpledialog
from PIL import Image
from multiprocessing import Process, Queue
from Config import *

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

def resetImageList(sets_list, current_set_index):
    images = os.listdir(temp_ss_path)
    for image in images:
        shutil.move(os.path.join(temp_ss_path, image), os.path.join(sets_list[current_set_index][1], image))
    current_set_index += 1
    current_image_index = DEFAULT_FIRST_IMAGE_INDEX
    if current_set_index == len(sets_list):
        print("Finished.")
        print("------------------------------------------")
        exit()
    else:
        print("Starting image index: " + str(DEFAULT_FIRST_IMAGE_INDEX))
        print("Current image index: " + str(current_image_index))
        print("Current set: " + str(sets_list[current_set_index][0]))
        print(IMAGE_TYPE + " sets left: " + str(len(sets_list) - current_set_index))
        print("------------------------------------------")
    return current_image_index, current_set_index, {"current": []}

def extractImageRegions(queue_in):
    while True:
        if not queue_in.empty():
            image, bbox, annotation, current_set = queue_in.get()
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
                image_region_temp = image[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0]]
                image_region = cv2.cvtColor(image_region_temp, cv2.COLOR_BGRA2RGBA)
                buffer = io.BytesIO()
                Image.fromarray(image_region, 'RGBA').save(buffer, format='png')
                png_image = Image.open(buffer)
                combined_image_regions.paste(png_image, (0, last_im_height))
            elif annotation["append_to_last_saved_image"]:
                last_image = setImageName(current_set, annotation["index"])
                screenshot_top = Image.open(os.path.join(temp_ss_path, last_image))
                width = max([bbox[1][0] - bbox[0][0]] + [screenshot_top.size[0]])
                height = sum([bbox[1][1] - bbox[0][1]] + [screenshot_top.size[1]])
                combined_image_regions = Image.new('RGBA', (width, height), (255, 255, 255))
                combined_image_regions.paste(screenshot_top, (0, 0))
                last_im_height = screenshot_top.size[1]
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
                buffer = io.BytesIO()
                Image.fromarray(image_region, 'RGBA').save(buffer, format='png')
                png_image = Image.open(buffer)
                combined_image_regions.paste(png_image, (0, 0))
            image_name = setImageName(current_set, annotation["index"])
            combined_image_regions.save(os.path.join(temp_ss_path, image_name))
            print("Screenshot processed: " + str(annotation["index"]))
            print("------------------------------------------")


def setImageName(current_set, index):
    if IMAGE_TYPE == "Exercises":
        image_type = "Exercise"
    elif IMAGE_TYPE == "Solutions":
        image_type = "Solution"
    if current_set[0][1] == "00":
        image_name = str(current_set[0][0]) + " -- " + image_type + " " + str(index).zfill(3) + ".png"
    else:
        image_name = ".".join(current_set[0]) + " -- " + image_type + " " + str(index).zfill(3) + ".png"
    return image_name



queue = Queue(256)
process = Process(target=extractImageRegions, args=(queue,))
def processImageWithBBoxes(image, bboxes, annotations, current_set):
    try:
        process.start()
    except:
        pass
    for key, annotation in zip(annotations.keys(), annotations.values()):
        if annotation["shape"] != SHAPE_LINE and annotation["operation"] in [OP_SIMPLE, OP_APP_TO_LAST, OP_COMBINE_W_H]:
            queue.put([image, bboxes[key], annotation, current_set])
    return


