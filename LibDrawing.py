import cv2
import time
import keyboard
import random
import string
import numpy as np
import pytesseract
from pytesseract import Output
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#from LibDrawingCoordinates import *
from Config import *

x_cursor, y_cursor = 0, 0
x_start, y_start, x_end, y_end = 0, 0, 0, 0
label_x_start, label_y_start, label_x_end, label_y_end = 0, 0, 0, 0
sc_x_center, sc_y_center = 0, 0
drawing_boundary = False
drawing_bbox = False
drawing = False
drawing_column_line = False
drawing_subcolumns = False
drawing_sc_rows = False
drawing_grid_outer_boundary = False
drawing_grid_column_bboxes = False
drawing_one_gcb = False
outer_boundary = [(0, 0), (0, 0)]
column_line = [(0, 0), (0, 0)]
header = []
one_column_boundary_set = False
two_columns_boundary_set = False
last_annotate_mode = None
last_color = None
label_ready = False
mask_x_offset = 20
mask_y_offset = 20
drawing_mask = False
im_bnd_gray = None
mask_offset_found = False
white_columns = None
grid_scan_mode = None
automatic_bbox_detect_mode = False

bboxes = {}
grid_col_bboxes = []
grid_row_lines =[]
masks = {}
screenshots = []


annotations = {}
#shape
#index
#operation
#grid

def drawBBoxes(orig_image, image, boundary, command, prev_bboxes, prev_masks, last_image_index, last_annotations, last_header, column_pos=None):
    global drawing_bbox
    global drawing
    global last_annotate_mode, last_color
    global bboxes, masks, header
    global x_start, y_start, x_end, y_end
    global label_x_start, label_y_start, label_x_end, label_y_end
    global current_image_index
    global label_ready
    global annotations
    global mask_x_offset, mask_y_offset
    global im_bnd_gray
    global mask_offset_found
    global automatic_bbox_detect_mode
    orig_image_w_outer_boundary = image.copy()
    grid_ordering = "horizontal"
    drawing = True
    scan_mode = True
    if len(last_annotations) == 0:
        annotations = {}
    else:
        annotations = last_annotations
    if len(last_header) == None:
        header = last_header
    if len(prev_bboxes) > 0:
        bboxes = prev_bboxes
        if annotations[list(bboxes.keys())[-1]]["column_pos"] != column_pos and column_pos in [COLUMN_LEFT, COLUMN_RIGHT]:
            code = generateCode()
            bboxes[code] = [(boundary[0][0], boundary[0][1]), (boundary[1][0], boundary[0][1])]
            addAnnotation(code=code, shape=SHAPE_LINE, operation=None, column_pos=column_pos, index=None)
    else:
        bboxes = {}
    if len(prev_masks) > 0:
        masks = prev_masks
    else:
        masks = {}
    if len(annotations) != 0:
        for key, bbox in zip(bboxes.keys(), bboxes.values()):
            if annotations[key]["shape"] != SHAPE_LINE:
                color = BBOX_COLOR[annotations[key]["operation"]]
                cv2.rectangle(image, bbox[0], bbox[1], color, 2)
                if IMAGE_TYPE == "Exercises" and annotations[key]["operation"] in [OP_SIMPLE, OP_COMBINE_W_H]:
                    mask = masks[key]
                    if annotations[key]["grid"]:
                        mask_width = (mask[1][0] - mask[0][0])
                        im_region = image[mask[0][1]:mask[1][1], bbox[0][0]:bbox[0][0] + mask_width]
                        white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                        masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                        image[mask[0][1]:mask[1][1], bbox[0][0]:bbox[0][0] + mask_width] = masked_reg
                        cv2.rectangle(image, (bbox[0][0], mask[0][1]), (bbox[0][0] + mask_width, mask[1][1]), color, 1)
                    else:
                        im_region = image[mask[0][1]:mask[1][1], mask[0][0]:mask[1][0]]
                        white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                        masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                        image[mask[0][1]:mask[1][1], mask[0][0]:mask[1][0]] = masked_reg
                        cv2.rectangle(image, mask[0], mask[1], color, 1)
                x_0, y_0, x_1, y_1 = bbox[0][0], bbox[0][1], bbox[0][0], bbox[0][1]
                label_x_start, label_y_start, label_x_end, label_y_end = x_0 - 28, y_0, x_1 - 2, y_1 + 20
                cv2.rectangle(image, (label_x_start, label_y_start), (label_x_end, label_y_end), color, -1)
                if annotations[key]["operation"] in [OP_SET_HEADER, OP_APP_TO_HEAD]:
                    label_str = "HEAD"
                    font_size = 0.30
                else:
                    label_str = str(annotations[key]["index"]).zfill(3)
                    font_size = 0.40
                cv2.putText(image, label_str, (label_x_start + 2, label_y_start + 14), cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 255, 255), 1, cv2.LINE_AA)
    if last_image_index != -1:
        current_image_index = last_image_index
    else:
        current_image_index = DEFAULT_FIRST_IMAGE_INDEX
    if command not in STANDARD_OPs:
        annotate_mode = OP_SIMPLE
    elif command == OP_APP_TO_LAST and len(os.listdir(temp_ss_path)) == 0:
        annotate_mode = OP_SIMPLE
    elif command == OP_APP_TO_LAST and len(os.listdir(temp_ss_path)) > 0:
        annotate_mode = OP_APP_TO_LAST
        if odds_only:
            current_image_index -= 2
        else:
            current_image_index -= 1
    elif command == OP_COMBINE_W_H and len(last_header) == 0:
        annotate_mode = OP_SIMPLE
    else:
        annotate_mode = command
    # if command != OP_GRID_MODE:
    #     last_annotate_mode = command
    # cv2.setMouseCallback("image", setBBOXCoordiates, [boundary])
    im_bnd_gray = cv2.cvtColor(orig_image, cv2.COLOR_BGR2GRAY)
    bbox_outer_boundary = boundary
    cv2.setMouseCallback("image", scanAndSetBBOXCoordiates, [bbox_outer_boundary])
    drawing_bbox = True
    image_w_new_bbox = image.copy()
    while drawing:
        image_w_new_bbox = image.copy()
        if annotate_mode in BBOX_COLOR.keys():
            color = BBOX_COLOR[annotate_mode]
            if annotate_mode in [OP_SIMPLE, OP_COMBINE_W_H]:
                last_annotate_mode = annotate_mode
        else:
            color = RED
        if annotate_mode != OP_GRID_MODE:
            if automatic_bbox_detect_mode:
                condition, image = setBBoxesAutomatically(orig_image, image, boundary, annotate_mode, column_pos)########################################################################################################################################################
                automatic_bbox_detect_mode = False
            else:
                if drawing_bbox is True:
                    cv2.rectangle(image_w_new_bbox, (x_start, y_start), (x_end, y_end), color, 1)
                if label_ready:
                    cv2.rectangle(image_w_new_bbox, (label_x_start, label_y_start), (label_x_end, label_y_end), color, -1)
                    if annotate_mode == OP_SET_HEADER or annotate_mode == OP_APP_TO_HEAD:
                        label_str = "HEAD"
                        font_size = 0.30
                    else:
                        label_str = str(current_image_index).zfill(3)
                        font_size = 0.40
                    cv2.putText(image_w_new_bbox, label_str, (label_x_start + 2, label_y_start + 14), cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 255, 255), 1, cv2.LINE_AA)
                    if IMAGE_TYPE == "Exercises" and annotate_mode in [OP_SIMPLE, OP_COMBINE_W_H]:
                        mask_x_start, mask_y_start, mask_x_end, mask_y_end = x_start, y_start, x_start + mask_x_offset, y_start + mask_y_offset
                        if mask_y_end >= y_end:
                            im_region = image_w_new_bbox[mask_y_start:y_end, mask_x_start:mask_x_end]
                            white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                            masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                            image_w_new_bbox[mask_y_start:y_end, mask_x_start:mask_x_end] = masked_reg
                            cv2.rectangle(image_w_new_bbox, (mask_x_start, mask_y_start), (mask_x_end, y_end), color, 1)
                        else:
                            im_region = image_w_new_bbox[mask_y_start:mask_y_end, mask_x_start:mask_x_end]
                            white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                            masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                            image_w_new_bbox[mask_y_start:mask_y_end, mask_x_start:mask_x_end] = masked_reg
                            cv2.rectangle(image_w_new_bbox, (mask_x_start, mask_y_start), (mask_x_end, mask_y_end), color, 1)
                cv2.imshow("image", image_w_new_bbox)
                cv2.waitKey(1)
        else:
            if annotate_mode == OP_APP_TO_LAST:
                if last_annotate_mode is not None:
                    annotate_mode = last_annotate_mode
            elif annotate_mode in [OP_SET_HEADER, OP_APP_TO_HEAD]:
                annotate_mode = OP_COMBINE_W_H
            elif annotate_mode == OP_GRID_MODE:
                if last_annotate_mode is not None:
                    annotate_mode = last_annotate_mode
            if len(bboxes) > 0:
                condition, image, sc_boundary, sc_annotate_mode = drawSubcolumns2(image_w_new_bbox, [(list(bboxes.values())[-1][0][0], list(bboxes.values())[-1][1][1]), (boundary[1][0], boundary[1][1])], annotate_mode, grid_ordering, column_pos)
            else:
                condition, image, sc_boundary, sc_annotate_mode = drawSubcolumns2(image_w_new_bbox, boundary, annotate_mode, grid_ordering, column_pos)
            if condition is False:
                if annotate_mode == OP_GRID_MODE and last_annotate_mode == None:
                    annotate_mode = OP_SIMPLE
                else:
                    if last_annotate_mode is not None:
                        annotate_mode = last_annotate_mode
                    # cv2.setMouseCallback("image", setBBOXCoordiates, [boundary])
                    bbox_outer_boundary = boundary
                    cv2.setMouseCallback("image", scanAndSetBBOXCoordiates, [bbox_outer_boundary])
                if len(bboxes) > 0:
                    # cv2.setMouseCallback("image", setBBOXCoordiates, [[(list(bboxes.values())[-1][0][0], list(bboxes.values())[-1][1][1]), (boundary[1][0], boundary[1][1])]])
                    bbox_outer_boundary = [(list(bboxes.values())[-1][0][0], list(bboxes.values())[-1][1][1]), (boundary[1][0], boundary[1][1])]
                    cv2.setMouseCallback("image", scanAndSetBBOXCoordiates, [bbox_outer_boundary])
                else:
                    # cv2.setMouseCallback("image", setBBOXCoordiates, [boundary])
                    bbox_outer_boundary = boundary
                    cv2.setMouseCallback("image", scanAndSetBBOXCoordiates, [bbox_outer_boundary])
            else:
                annotate_mode = sc_annotate_mode
                if drawing is False:
                    image_w_new_bbox = image
                else:
                    # cv2.setMouseCallback("image", setBBOXCoordiates, [[(sc_boundary[0][0], sc_boundary[1][1]), (boundary[1][0], boundary[1][1])]])
                    bbox_outer_boundary = [(sc_boundary[0][0], sc_boundary[1][1]), (boundary[1][0], boundary[1][1])]
                    cv2.setMouseCallback("image", scanAndSetBBOXCoordiates, [bbox_outer_boundary])

        if drawing_bbox is False:
            if annotate_mode == OP_SIMPLE:
                code = generateCode()
                bboxes[code] = [(x_start, y_start), (x_end, y_end)]
                if IMAGE_TYPE == "Exercises":
                    if mask_y_end >= y_end:
                        masks[code] = [(mask_x_start, mask_y_start), (mask_x_end, y_end)]
                    else:
                        masks[code] = [(mask_x_start, mask_y_start), (mask_x_end, mask_y_end)]
                addAnnotation(code=code, shape=SHAPE_BBOX, operation=OP_SIMPLE, column_pos=column_pos, index=current_image_index)
                if odds_only:
                    current_image_index += 2
                else:
                    current_image_index += 1
            elif annotate_mode == OP_APP_TO_LAST:
                code = generateCode()
                bboxes[code] = [(x_start, y_start), (x_end, y_end)]
                addAnnotation(code=code, shape=SHAPE_BBOX, operation=OP_APP_TO_LAST, column_pos=column_pos, index=current_image_index, append_to_last_saved_image=True)
                if odds_only:
                    current_image_index += 2
                else:
                    current_image_index += 1
            elif annotate_mode == OP_SET_HEADER:
                header_bbox = [(x_start, y_start), (x_end, y_end)]
                header = []
                header.append(orig_image[header_bbox[0][1]:header_bbox[1][1], header_bbox[0][0]:header_bbox[1][0]])
                code = generateCode()
                bboxes[code] = [(x_start, y_start), (x_end, y_end)]
                addAnnotation(code=code, shape=SHAPE_BBOX, operation=OP_SET_HEADER, column_pos=column_pos, index=None)
            elif annotate_mode == OP_COMBINE_W_H:
                code = generateCode()
                bboxes[code] = [(x_start, y_start), (x_end, y_end)]
                if IMAGE_TYPE == "Exercises":
                    if mask_y_end >= y_end:
                        masks[code] = [(mask_x_start, mask_y_start), (mask_x_end, y_end)]
                    else:
                        masks[code] = [(mask_x_start, mask_y_start), (mask_x_end, mask_y_end)]
                addAnnotation(code=code, shape=SHAPE_BBOX, operation=OP_COMBINE_W_H, column_pos=column_pos, index=current_image_index, header=header)
                if odds_only:
                    current_image_index += 2
                else:
                    current_image_index += 1
            elif annotate_mode == OP_APP_TO_HEAD: #in the future you will have amend this to account for parts of the header taken on different pages
                header_bbox = [(x_start, y_start), (x_end, y_end)]
                header.append(orig_image[header_bbox[0][1]:header_bbox[1][1], header_bbox[0][0]:header_bbox[1][0]])
                code = generateCode()
                bboxes[code] = header_bbox
                addAnnotation(code=code, shape=SHAPE_BBOX, operation=OP_APP_TO_HEAD, column_pos=column_pos, index=None)
            cv2.rectangle(image_w_new_bbox, (x_start, y_start), (x_end, y_end), color, 2)
            cv2.imshow("image", image_w_new_bbox)
            cv2.waitKey(1)
            if annotate_mode == OP_APP_TO_LAST:
                if last_annotate_mode is not None:
                    annotate_mode = last_annotate_mode
                else:
                    annotate_mode = OP_SIMPLE
            elif annotate_mode == OP_SET_HEADER:
                annotate_mode = OP_COMBINE_W_H
            elif annotate_mode == OP_APP_TO_HEAD:
                annotate_mode = OP_COMBINE_W_H
            image = image_w_new_bbox
            drawing_bbox = True
            label_ready = False
            mask_offset_found = False

        if keyboard.is_pressed('ctrl+shift+alt+1'):
            time.sleep(0.01)
            if annotate_mode != OP_SIMPLE:
                if annotate_mode == OP_APP_TO_LAST:
                    if odds_only:
                        current_image_index += 2
                    else:
                        current_image_index += 1
                annotate_mode = OP_SIMPLE
        elif keyboard.is_pressed('ctrl+shift+alt+2'):
            time.sleep(0.01)
            if annotate_mode != OP_APP_TO_LAST:
                last_annotate_mode = annotate_mode
                if len(os.listdir(temp_ss_path)) == 0 and len(bboxes) == 0:
                    annotate_mode = OP_SIMPLE
                else:
                    annotate_mode = OP_APP_TO_LAST
                    if odds_only:
                        current_image_index -= 2
                    else:
                        current_image_index -= 1
        elif keyboard.is_pressed('ctrl+shift+alt+3'):
            time.sleep(0.01)
            if annotate_mode != OP_SET_HEADER :
                if annotate_mode == OP_APP_TO_LAST:
                    if odds_only:
                        current_image_index += 2
                    else:
                        current_image_index += 1
                annotate_mode = OP_SET_HEADER
        elif keyboard.is_pressed('ctrl+shift+alt+4'):
            time.sleep(0.01)
            if annotate_mode != OP_COMBINE_W_H:
                if annotate_mode == OP_APP_TO_LAST:
                    if odds_only:
                        current_image_index += 2
                    else:
                        current_image_index += 1
                if len(header) == 0:
                    annotate_mode = OP_SIMPLE
                else:
                    annotate_mode = OP_COMBINE_W_H
        elif keyboard.is_pressed('ctrl+shift+alt+5'):
            time.sleep(0.01)
            if annotate_mode != OP_APP_TO_HEAD :
                if annotate_mode == OP_APP_TO_LAST:
                    if odds_only:
                        current_image_index += 2
                    else:
                        current_image_index += 1
                if len(header) == 0:
                    annotate_mode = OP_SIMPLE
                else:
                    annotate_mode = OP_APP_TO_HEAD
        elif keyboard.is_pressed('ctrl+shift+alt+6'):
            time.sleep(0.01)
            if annotate_mode != OP_GRID_MODE:
                if annotate_mode == OP_APP_TO_LAST:
                    if odds_only:
                        current_image_index += 2
                    else:
                        current_image_index += 1
                if annotate_mode != OP_GRID_MODE:
                    last_annotate_mode = annotate_mode
                annotate_mode = OP_GRID_MODE
        elif keyboard.is_pressed('ctrl+shift+alt+8'):
            while keyboard.is_pressed('ctrl+shift+alt+8'):
                continue
            code = generateCode()
            bboxes[code] = [(x_start, y_end), (x_end, y_end)]
            addAnnotation(code=code, shape=SHAPE_LINE, operation=8, column_pos=column_pos, index=None)
            cv2.imshow("image", image)
            cv2.waitKey(1)
            x_start, y_start, x_end, y_end = 0, 0, 0, 0
            label_x_start, label_y_start, label_x_end, label_y_end = 0, 0, 0, 0
        elif keyboard.is_pressed('ctrl+shift+alt+9'):
            while keyboard.is_pressed('ctrl+shift+alt+9'):
                continue
            if len(bboxes) > 0:
                minimum = 0
                for key in reversed(annotations):
                    if annotations[key]["index"] != None:
                        minimum = annotations[key]["index"]
                if current_image_index - 1 > minimum:
                    if odds_only:
                        current_image_index -= 2
                    else:
                        current_image_index -= 1
        elif keyboard.is_pressed('ctrl+shift+alt+0'):
            while keyboard.is_pressed('ctrl+shift+alt+0'):
                continue
            if odds_only:
                current_image_index += 2
            else:
                current_image_index += 1
        elif keyboard.is_pressed('ctrl+shift+alt+x'):
            while keyboard.is_pressed('ctrl+shift+alt+x'):
                continue
            if scan_mode:
                scan_mode = False
                cv2.setMouseCallback("image", setBBOXCoordiates, [bbox_outer_boundary])
            else:
                scan_mode = True
                cv2.setMouseCallback("image", scanAndSetBBOXCoordiates, [bbox_outer_boundary])
        elif keyboard.is_pressed('ctrl+shift+alt+y'):
            while keyboard.is_pressed('ctrl+shift+alt+y'):
                continue
            automatic_bbox_detect_mode = not automatic_bbox_detect_mode
            print("automatic_bbox_detect_mode set to: " + str(automatic_bbox_detect_mode))

        # elif keyboard.is_pressed('ctrl+shift+alt+y'):
        #     while keyboard.is_pressed('ctrl+shift+alt+y'):
        #         continue
        #     if grid_ordering == "horizontal":
        #         grid_ordering = "vertical"
        #     elif grid_ordering == "vertical":
        #         grid_ordering = "horizontal"
        #     print("grid ordering: " + grid_ordering)
        elif keyboard.is_pressed('ctrl+shift+alt+z'):
            while keyboard.is_pressed('ctrl+shift+alt+z'):
                continue
        # elif keyboard.is_pressed('ctrl+shift+alt+C'):
        #     if mask_x_end - 1 > x_start:
        #         mask_x_offset -= 1
        # elif keyboard.is_pressed('ctrl+shift+alt+G'):
        #     if mask_x_end + 1 < x_end:
        #         mask_x_offset += 1
        # elif keyboard.is_pressed('ctrl+shift+alt+E'):
        #     if mask_y_end - 1 > y_start:
        #         mask_y_offset -= 1
        # elif keyboard.is_pressed('ctrl+shift+alt+F'):
        #     if mask_y_end + 1 < y_end:
        #         mask_y_offset += 1
        elif keyboard.is_pressed('esc'):
            while keyboard.is_pressed('esc'):
                continue
            if len(bboxes) == 0:
                drawing = False
                mask_offset_found = False
                print("Canceled.")
                return False, None, None, [], [], annotations, last_image_index, header
            else:
                undo_code = list(annotations.keys())[-1]
                undo_annotation = annotations.pop(undo_code)
                bboxes.pop(list(bboxes.keys())[-1])
                if undo_annotation["shape"] == SHAPE_LINE:
                    if len(annotations) > 0:
                        undo_code = list(annotations.keys())[-1]
                        undo_annotation = annotations.pop(undo_code)
                        bboxes.pop(list(bboxes.keys())[-1])
                    if len(annotations) > 0 \
                    and annotations[list(annotations.keys())[-1]]["column_pos"] != column_pos \
                    and column_pos in [COLUMN_LEFT, COLUMN_RIGHT]:
                        mask_offset_found = False
                        return False, None, undo_annotation["operation"], bboxes, masks, annotations, undo_annotation["index"], header
                if undo_annotation["operation"] in [OP_SIMPLE, OP_APP_TO_LAST, OP_COMBINE_W_H]:
                    if undo_annotation["grid"] is True:
                        for key in reversed(list(annotations.keys())):
                            if annotations[key]["grid"] == True:
                                bboxes.pop(key)
                                if IMAGE_TYPE == "Exercises":
                                    masks.pop(key)
                                current_image_index = annotations.pop(key)["index"]
                            else:
                                annotations.pop(list(annotations.keys())[-1])
                                bboxes.pop(list(bboxes.keys())[-1])
                                break
                    else:
                        current_image_index = undo_annotation["index"]
                elif undo_annotation["operation"] == OP_SET_HEADER:
                    header = []
                elif undo_annotation["operation"] == OP_APP_TO_HEAD:
                    header.pop(-1)
                if undo_annotation["operation"] in STANDARD_OPs:
                    annotate_mode = undo_annotation["operation"]
                image = orig_image_w_outer_boundary.copy()
                for key, bbox in zip(bboxes.keys(), bboxes.values()):
                    if annotations[key]["shape"] != SHAPE_LINE:
                        color = BBOX_COLOR[annotations[key]["operation"]]
                        cv2.rectangle(image, bbox[0], bbox[1], color, 2)
                        if IMAGE_TYPE == "Exercises" and annotations[key]["operation"] in [OP_SIMPLE, OP_COMBINE_W_H]:
                            mask = masks[key]
                            if annotations[key]["grid"]:
                                mask_width = (mask[1][0] - mask[0][0])
                                im_region = image[mask[0][1]:mask[1][1], bbox[0][0]:bbox[0][0] + mask_width]
                                white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                                masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                                image[mask[0][1]:mask[1][1], bbox[0][0]:bbox[0][0] + mask_width] = masked_reg
                                cv2.rectangle(image, (bbox[0][0], mask[0][1]), (bbox[0][0] + mask_width, mask[1][1]), color, 1)
                            else:
                                im_region = image[mask[0][1]:mask[1][1], mask[0][0]:mask[1][0]]
                                white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                                masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                                image[mask[0][1]:mask[1][1], mask[0][0]:mask[1][0]] = masked_reg
                                cv2.rectangle(image, mask[0], mask[1], color, 1)
                        x_0, y_0, x_1, y_1 = bbox[0][0], bbox[0][1], bbox[0][0], bbox[0][1]
                        label_x_start, label_y_start, label_x_end, label_y_end = x_0 - 28, y_0, x_1 - 2, y_1 + 20
                        cv2.rectangle(image, (label_x_start, label_y_start), (label_x_end, label_y_end), color, -1)
                        if annotations[key]["operation"] in [OP_SET_HEADER, OP_APP_TO_HEAD]:
                            label_str = "HEAD"
                            font_size = 0.30
                        else:
                            label_str = str(annotations[key]["index"]).zfill(3)
                            font_size = 0.40
                        cv2.putText(image, label_str, (label_x_start + 2, label_y_start + 14), cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.imshow("image", image)
                cv2.waitKey(1)
                x_start, y_start, x_end, y_end = 0, 0, 0, 0
                label_x_start, label_y_start, label_x_end, label_y_end = 0, 0, 0, 0
                # cv2.setMouseCallback("image", setBBOXCoordiates, [boundary])
                bbox_outer_boundary = boundary
                cv2.setMouseCallback("image", scanAndSetBBOXCoordiates, [bbox_outer_boundary])
    return True, image_w_new_bbox, annotate_mode, bboxes, masks, annotations, current_image_index, header

def drawSubcolumns2(image, boundary, annotate_mode, grid_ordering, column_pos=None):
    global x_start, y_start, x_end, y_end
    global drawing_grid_outer_boundary
    global drawing_grid_column_bboxes, drawing_one_gcb
    global drawing_grid_row_lines, drawing_one_grl
    global grid_col_bboxes
    global grid_row_lines
    global current_image_index
    global drawing
    global label_ready
    global white_columns
    global grid_scan_mode
    # 0. Initialize
    grid_scan_mode = True
    grid_col_bboxes = []
    grid_col_masks = []
    grid_row_lines = []
    old_image_index = current_image_index
    cv2.setMouseCallback("image", SASGridOuterBoundary, [boundary])
    drawing_grid_outer_boundary = True
    image_w_gob = image.copy()
    line_bbox = [(boundary[0][0], boundary[0][1]), (boundary[1][0], boundary[0][1])]
    if annotate_mode == OP_GRID_MODE:
        annotate_mode = OP_SIMPLE
    x_0, y_0, x_1, y_1 = boundary[0][0], boundary[0][1], boundary[0][0], boundary[0][1]
    l_x_0, l_y_0, l_x_1, l_y_1 = x_0 - 28, y_0, x_1 - 2, y_1 + 20


    # 1. Set outer boundary
    while drawing_grid_outer_boundary:
        image_w_gob = image.copy()
        cv2.rectangle(image_w_gob, (l_x_0, l_y_0), (l_x_1, l_y_1), GREEN, -1)
        cv2.putText(image_w_gob, "GRID", (l_x_0 + 2, l_y_0 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.30, WHITE, 1, cv2.LINE_AA)
        cv2.rectangle(image_w_gob, line_bbox[0], (x_end, y_end), GREEN, 1)
        cv2.imshow("image", image_w_gob)
        cv2.waitKey(1)
        if keyboard.is_pressed('esc'):
            time.sleep(0.5)
            drawing_grid_outer_boundary = False
            print("Canceled.")
            return False, image, None, None
    grid_outer_boundary = [line_bbox[0], (x_end, y_end)]
    cv2.rectangle(image_w_gob, (l_x_0, l_y_0), (l_x_1, l_y_1), GREEN, -1)
    cv2.putText(image_w_gob, "GRID", (l_x_0 + 2, l_y_0 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.30, WHITE, 1, cv2.LINE_AA)
    cv2.rectangle(image_w_gob, grid_outer_boundary[0], grid_outer_boundary[1], GREEN, 2)
    cv2.imshow("image", image_w_gob)
    cv2.waitKey(1)

    # 2. Set column bounding boxes along with masks
    cv2.setMouseCallback("image", SASGridColumnBBoxes, [grid_outer_boundary])
    image_w_gcb = image_w_gob.copy()
    if annotate_mode in [OP_SIMPLE, OP_COMBINE_W_H]:
        color = BBOX_COLOR[annotate_mode]
    else:
        color = RED
    drawing_grid_column_bboxes = True
    drawing_one_gcb = True
    while drawing_grid_column_bboxes:
        image_w_gcb = image_w_gob.copy()
        if drawing_one_gcb:
            cv2.rectangle(image_w_gcb, (x_start, y_start), (x_end, y_end), color, 1)
            if IMAGE_TYPE == "Exercises":
                mask_x_start, mask_x_end = x_start, x_start + mask_x_offset
                im_region = image_w_gcb[y_start:y_end, mask_x_start:mask_x_end]
                white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                image_w_gcb[y_start:y_end, mask_x_start:mask_x_end] = masked_reg
                cv2.rectangle(image_w_gcb, (mask_x_start, y_start), (mask_x_end, y_end), color, 1)
            cv2.imshow("image", image_w_gcb)
            cv2.waitKey(1)
        else:
            grid_col_bboxes.append([(x_start, y_start), (x_end, y_end)])
            cv2.rectangle(image_w_gcb, (x_start, y_start), (x_end, y_end), color, 2)
            if IMAGE_TYPE == "Exercises":
                mask_x_start, mask_x_end = x_start, x_start + mask_x_offset
                grid_col_masks.append([mask_x_start, mask_x_end])
                im_region = image_w_gcb[y_start:y_end, mask_x_start:mask_x_end]
                white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
                masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
                image_w_gcb[y_start:y_end, mask_x_start:mask_x_end] = masked_reg
                cv2.rectangle(image_w_gcb, (mask_x_start, y_start), (mask_x_end, y_end), color, 1)
            cv2.imshow("image", image_w_gcb)
            cv2.waitKey(1)
            image_w_gob = image_w_gcb
            drawing_one_gcb = True
        if keyboard.is_pressed('ctrl+shift+alt+x'):
            while keyboard.is_pressed('ctrl+shift+alt+x'):
                continue
            if grid_scan_mode:
                grid_scan_mode = False
            else:
                grid_scan_mode = True
        if keyboard.is_pressed('esc'):
            time.sleep(0.5)
            white_columns = None
            drawing_grid_column_bboxes = False
            drawing_one_gcb = False
            grid_col_bboxes = []
            print("Canceled.")
            return False, image, None, None
    white_columns = None
    if [(x_start, y_start), (x_end, y_end)] not in grid_col_bboxes:
        if IMAGE_TYPE == "Exercises":
            grid_col_masks.append([mask_x_start, mask_x_end])
        grid_col_bboxes.append([(x_start, y_start), (x_end, y_end)])
        cv2.rectangle(image_w_gcb, (x_start, y_start), (x_end, y_end), color, 2)
        cv2.imshow("image", image_w_gcb)
        cv2.waitKey(1)



    # 3. Set row dividing line
    cv2.setMouseCallback("image", SASGridRowLines, [grid_outer_boundary])
    image_w_rl = image_w_gcb.copy()
    drawing_grid_row_lines = True
    drawing_one_grl = True
    while drawing_grid_row_lines:
        image_w_rl = image_w_gcb.copy()
        if drawing_one_grl:
            if y_end >= grid_outer_boundary[1][1]:
                cv2.line(image_w_rl, (x_start, y_start), (x_end, y_end), BLACK, 1)
            else:
                cv2.line(image_w_rl, (x_start, y_start), (x_end, y_end), color, 1)
            cv2.imshow("image", image_w_rl)
            cv2.waitKey(1)
        else:
            grid_row_lines.append([(x_start, y_start), (x_end, y_end)])
            cv2.line(image_w_rl, (x_start, y_start), (x_end, y_end), color, 2)
            cv2.imshow("image", image_w_rl)
            cv2.waitKey(1)
            image_w_gcb = image_w_rl
            drawing_one_grl = True
        if keyboard.is_pressed('esc'):
            time.sleep(0.5)
            current_image_index = old_image_index
            drawing_grid_row_lines = False
            print("Canceled.")
            return False, image, None, None
    # if [(x_start, y_start), (x_end, y_end)] not in grid_row_lines:
    #     grid_row_lines.append([(x_start, y_start), (x_end, y_end)])
    #     cv2.line(image_w_rl, (x_start, y_start), (x_end, y_end), color, 2)
    #     cv2.imshow("image", image_w_rl)
    #     cv2.waitKey(1)


    # 4. Prepare bboxes data for return
    if annotate_mode == OP_COMBINE_W_H:
        grid_header = header
    else:
        grid_header = None
    key_lb_1 = generateCode()
    bboxes[key_lb_1] = line_bbox
    addAnnotation(code=key_lb_1, shape=SHAPE_LINE, operation=annotate_mode, column_pos=column_pos, index=None)
    k = int(current_image_index + (len(grid_col_bboxes) * (len(grid_row_lines) + 1))/2)
    keys_for_plotting = []
    for i in range(len(grid_row_lines) + 1): # i is row number, not line number
        for j in range(len(grid_col_bboxes)):
            if i == 0: # first row
                if len(grid_row_lines) > 0:
                    bbox = [grid_col_bboxes[j][0], (grid_col_bboxes[j][1][0], grid_row_lines[i][1][1])]
                    if IMAGE_TYPE == "Exercises":
                        mask = [(grid_col_masks[j][0], grid_col_bboxes[j][0][1]), (grid_col_masks[j][1], grid_row_lines[i][1][1])]
                else:
                    bbox = grid_col_bboxes[j]
                    if IMAGE_TYPE == "Exercises":
                        mask = [(grid_col_masks[j][0], grid_col_bboxes[j][0][1]), (grid_col_masks[j][1], grid_col_bboxes[j][1][1])]
            elif i == len(grid_row_lines):  # last row
                bbox = [(grid_col_bboxes[j][0][0], grid_row_lines[i - 1][0][1]), grid_col_bboxes[j][1]]
                if IMAGE_TYPE == "Exercises":
                    mask = [(grid_col_masks[j][0], grid_row_lines[i - 1][0][1]), (grid_col_masks[j][1], grid_col_bboxes[j][1][1])]
            elif len(grid_row_lines) > 1:
                bbox = [(grid_col_bboxes[j][0][0], grid_row_lines[i - 1][0][1]), (grid_col_bboxes[j][1][0], grid_row_lines[i][1][1])]
                if IMAGE_TYPE == "Exercises":
                    mask = [(grid_col_masks[j][0], grid_row_lines[i - 1][0][1]), (grid_col_masks[j][1], grid_row_lines[i][1][1])]

            key = generateCode()
            bboxes[key] = bbox
            if IMAGE_TYPE == "Exercises":
                masks[key] = mask
            keys_for_plotting.append(key)
            if grid_ordering == "horizontal":
                addAnnotation(code=key, shape=SHAPE_BBOX, operation=annotate_mode, column_pos=column_pos, index=current_image_index, grid=True, header=grid_header)
                if odds_only:
                    current_image_index += 2
                else:
                    current_image_index += 1
            elif grid_ordering == "vertical":
                if i % 2 == 1:
                    addAnnotation(code=key, shape=SHAPE_BBOX, operation=annotate_mode, column_pos=column_pos, index=current_image_index, grid=True, header=grid_header)
                    if odds_only:
                        current_image_index += 2
                    else:
                        current_image_index += 1
                else:
                    addAnnotation(code=key, shape=SHAPE_BBOX, operation=annotate_mode, column_pos=column_pos, index=k, grid=True, header=grid_header)
                    k += 1
    if grid_ordering == "vertical":
        current_image_index = k
    key_lb_2 = generateCode()
    bboxes[key_lb_2] = [(boundary[0][0], grid_outer_boundary[1][1]), (boundary[1][0], grid_outer_boundary[1][1])]
    addAnnotation(code=key_lb_2, shape=SHAPE_LINE, operation=annotate_mode, column_pos=column_pos, index=None)

    #5. Plot index numbers
    for key in keys_for_plotting:
        bbox = bboxes[key]
        x_0, y_0, x_1, y_1 = bbox[0][0], bbox[0][1], bbox[0][0], bbox[0][1]
        l_x_0, l_y_0, l_x_1, l_y_1 = x_0 - 28, y_0, x_1 - 2, y_1 + 20
        cv2.rectangle(image_w_rl, (l_x_0, l_y_0), (l_x_1, l_y_1), color, -1)
        cv2.putText(image_w_rl, str(annotations[key]["index"]).zfill(3), (l_x_0 + 2, l_y_0 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow("image", image_w_rl)
        cv2.waitKey(1)

    if grid_outer_boundary[1][1] >= boundary[1][1]:
        drawing = False
    label_ready = False
    return True, image_w_rl, grid_outer_boundary, annotate_mode  # outer_boundary already global



def drawOuterBoundary(image, command, last_header, one_column_boundary_set, two_columns_boundary_set, setted_outer_boundary):
    global x_start, y_start, x_end, y_end
    global label_x_start, label_y_start, label_x_end, label_y_end
    global drawing_boundary, drawing
    global outer_boundary
    global column_line
    global annotations
    drawing = False
    if not two_columns_boundary_set:
        outer_boundary = [(0, 0), (0, 0)]
        column_line = [(0, 0), (0, 0)]
    if not one_column_boundary_set:
        outer_boundary = [(0, 0), (0, 0)]
    if one_column_boundary_set or two_columns_boundary_set:
        outer_boundary = setted_outer_boundary
        image_w_outer_boundary = cv2.rectangle(image.copy(), outer_boundary[0], outer_boundary[1], NEON_GREEN, 2)
        cv2.imshow("image", image_w_outer_boundary)
        cv2.waitKey(1)
        drawing = True
    else:
        if command not in STANDARD_OPs:
            annotate_mode = OP_SIMPLE
        elif command == OP_APP_TO_LAST and len(os.listdir(temp_ss_path)) == 0:
            annotate_mode = OP_SIMPLE
        elif command == OP_APP_TO_LAST and len(os.listdir(temp_ss_path)) > 0:
            annotate_mode = OP_APP_TO_LAST
        elif command == OP_COMBINE_W_H and len(last_header) == 0:
            annotate_mode = OP_SIMPLE
        else:
            annotate_mode = command
        cv2.setMouseCallback("image", setOuterBoundaryCoordiates, [])
        image_w_mask = image.copy()
        im_region = image_w_mask[0:image.shape[0], 0:image.shape[1]]
        white_rect = np.ones(im_region.shape, dtype=np.uint8) * 40
        masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
        image_w_mask[0:image.shape[0], 0:image.shape[1]] = masked_reg
        while True:
            if annotate_mode in BBOX_COLOR.keys():
                color = BBOX_COLOR[annotate_mode]
            else:
                color = RED
            image_w_outer_boundary = image_w_mask.copy()
            cv2.line(image_w_outer_boundary, (x_cursor, 0), (x_cursor, image.shape[0]), color, 1)
            cv2.line(image_w_outer_boundary, (0, y_cursor), (image.shape[1], y_cursor), color, 1)
            if drawing_boundary is True:
                image_wo_mask = image.copy()
                unmasked_reg = image_wo_mask[y_start:y_end, x_start:x_end]
                image_w_outer_boundary[y_start:y_end, x_start:x_end] = unmasked_reg
                cv2.rectangle(image_w_outer_boundary, (x_start, y_start), (x_end, y_end), NEON_GREEN, 1)
            cv2.imshow("image", image_w_outer_boundary)
            cv2.waitKey(1)

            if drawing_boundary is False and drawing == True:
                break
            if keyboard.is_pressed('ctrl+shift+alt+1'):
                time.sleep(0.01)
                if annotate_mode != OP_SIMPLE:
                    annotate_mode = OP_SIMPLE
            elif keyboard.is_pressed('ctrl+shift+alt+2'):
                time.sleep(0.01)
                if annotate_mode != OP_APP_TO_LAST:
                    if len(os.listdir(temp_ss_path)) == 0 and len(bboxes) == 0:
                        annotate_mode = OP_SIMPLE
                    else:
                        annotate_mode = OP_APP_TO_LAST
            elif keyboard.is_pressed('ctrl+shift+alt+3'):
                time.sleep(0.01)
                if annotate_mode != OP_SET_HEADER:
                    annotate_mode = OP_SET_HEADER
            elif keyboard.is_pressed('ctrl+shift+alt+4'):
                time.sleep(0.01)
                if annotate_mode != OP_COMBINE_W_H:
                    if len(header) == 0:
                        annotate_mode = OP_SIMPLE
                    else:
                        annotate_mode = OP_COMBINE_W_H
            elif keyboard.is_pressed('ctrl+shift+alt+5'):
                time.sleep(0.01)
                if annotate_mode != OP_APP_TO_HEAD:
                    if len(header) == 0:
                        annotate_mode = OP_SIMPLE
                    else:
                        annotate_mode = OP_APP_TO_HEAD
            elif keyboard.is_pressed('ctrl+shift+alt+6'):
                time.sleep(0.01)
                if annotate_mode != OP_GRID_MODE:
                    annotate_mode = OP_GRID_MODE
            if keyboard.is_pressed('esc'):
                time.sleep(0.01)
                drawing = False
                drawing_boundary = False
                outer_boundary = [(0, 0), (0, 0)]
                #one_column_boundary_set = False
                column_line = [(0, 0), (0, 0)]
                #two_columns_boundary_set = False
                print("Canceled.")
                return False, None, None, None, None
        image_w_outer_boundary = image_w_mask.copy()
        image_wo_mask = image.copy()
        unmasked_reg = image_wo_mask[y_start:y_end, x_start:x_end]
        image_w_outer_boundary[y_start:y_end, x_start:x_end] = unmasked_reg
        cv2.rectangle(image_w_outer_boundary, (x_start, y_start), (x_end, y_end), NEON_GREEN, 2)
        cv2.imshow("image", image_w_outer_boundary)
        cv2.waitKey(1)
    x_start, y_start, x_end, y_end = 0, 0, 0, 0
    label_x_start, label_y_start, label_x_end, label_y_end = 0, 0, 0, 0
    drawing_boundary = False
    return True, image_w_outer_boundary, outer_boundary, one_column_boundary_set, two_columns_boundary_set #outer_boundary already global


def drawColumnLine(image, boundary):
    global drawing_column_line
    global two_columns_boundary_set
    global column_line
    global outer_boundary
    global one_column_boundary_set
    global drawing
    global im_bnd_gray
    if two_columns_boundary_set:
        image_w_column_line = cv2.rectangle(image, column_line[0], column_line[1], NEON_GREEN, 2)
        cv2.imshow("image", image_w_column_line)
        cv2.waitKey(1)
        boundary_left_column = [(boundary[0][0], boundary[0][1]), (column_line[1][0], boundary[1][1])]
        boundary_right_column = [(column_line[0][0], boundary[0][1]), (boundary[1][0], boundary[1][1])]
    else:
        drawing_column_line = True
        # cv2.setMouseCallback("image", setColumnLineCoordiates, [boundary])
        im_bnd_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.setMouseCallback("image", scanSetColumnLineCoordiates, [boundary])
        while True:
            image_w_column_line = image.copy()
            if drawing_column_line is True:
                cv2.line(image_w_column_line, (x_start, y_start), (x_end, y_end), NEON_GREEN, 1)
            cv2.imshow("image", image_w_column_line)
            cv2.waitKey(1)

            if drawing_column_line is False:
                boundary_left_column = [(boundary[0][0], boundary[0][1]), (x_end, boundary[1][1])]
                boundary_right_column = [(x_end, boundary[0][1]), (boundary[1][0], boundary[1][1])]
                break

            if keyboard.is_pressed('esc'):
                time.sleep(0.01)
                drawing = False
                outer_boundary = [(0, 0), (0, 0)]
                #one_column_boundary_set = False
                column_line = [(0, 0), (0, 0)]
                #two_columns_boundary_set = False
                print("Canceled.")
                return False, None, None, None
        image_w_column_line = image.copy()
        cv2.line(image_w_column_line, (x_start, y_start), (x_end, y_end), NEON_GREEN, 2)
        cv2.imshow("image", image_w_column_line)
        cv2.waitKey(1)
    return True, image_w_column_line, boundary_left_column, boundary_right_column
########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################
def SASColumnLineForMaskRegion(event, x, y, flags, param):
    global x_start, y_start, x_end, y_end
    global drawing_col_line_mr

    boundary = param[0]
    x_start, y_start, x_end, y_end = x, boundary[0][1], x, boundary[1][1]
    if event == cv2.EVENT_LBUTTONUP:
        drawing_col_line_mr = False



# T(n) = 2T(n/2) + f(m) for n rows, m entries per row, so T(n) = Theta(nlgn)
def binSearchForBBOXBoundaries(intensity_type, rows, rows_indices, scan_up):
    if len(rows) > 1:
        top_min_pixel_val, top_mpv_row_index = binSearchForBBOXBoundaries(intensity_type, rows[:int(np.ceil(len(rows) / 2))], rows_indices[:int(np.ceil(len(rows) / 2))], scan_up)
        bott_min_pixel_val, bott_mpv_row_index = binSearchForBBOXBoundaries(intensity_type, rows[int(np.ceil(len(rows) / 2)):], rows_indices[int(np.ceil(len(rows) / 2)):], scan_up)
        if intensity_type == "black":
            if top_min_pixel_val < bott_min_pixel_val:
                return top_min_pixel_val, top_mpv_row_index
            elif bott_min_pixel_val < top_min_pixel_val:
                return bott_min_pixel_val, bott_mpv_row_index
            elif top_min_pixel_val == bott_min_pixel_val:
                if scan_up:
                    return top_min_pixel_val, max(top_mpv_row_index, bott_mpv_row_index)
                else:
                    return top_min_pixel_val, min(top_mpv_row_index, bott_mpv_row_index)
        elif intensity_type == "white":
            if top_min_pixel_val > bott_min_pixel_val:
                return top_min_pixel_val, top_mpv_row_index
            elif bott_min_pixel_val > top_min_pixel_val:
                return bott_min_pixel_val, bott_mpv_row_index
            elif top_min_pixel_val == bott_min_pixel_val:
                if scan_up:
                    return top_min_pixel_val, max(top_mpv_row_index, bott_mpv_row_index)
                else:
                    return top_min_pixel_val, min(top_mpv_row_index, bott_mpv_row_index)

    else:
        return int(min(rows[0])), rows_indices[0]


def setBBoxesAutomatically(orig_image, image_w_outer_bnd, boundary, annotate_mode, column_pos):
    global x_start, y_start, x_end, y_end
    global drawing_col_line_mr
    global current_image_index
    global drawing
    global label_ready


    color = BBOX_COLOR[annotate_mode]
    cv2.setMouseCallback("image", SASColumnLineForMaskRegion, [boundary])
    drawing_col_line_mr = True
    image_w_line = image_w_outer_bnd.copy()
    while drawing_col_line_mr:
        image_w_line = image_w_outer_bnd.copy()
        cv2.line(image_w_line, (x_start, y_start), (x_end, y_end), BLACK, 1)
        cv2.imshow("image", image_w_line)
        cv2.waitKey(1)
    col_line = [(x_start, y_start), (x_end, y_end)]
    cv2.line(image_w_line, col_line[0], col_line[1], BLACK, 1)
    cv2.imshow("image", image_w_line)
    cv2.waitKey(1)

    im_bnd_gray = cv2.cvtColor(orig_image, cv2.COLOR_BGR2GRAY)
    _, im_thresh_otsu = cv2.threshold(im_bnd_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    mask_scan_region = im_thresh_otsu[boundary[0][1]:boundary[1][1], boundary[0][0]:x_end]
    temp_pos_y = binSearchForBBOXBoundaries("black", mask_scan_region, [i for i in range(len(mask_scan_region))], scan_up=False)
    start_pos_y = binSearchForBBOXBoundaries("white", mask_scan_region[temp_pos_y[1]:], [i for i in range(temp_pos_y[1], len(mask_scan_region))], scan_up=False)
    top_bbox_y = boundary[0][1]
    image_w_bboxes = image_w_line.copy()
    while True:
        pos_y2 = binSearchForBBOXBoundaries("black", mask_scan_region[start_pos_y[1]:], [i for i in range(start_pos_y[1], len(mask_scan_region))], scan_up=False)
        if pos_y2[0] >= 240:
            break
        upper_scan_region = im_thresh_otsu[boundary[0][1]:boundary[0][1] + pos_y2[1], boundary[0][0]:boundary[1][0]]
        temp_pos_y = binSearchForBBOXBoundaries("white", upper_scan_region, [i for i in range(len(upper_scan_region))], scan_up=True)
        pos_y1 = binSearchForBBOXBoundaries("black", upper_scan_region[:temp_pos_y[1]], [i for i in range(len(upper_scan_region[:temp_pos_y[1]]))], scan_up=True)
        if pos_y1[0] >= 240:
            break
        midpoint_y = int((pos_y1[1] + pos_y2[1]) / 2)
        key = generateCode()
        bbox = [(boundary[0][0], top_bbox_y), (boundary[1][0], boundary[0][1] + midpoint_y)]
        bboxes[key] = bbox
        addAnnotation(code=key, shape=SHAPE_BBOX, operation=annotate_mode, column_pos=column_pos, index=current_image_index)
        if IMAGE_TYPE == "Exercises":
            mask = [(boundary[0][0], top_bbox_y), (col_line[0][0], boundary[0][1] + midpoint_y)]
            masks[key] = mask
            im_region = image_w_bboxes[mask[0][1]:mask[1][1], mask[0][0]:mask[1][0]]
            white_rect = np.ones(im_region.shape, dtype=np.uint8) * 150
            masked_reg = cv2.addWeighted(im_region, 0.5, white_rect, 0.5, 1.0)
            image_w_bboxes[mask[0][1]:mask[1][1], mask[0][0]:mask[1][0]] = masked_reg
            cv2.rectangle(image_w_bboxes, mask[0], mask[1], BLACK, 1)
        if odds_only:
            current_image_index += 2
        else:
            current_image_index += 1
        cv2.rectangle(image_w_bboxes, bbox[0], bbox[1], color, 1)
        x_0, y_0, x_1, y_1 = bbox[0][0], bbox[0][1], bbox[0][0], bbox[0][1]
        l_x_0, l_y_0, l_x_1, l_y_1 = x_0 - 28, y_0, x_1 - 2, y_1 + 20
        cv2.rectangle(image_w_bboxes, (l_x_0, l_y_0), (l_x_1, l_y_1), color, -1)
        cv2.putText(image_w_bboxes, str(annotations[key]["index"]).zfill(3), (l_x_0 + 2, l_y_0 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow("image", image_w_bboxes)
        cv2.waitKey(1)
        top_bbox_y = boundary[0][1] + midpoint_y
        start_pos_y = binSearchForBBOXBoundaries("white", mask_scan_region[pos_y2[1]:], [i for i in range(pos_y2[1], len(mask_scan_region))], scan_up=False)

    pass
    pass
    return True, image_w_bboxes

########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################
def setSCRowsCoordiates(event, x, y, flags, param):
    global drawing_subcolumns
    global drawing_sc_rows
    global temp_bboxes
    global x_start, y_start, x_end, y_end
    boundary = param[0]
    x_center = param[1]
    if event == cv2.EVENT_MOUSEMOVE:
        if y > boundary[1][1]:
            x_start, y_start, x_end, y_end = boundary[0][0], boundary[1][1], boundary[1][0], boundary[1][1]
        elif y < boundary[0][1]:
            x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[0][1]
        else:
            x_start, y_start, x_end, y_end = boundary[0][0], y, boundary[1][0], y
    if event == cv2.EVENT_LBUTTONUP:
        drawing_sc_rows = False
        if y > boundary[1][1]:
            drawing_subcolumns = False

def scanAndSetSCRowsCoordiates(event, x, y, flags, param):
    global drawing_subcolumns
    global drawing_sc_rows
    global temp_bboxes
    global x_start, y_start, x_end, y_end
    boundary = param[0]
    if event == cv2.EVENT_MOUSEMOVE:
        if y > boundary[1][1]:
            x_start, y_start, x_end, y_end = boundary[0][0], boundary[1][1], boundary[1][0], boundary[1][1]
        elif y < boundary[0][1]:
            x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[0][1]
        else:
            scan_region = im_bnd_gray[y - 20:y + 20, boundary[0][0]:boundary[1][0]]
            offset = -20
            reg_rows = {}
            cont_rows = []
            start = True
            for i in range(40):
                avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                reg_rows[y + offset] = avg_pixel_val
                offset += 1
                if avg_pixel_val == 255:
                    if start == False:
                        row = [y + offset]
                        cont_rows.append(row)
                        start = True
                    else:
                        if len(cont_rows) > 0:
                            cont_rows[-1].append(y + offset)
                else:
                    start = False
            idx = None
            max_len = 0
            for i in range(len(cont_rows)):
                reg = cont_rows[i]
                if (reg[-1] - reg[0]) > max_len:
                    max_len = reg[-1] - reg[0]
                    idx = i
            if idx is not None:
                if (cont_rows[idx][-1] - cont_rows[idx][0]) % 2 == 1:
                    midpoint = int((cont_rows[idx][-1] + cont_rows[idx][0]) / 2)
                else:
                    midpoint = int(np.ceil((cont_rows[idx][-1] + cont_rows[idx][0]) / 2))
                if midpoint > boundary[1][1]:
                    x_start, y_start, x_end, y_end = boundary[0][0], boundary[1][1], boundary[1][0], boundary[1][1]
                elif y < boundary[0][1]:
                    x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[0][1]
                else:
                    x_start, y_start, x_end, y_end = boundary[0][0], midpoint, boundary[1][0], midpoint
            else:
                x_start, y_start, x_end, y_end = boundary[0][0], y, boundary[1][0], y
    if event == cv2.EVENT_LBUTTONUP:
        drawing_sc_rows = False
        if y > boundary[1][1]:
            drawing_subcolumns = False


def setSubcolumnsCoordiates(event, x, y, flags, param):
    global drawing_subcolumns
    global sc_x_center, sc_y_center
    global mask_x_offset, mask_y_offset
    global drawing_mask
    boundary = param[0]
    if x > boundary[1][0]:
        sc_x_center = boundary[1][0]
    elif x < boundary[0][0]:
        sc_x_center = boundary[0][0]
    else:
        sc_x_center = x
    if y > boundary[1][1]:
        sc_y_center = boundary[1][1]
    elif y < boundary[0][1]:
        sc_y_center = boundary[0][1]
    else:
        sc_y_center = y
    if event == cv2.EVENT_LBUTTONUP:
        drawing_subcolumns = False

    if event == cv2.EVENT_RBUTTONDOWN:
        drawing_mask = True
    elif event == cv2.EVENT_MOUSEMOVE and drawing_mask == True:
        mask_x_offset = x - x_start
    elif event == cv2.EVENT_RBUTTONUP and drawing_mask == True:
        drawing_mask = False


def scanAndSetSubcolumnsCoordiates(event, x, y, flags, param):
    global drawing_subcolumns
    global sc_x_center, sc_y_center
    global mask_x_offset, mask_y_offset
    global drawing_mask
    boundary = param[0]
    if x > boundary[1][0]:
        sc_x_center = boundary[1][0]
    elif x < boundary[0][0]:
        sc_x_center = boundary[0][0]
    else:
        sc_x_center = x

    if y > boundary[1][1]:
        sc_y_center = boundary[1][1]
    elif y < boundary[0][1]:
        sc_y_center = boundary[0][1]
    else:
        scan_region = im_bnd_gray[y - 20:y + 20, boundary[0][0]:boundary[1][0]]
        offset = -20
        reg_rows = {}
        cont_rows = []
        start = True
        for i in range(40):
            avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
            reg_rows[y + offset] = avg_pixel_val
            offset += 1
            if avg_pixel_val == 255:
                if start == False:
                    row = [y + offset]
                    cont_rows.append(row)
                    start = True
                else:
                    if len(cont_rows) > 0:
                        cont_rows[-1].append(y + offset)
            else:
                start = False
        idx = None
        max_len = 0
        for i in range(len(cont_rows)):
            reg = cont_rows[i]
            if (reg[-1] - reg[0]) > max_len:
                max_len = reg[-1] - reg[0]
                idx = i
        if idx is not None:
            if (cont_rows[idx][-1] - cont_rows[idx][0]) % 2 == 1:
                midpoint = int((cont_rows[idx][-1] + cont_rows[idx][0]) / 2)
            else:
                midpoint = int(np.ceil((cont_rows[idx][-1] + cont_rows[idx][0]) / 2))
            if midpoint > boundary[1][1]:
                sc_y_center = boundary[1][1]
            elif y < boundary[0][1]:
                sc_y_center = boundary[0][1]
            else:
                sc_y_center = midpoint
        else:
            sc_y_center = y
    if event == cv2.EVENT_LBUTTONUP:
        drawing_subcolumns = False

    if event == cv2.EVENT_RBUTTONDOWN:
        drawing_mask = True
    elif event == cv2.EVENT_MOUSEMOVE and drawing_mask == True:
        mask_x_offset = x - x_start
    elif event == cv2.EVENT_RBUTTONUP and drawing_mask == True:
        drawing_mask = False

def setColumnLineCoordiates(event, x, y, flags, param):
    global drawing_column_line
    global column_line
    global boundary_left_column, boundary_right_column
    global x_start, y_start, x_end, y_end
    if event == cv2.EVENT_MOUSEMOVE:
        if x > outer_boundary[1][0]:
            x_start, y_start, x_end, y_end = outer_boundary[1][0], outer_boundary[0][1], outer_boundary[1][0], outer_boundary[1][1]
        elif x < outer_boundary[0][0]:
            x_start, y_start, x_end, y_end = outer_boundary[0][0], outer_boundary[0][1], outer_boundary[0][0], outer_boundary[1][1]
        else:
            x_start, y_start, x_end, y_end = x, outer_boundary[0][1], x, outer_boundary[1][1]
    if event == cv2.EVENT_LBUTTONUP:
        column_line = [(x_start, y_start), (x_end, y_end)]
        drawing_column_line = False

def scanSetColumnLineCoordiates(event, x, y, flags, param):
    global drawing_column_line
    global column_line
    global boundary_left_column, boundary_right_column
    global x_start, y_start, x_end, y_end
    global im_bnd_gray
    if event == cv2.EVENT_MOUSEMOVE:
        if x > outer_boundary[1][0]:
            x_start, y_start, x_end, y_end = outer_boundary[1][0], outer_boundary[0][1], outer_boundary[1][0], outer_boundary[1][1]
        elif x < outer_boundary[0][0]:
            x_start, y_start, x_end, y_end = outer_boundary[0][0], outer_boundary[0][1], outer_boundary[0][0], outer_boundary[1][1]
        else:
            # x_start, y_start, x_end, y_end = x, outer_boundary[0][1], x, outer_boundary[1][1]
            scan_radius = SCAN_RADIUS_COL_LINE
            scan_region = im_bnd_gray[outer_boundary[0][1]:outer_boundary[1][1], x - scan_radius:x + scan_radius]
            scan_region = np.transpose(scan_region)
            offset = -scan_radius
            reg_columns = {}
            cont_columns = []
            start = True
            for i in range(len(scan_region)):
                avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                reg_columns[x + offset] = avg_pixel_val
                offset += 1
                if avg_pixel_val > 250:
                    if start == False:
                        column = [x + offset]
                        cont_columns.append(column)
                        start = True
                    else:
                        if len(cont_columns) > 0:
                            cont_columns[-1].append(x + offset)
                else:
                    start = False
            idx = None
            max_len = 0
            for i in range(len(cont_columns)):
                reg = cont_columns[i]
                if (reg[-1] - reg[0]) > max_len:
                    max_len = reg[-1] - reg[0]
                    idx = i
            if idx is not None:
                if (cont_columns[idx][-1] - cont_columns[idx][0]) % 2 == 1:
                    midpoint = int((cont_columns[idx][-1] + cont_columns[idx][0]) / 2)
                else:
                    midpoint = int(np.ceil((cont_columns[idx][-1] + cont_columns[idx][0]) / 2))
                if midpoint > outer_boundary[1][0]:
                    x_start, y_start, x_end, y_end = outer_boundary[1][0], outer_boundary[0][1], outer_boundary[1][0], outer_boundary[1][1]
                elif y < outer_boundary[0][0]:
                    x_start, y_start, x_end, y_end = outer_boundary[0][0], outer_boundary[0][1], outer_boundary[0][0], outer_boundary[1][1]
                else:
                    x_start, y_start, x_end, y_end = midpoint, outer_boundary[0][1], midpoint, outer_boundary[1][1]
            else:
                x_start, y_start, x_end, y_end = x, outer_boundary[0][1], x, outer_boundary[1][1]
    if event == cv2.EVENT_LBUTTONUP:
        column_line = [(x_start, y_start), (x_end, y_end)]
        drawing_column_line = False


def setOuterBoundaryCoordiates(event, x, y, flags, param):
    global drawing
    global drawing_boundary
    global outer_boundary
    global x_start, y_start, x_end, y_end
    global label_x_start, label_y_start, label_x_end, label_y_end
    global x_cursor, y_cursor
    global label_ready
    x_cursor, y_cursor = x, y
    if event == cv2.EVENT_MOUSEMOVE and drawing == False:
        label_x_start, label_y_start, label_x_end, label_y_end = x - 31, y + 20, x - 5, y + 5
    if event == cv2.EVENT_LBUTTONDOWN and drawing == False:
        x_start, y_start, x_end, y_end = x, y, x, y
        drawing = True
        drawing_boundary = True
    elif event == cv2.EVENT_MOUSEMOVE and drawing == True:
        if drawing_boundary == True:
            x_end, y_end = x, y
    elif event == cv2.EVENT_LBUTTONUP and drawing == True:
        x_end, y_end = x, y
        if x_end > x_start and y_end > y_start:
            drawing_boundary = False
            outer_boundary = [(x_start, y_start), (x_end, y_end)]
        elif x_start > x_end and y_end > y_start:
            drawing_boundary = False
            outer_boundary = [(x_end, y_start), (x_start, y_end)]
        elif x_end > x_start and y_start > y_end:
            drawing_boundary = False
            outer_boundary = [(x_start, y_end), (x_end, y_start)]
        elif x_start > x_end and y_start > y_end:
            drawing_boundary = False
            outer_boundary = [(x_end, y_end), (x_start, y_start)]
        drawing_boundary = False

def setBBOXCoordiates(event, x, y, flags, param):
    global drawing
    global drawing_bbox, bboxes
    global x_start, y_start, x_end, y_end
    global label_x_start, label_y_start, label_x_end, label_y_end
    global label_ready
    global mask_x_offset, mask_y_offset
    global drawing_mask
    boundary = param[0]
    if drawing_bbox and drawing:
        if len(bboxes) == 0:
            if y > boundary[1][1]:
                x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[1][1]
            elif y < boundary[0][1]:
                x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[0][1]
            else:
                x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], y
        else:
            if y > boundary[1][1]:
                x_start, y_start, x_end, y_end = list(bboxes.values())[-1][0][0], list(bboxes.values())[-1][1][1], list(bboxes.values())[-1][1][0], boundary[1][1]
            elif y < list(bboxes.values())[-1][1][1]:
                x_start, y_start, x_end, y_end = list(bboxes.values())[-1][0][0], list(bboxes.values())[-1][1][1], list(bboxes.values())[-1][1][0], list(bboxes.values())[-1][1][1]
            else:
                x_start, y_start, x_end, y_end = list(bboxes.values())[-1][0][0], list(bboxes.values())[-1][1][1], list(bboxes.values())[-1][1][0], y
        label_x_start, label_y_start, label_x_end, label_y_end = x_start - 28, y_start, x_start - 2, y_start + 20
        label_ready = True

    if event == cv2.EVENT_LBUTTONUP:
        drawing_bbox = False
        if y_end >= boundary[1][1]:
            drawing = False
    if event == cv2.EVENT_RBUTTONDOWN:
        drawing_mask = True
    elif event == cv2.EVENT_MOUSEMOVE and drawing_mask == True:
        mask_x_offset, mask_y_offset = x - x_start, y - y_start
    elif event == cv2.EVENT_RBUTTONUP and drawing_mask == True:
        drawing_mask = False

def scanAndSetBBOXCoordiates(event, x, y, flags, param):
    global drawing
    global drawing_bbox, bboxes
    global x_start, y_start, x_end, y_end
    global label_x_start, label_y_start, label_x_end, label_y_end
    global label_ready
    global mask_x_offset, mask_y_offset
    global drawing_mask
    global im_bnd_gray
    global mask_offset_found
    boundary = param[0]
    if drawing_bbox and drawing:
        scan_radius = SCAN_RADIUS_BBOX
        if len(bboxes) == 0:
            if y > boundary[1][1]:
                x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[1][1]
            elif y < boundary[0][1]:
                x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[0][1]
            else:
                # x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], y
                scan_region = im_bnd_gray[y - scan_radius:y + scan_radius, boundary[0][0]:boundary[1][0]]
                offset = -scan_radius
                reg_rows = {}
                cont_rows = []
                start = True
                for i in range(len(scan_region)):
                    avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                    reg_rows[y + offset] = avg_pixel_val
                    offset+=1
                    if avg_pixel_val >= SCAN_ROW_AVERAGE_COLOR_THRESHOLD:
                        if start == False:
                            row = [y + offset]
                            cont_rows.append(row)
                            start = True
                        else:
                            if len(cont_rows) > 0:
                                cont_rows[-1].append(y + offset)
                    else:
                        start = False
                idx = None
                max_len = 0
                for i in range(len(cont_rows)):
                    reg = cont_rows[i]
                    if (reg[-1] - reg[0]) > max_len:
                        max_len = reg[-1] - reg[0]
                        idx = i
                if idx is not None:
                    if (cont_rows[idx][-1] - cont_rows[idx][0]) % 2 == 1:
                        midpoint = int((cont_rows[idx][-1] + cont_rows[idx][0]) / 2)
                    else:
                        midpoint = int(np.ceil((cont_rows[idx][-1] + cont_rows[idx][0]) / 2))
                    if midpoint > boundary[1][1]:
                        x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[1][1]
                    elif y < boundary[0][1]:
                        x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[0][1]
                    else:
                        x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], midpoint
                else:
                    x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], y

        else:
            bb_x_start, bb_y_start, bb_x_end, bb_y_end = list(bboxes.values())[-1][0][0], list(bboxes.values())[-1][1][1], list(bboxes.values())[-1][1][0], list(bboxes.values())[-1][1][1]
            if y > boundary[1][1]:
                x_start, y_start, x_end, y_end = bb_x_start, bb_y_start, bb_x_end, boundary[1][1]
            elif y < bb_y_start:
                x_start, y_start, x_end, y_end = bb_x_start, bb_y_start, bb_x_end, bb_y_start
            else:
                # x_start, y_start, x_end, y_end = bb_x_start, bb_y_end, bb_x_end, y
                scan_region = im_bnd_gray[y - scan_radius:y + scan_radius, bb_x_start:bb_x_end]
                offset = -scan_radius
                reg_rows = {}
                cont_rows = []
                start = True
                for i in range(len(scan_region)):
                    avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                    #reg_rows[y + offset] = avg_pixel_val
                    offset += 1
                    if avg_pixel_val >= SCAN_ROW_AVERAGE_COLOR_THRESHOLD:
                        if start == False:
                            row = [y + offset]
                            cont_rows.append(row)
                            start = True
                        else:
                            if len(cont_rows) > 0:
                                cont_rows[-1].append(y + offset)
                    else:
                        start = False
                idx = None
                max_len = 0
                for i in range(len(cont_rows)):
                    reg = cont_rows[i]
                    if (reg[-1] - reg[0]) > max_len:
                        max_len = reg[-1] - reg[0]
                        idx = i
                if idx is not None:
                    if (cont_rows[idx][-1] - cont_rows[idx][0]) % 2 == 1:
                        midpoint = int((cont_rows[idx][-1] + cont_rows[idx][0]) / 2)
                    else:
                        midpoint = int(np.ceil((cont_rows[idx][-1] + cont_rows[idx][0]) / 2))
                    if midpoint > boundary[1][1]:
                        x_start, y_start, x_end, y_end = bb_x_start, bb_y_start, bb_x_end, boundary[1][1]
                    elif y < bb_y_start:
                        x_start, y_start, x_end, y_end = bb_x_start, bb_y_start, bb_x_end, bb_y_start
                    else:
                        x_start, y_start, x_end, y_end = bb_x_start, bb_y_start, bb_x_end, midpoint
                else:
                    x_start, y_start, x_end, y_end = bb_x_start, bb_y_start, bb_x_end, y

        label_x_start, label_y_start, label_x_end, label_y_end = x_start - 28, y_start, x_start - 2, y_start + 20
        label_ready = True

    # Detection and Masking
    # if mask_offset_found is False and drawing_bbox and drawing:
    #     if len(bboxes) == 0:
    #         msr_y_top, msr_x_start, msr_x_end = boundary[0][1], boundary[0][0], boundary[1][0]
    #     else:
    #         msr_x_start, msr_y_start, msr_x_end, msr_y_top = list(bboxes.values())[-1][0][0], list(bboxes.values())[-1][1][1], list(bboxes.values())[-1][1][0], list(bboxes.values())[-1][1][1]
    #     mask_scan_region = im_bnd_gray[msr_y_top:y, msr_x_start:msr_x_end]
    #     top_horizontal_white_row_detected = False
    #     for i in range(len(mask_scan_region)):
    #         avg_pixel_val = int(np.floor(np.mean(mask_scan_region[i])))
    #         if avg_pixel_val < 255 and top_horizontal_white_row_detected is False:
    #             top_horizontal_white_row_detected = True
    #             continue
    #         elif avg_pixel_val == 255 and top_horizontal_white_row_detected:
    #             y_pos_1 = i
    #             y_pos_2 = i
    #             for j in range(y_pos_1, len(mask_scan_region)):
    #                 if True in [k <= 240 for k in mask_scan_region[j]]:
    #                     y_pos_2 = j
    #                     break
    #             if (y_pos_1 + y_pos_2) % 2 == 1:
    #                 mask_y_offset = int((y_pos_1 + y_pos_2)/2)
    #             else:
    #                 mask_y_offset = int(np.ceil(y_pos_1 + y_pos_2)/2)
    #             # mask_offset_found = True
    #             break
    #     mask_scan_region_x = np.transpose(im_bnd_gray[msr_y_top:msr_y_top + mask_y_offset, msr_x_start:msr_x_end])
    #     white_space_count = 0
    #     final_white_col_detected = False
    #     look_for_black = False
    #     for i in range(len(mask_scan_region_x)):
    #         avg_pixel_val = int(np.floor(np.mean(mask_scan_region_x[i])))
    #         if avg_pixel_val == 255 and final_white_col_detected is False and look_for_black is False:
    #             white_space_count += 1
    #             look_for_black = True
    #             if white_space_count == NUM_WHT_SPACE:
    #                 final_white_col_detected = True
    #                 x_pos_1 = i
    #                 continue
    #         if avg_pixel_val < 255 and final_white_col_detected is False and look_for_black is True:
    #             look_for_black = False
    #         if avg_pixel_val < 255 and final_white_col_detected is True and look_for_black is True:
    #             if (x_pos_1 + i) % 2 == 1:
    #                 mask_x_offset = int((x_pos_1 + i)/2)
    #             else:
    #                 mask_x_offset = int(np.ceil(x_pos_1 + i)/2)
    #             mask_offset_found = True
    #             break


    if event == cv2.EVENT_LBUTTONUP:
        drawing_bbox = False
        if y_end >= boundary[1][1]:
            drawing = False
    if event == cv2.EVENT_RBUTTONDOWN:
        drawing_mask = True
    elif event == cv2.EVENT_MOUSEMOVE and drawing_mask == True:
        mask_x_offset, mask_y_offset = x - x_start, y - y_start
    elif event == cv2.EVENT_RBUTTONUP and drawing_mask == True:
        drawing_mask = False



def SASGridOuterBoundary(event, x, y, flags, param):
    global x_start, y_start, x_end, y_end
    global drawing_grid_outer_boundary
    global drawing
    global im_bnd_gray
    boundary = param[0]
    if drawing_grid_outer_boundary and drawing:
        if len(bboxes) == 0:
            if y > boundary[1][1]:
                x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[1][1]
            elif y < boundary[0][1]:
                x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[0][1]
            else:
                scan_region = im_bnd_gray[y - 20:y + 20, boundary[0][0]:boundary[1][0]]
                offset = -20
                reg_rows = {}
                cont_rows = []
                start = True
                for i in range(40):
                    avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                    reg_rows[y + offset] = avg_pixel_val
                    offset+=1
                    if avg_pixel_val == 255:
                        if start == False:
                            row = [y + offset]
                            cont_rows.append(row)
                            start = True
                        else:
                            if len(cont_rows) > 0:
                                cont_rows[-1].append(y + offset)
                    else:
                        start = False
                idx = None
                max_len = 0
                for i in range(len(cont_rows)):
                    reg = cont_rows[i]
                    if (reg[-1] - reg[0]) > max_len:
                        max_len = reg[-1] - reg[0]
                        idx = i
                if idx is not None:
                    if (cont_rows[idx][-1] - cont_rows[idx][0]) % 2 == 1:
                        midpoint = int((cont_rows[idx][-1] + cont_rows[idx][0]) / 2)
                    else:
                        midpoint = int(np.ceil((cont_rows[idx][-1] + cont_rows[idx][0]) / 2))
                    if midpoint > boundary[1][1]:
                        x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[1][1]
                    elif y < boundary[0][1]:
                        x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[0][1]
                    else:
                        x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], midpoint
                else:
                    x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], y

        else:
            bb_x_start, bb_y_start, bb_x_end, bb_y_end = list(bboxes.values())[-1][0][0], list(bboxes.values())[-1][1][1], list(bboxes.values())[-1][1][0], list(bboxes.values())[-1][1][1]
            if y > boundary[1][1]:
                x_start, y_start, x_end, y_end = bb_x_start, bb_y_start, bb_x_end, boundary[1][1]
            elif y < bb_y_start:
                x_start, y_start, x_end, y_end = bb_x_start, bb_y_start, bb_x_end, bb_y_start
            else:
                scan_region = im_bnd_gray[y - 20:y + 20, bb_x_start:bb_x_end]
                offset = -20
                cont_rows = []
                start = True
                for i in range(40):
                    avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                    offset += 1
                    if avg_pixel_val == 255:
                        if start == False:
                            row = [y + offset]
                            cont_rows.append(row)
                            start = True
                        else:
                            if len(cont_rows) > 0:
                                cont_rows[-1].append(y + offset)
                    else:
                        start = False
                idx = None
                max_len = 0
                for i in range(len(cont_rows)):
                    reg = cont_rows[i]
                    if (reg[-1] - reg[0]) > max_len:
                        max_len = reg[-1] - reg[0]
                        idx = i
                if idx is not None:
                    if (cont_rows[idx][-1] - cont_rows[idx][0]) % 2 == 1:
                        midpoint = int((cont_rows[idx][-1] + cont_rows[idx][0]) / 2)
                    else:
                        midpoint = int(np.ceil((cont_rows[idx][-1] + cont_rows[idx][0]) / 2))
                    if midpoint > boundary[1][1]:
                        x_start, y_start, x_end, y_end = bb_x_start, bb_y_start, bb_x_end, boundary[1][1]
                    elif y < bb_y_start:
                        x_start, y_start, x_end, y_end = bb_x_start, bb_y_start, bb_x_end, bb_y_start
                    else:
                        x_start, y_start, x_end, y_end = bb_x_start, bb_y_start, bb_x_end, midpoint
                else:
                    x_start, y_start, x_end, y_end = bb_x_start, bb_y_start, bb_x_end, y

    if event == cv2.EVENT_LBUTTONUP:
        drawing_grid_outer_boundary = False


def SASGridColumnBBoxes(event, x, y, flags, param):
    global x_start, y_start, x_end, y_end
    global drawing_grid_column_bboxes, drawing_one_gcb
    global im_bnd_gray
    global grid_col_bboxes
    global drawing_mask
    global mask_x_offset
    global white_columns
    global grid_scan_mode
    boundary = param[0]
    if drawing_one_gcb and drawing_grid_column_bboxes:
        if len(grid_col_bboxes) > 0:
            boundary = boundary.copy()
            boundary[0] = (grid_col_bboxes[-1][1][0], grid_col_bboxes[-1][0][1])
        if x > boundary[1][0]:
            x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[1][1]
        elif x < boundary[0][0]:
            x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[0][0], boundary[0][1]
        else:
            if grid_scan_mode is False:
                x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], x, boundary[1][1]
            else:
                if len(grid_col_bboxes) == 0 and white_columns is None:
                    grid_region = im_bnd_gray[boundary[0][1]:boundary[1][1], boundary[0][0]:boundary[1][0]]
                    grid_region = np.transpose(grid_region)
                    white_columns = 0
                    for i in range(len(grid_region)):
                        avg_pixel_val = int(np.floor(np.mean(grid_region[i])))
                        if avg_pixel_val == 255:
                            white_columns += 1
                        else:
                            #print("white col: " + str(white_columns))
                            break
                scan_radius = SCAN_RADIUS_GRID_COL
                scan_region = im_bnd_gray[boundary[0][1]:boundary[1][1], x - scan_radius:x + scan_radius]
                scan_region = np.transpose(scan_region)
                offset = -scan_radius
                reg_columns = {}
                cont_columns = []
                start = True
                for i in range(len(scan_region)):
                    avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                    reg_columns[x + offset] = avg_pixel_val
                    offset += 1
                    if avg_pixel_val == 255:
                        if start == False:
                            column = [x + offset]
                            cont_columns.append(column)
                            start = True
                        else:
                            if len(cont_columns) > 0:
                                cont_columns[-1].append(x + offset)
                    else:
                        start = False
                idx = None
                max_len = 0
                for i in range(len(cont_columns)):
                    reg = cont_columns[i]
                    if (reg[-1] - reg[0]) > max_len:
                        max_len = reg[-1] - reg[0]
                        idx = i
                if idx is not None:
                    # if (cont_columns[idx][-1] - cont_columns[idx][0]) % 2 == 1:
                    #     midpoint = int((cont_columns[idx][-1] + cont_columns[idx][0]) / 2)
                    # else:
                    #     midpoint = int(np.ceil((cont_columns[idx][-1] + cont_columns[idx][0]) / 2))
                    endpoint = cont_columns[idx][-1] - white_columns# + 8
                    if endpoint > boundary[1][0]:
                        x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[1][1]
                    elif x < boundary[0][0]:
                        x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[0][0], boundary[1][1]
                    else:
                        x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], endpoint, boundary[1][1]
                else:
                    x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], x, boundary[1][1]

    if event == cv2.EVENT_LBUTTONUP:
        drawing_one_gcb = False
        if x_end >= boundary[1][0]:
            drawing_grid_column_bboxes = False

    if event == cv2.EVENT_RBUTTONDOWN:
        drawing_mask = True
    elif event == cv2.EVENT_MOUSEMOVE and drawing_mask == True:
        mask_x_offset = x - x_start
    elif event == cv2.EVENT_RBUTTONUP and drawing_mask == True:
        drawing_mask = False


def SASGridRowLines(event, x, y, flags, param):
    global x_start, y_start, x_end, y_end
    global drawing_grid_row_lines, drawing_one_grl
    global im_bnd_gray
    global grid_row_lines
    boundary = param[0]
    if drawing_one_grl and drawing_grid_row_lines:
        if len(grid_row_lines) > 0:
            boundary[0] = (grid_row_lines[-1][0][0], grid_row_lines[-1][0][1])
        if event == cv2.EVENT_MOUSEMOVE:
            if y > boundary[1][1]:
                x_start, y_start, x_end, y_end = boundary[0][0], boundary[1][1], boundary[1][0], boundary[1][1]
            elif y < boundary[0][1]:
                x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[0][1]
            else:
                scan_radius = SCAN_RADIUS_GRID_RL
                scan_region = im_bnd_gray[y - scan_radius:y + scan_radius, boundary[0][0]:boundary[1][0]]
                offset = -scan_radius
                reg_rows = {}
                cont_rows = []
                start = True
                for i in range(len(scan_region)):
                    avg_pixel_val = int(np.floor(np.mean(scan_region[i])))
                    reg_rows[y + offset] = avg_pixel_val
                    offset += 1
                    if avg_pixel_val == 255:
                        if start == False:
                            row = [y + offset]
                            cont_rows.append(row)
                            start = True
                        else:
                            if len(cont_rows) > 0:
                                cont_rows[-1].append(y + offset)
                    else:
                        start = False
                idx = None
                max_len = 0
                for i in range(len(cont_rows)):
                    reg = cont_rows[i]
                    if (reg[-1] - reg[0]) > max_len:
                        max_len = reg[-1] - reg[0]
                        idx = i
                if idx is not None:
                    if (cont_rows[idx][-1] - cont_rows[idx][0]) % 2 == 1:
                        midpoint = int((cont_rows[idx][-1] + cont_rows[idx][0]) / 2)
                    else:
                        midpoint = int(np.ceil((cont_rows[idx][-1] + cont_rows[idx][0]) / 2))
                    if midpoint > boundary[1][1]:
                        x_start, y_start, x_end, y_end = boundary[0][0], boundary[1][1], boundary[1][0], boundary[1][1]
                    elif y < boundary[0][1]:
                        x_start, y_start, x_end, y_end = boundary[0][0], boundary[0][1], boundary[1][0], boundary[0][1]
                    else:
                        x_start, y_start, x_end, y_end = boundary[0][0], midpoint, boundary[1][0], midpoint
                else:
                    x_start, y_start, x_end, y_end = boundary[0][0], y, boundary[1][0], y
        if event == cv2.EVENT_LBUTTONUP:
            drawing_one_grl = False
            if y >= boundary[1][1]:
                drawing_grid_row_lines = False



def generateCode():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

def addAnnotation(code, shape, operation, index, grid=False, header=None, append_to_last_saved_image=False, column_pos=None):
    annotations[code] = {}
    annotations[code]["shape"] = shape
    annotations[code]["shape"] = shape
    annotations[code]["operation"] = operation
    annotations[code]["index"] = index
    annotations[code]["grid"] = grid
    annotations[code]["header"] = header
    annotations[code]["append_to_last_saved_image"] = append_to_last_saved_image
    annotations[code]["column_pos"] = column_pos



# # T(n) = n*f(m) for n rows, m entries per row
# def search_gs_intensity(intensity_type, mask_scan_region, boundary_top_y, start_pos_y, image_w_outer_bnd, boundary, scan_up):
#     start = start_pos_y - boundary_top_y
#     if scan_up is False:
#         for i in range(start, len(mask_scan_region)):
#             image_w_search_lines = image_w_outer_bnd.copy()
#             cv2.line(image_w_search_lines, (boundary[0][0], i + boundary_top_y), (boundary[1][0], i + boundary_top_y), RED, 1)
#             cv2.imshow("image", image_w_search_lines)
#             cv2.waitKey(1)
#             if intensity_type == "white":
#                 min_pixel_val = int(min(mask_scan_region[i]))
#                 if min_pixel_val >= 245:
#                     return i + boundary_top_y
#             elif intensity_type == "black":
#                 min_pixel_val = int(min(mask_scan_region[i]))
#                 if min_pixel_val <= 200:
#                     return i + boundary_top_y
#     else:
#         for i in reversed(range(start)):
#             image_w_search_lines = image_w_outer_bnd.copy()
#             cv2.line(image_w_search_lines, (boundary[0][0], i + boundary_top_y), (boundary[1][0], i + boundary_top_y), RED, 1)
#             cv2.imshow("image", image_w_search_lines)
#             cv2.waitKey(1)
#             if intensity_type == "white":
#                 min_pixel_val = int(min(mask_scan_region[i]))
#                 if min_pixel_val >= 245:
#                     return i + boundary_top_y
#             elif intensity_type == "black":
#                 min_pixel_val = int(min(mask_scan_region[i]))
#                 if min_pixel_val <= 200:
#                     return i + boundary_top_y
#     return None


# def drawSubcolumns(image, boundary, annotate_mode, grid_ordering, column_pos=None):
#     global sc_x_center, sc_y_center
#     global drawing_boundary, drawing_subcolumns, drawing, drawing_sc_rows
#     global x_start, y_start, x_end, y_end
#     global bboxes
#     global masks
#     global current_image_index
#     global annotations
#     global label_ready
#     global header
#     global mask_x_offset
#     temp_bboxes = {}
#     old_image_index = current_image_index
#     cv2.setMouseCallback("image", scanAndSetSubcolumnsCoordiates, [boundary])
#     drawing_subcolumns = True
#     image_w_subcolumns = image.copy()
#     code = generateCode()
#     temp_bboxes[code] = [(boundary[0][0], boundary[0][1]), (boundary[1][0], boundary[0][1])]
#     if annotate_mode == OP_GRID_MODE:
#         annotate_mode = OP_SIMPLE
#     x_0, y_0, x_1, y_1 = boundary[0][0], boundary[0][1], boundary[0][0], boundary[0][1]
#     l_x_0, l_y_0, l_x_1, l_y_1 = x_0 - 28, y_0, x_1 - 2, y_1 + 20
#     while drawing_subcolumns:
#         if annotate_mode in [OP_SIMPLE, OP_COMBINE_W_H]:
#             color = BBOX_COLOR[annotate_mode]
#         else:
#             color = RED
#         image_w_subcolumns = image.copy()
#         cv2.rectangle(image_w_subcolumns, (l_x_0, l_y_0), (l_x_1, l_y_1), color, -1)
#         cv2.putText(image_w_subcolumns, "GRID", (l_x_0 + 2, l_y_0 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.30, (255, 255, 255), 1, cv2.LINE_AA)
#         cv2.rectangle(image_w_subcolumns, temp_bboxes[list(temp_bboxes.keys())[-1]][0], (temp_bboxes[list(temp_bboxes.keys())[-1]][1][0], sc_y_center), color, 1)
#         cv2.line(image_w_subcolumns, (sc_x_center, sc_y_center), (sc_x_center, temp_bboxes[list(temp_bboxes.keys())[-1]][0][1]), color, 1)
#
#         mask_x_start, mask_x_end = x_start, x_start + mask_x_offset
#         im_region_left = image_w_subcolumns[y_start:sc_y_center, mask_x_start:mask_x_end]
#         im_region_right = image_w_subcolumns[y_start:sc_y_center, sc_x_center:sc_x_center + mask_x_offset]
#         white_rect = np.ones(im_region_left.shape, dtype=np.uint8) * 150
#         masked_reg_left = cv2.addWeighted(im_region_left, 0.5, white_rect, 0.5, 1.0)
#         masked_reg_right = cv2.addWeighted(im_region_right, 0.5, white_rect, 0.5, 1.0)
#         image_w_subcolumns[y_start:sc_y_center, mask_x_start:mask_x_end] = masked_reg_left
#         image_w_subcolumns[y_start:sc_y_center, sc_x_center:sc_x_center + mask_x_offset] = masked_reg_right
#         cv2.rectangle(image_w_subcolumns, (mask_x_start, y_start), (mask_x_end, sc_y_center), color, 1)
#         cv2.rectangle(image_w_subcolumns, (sc_x_center, y_start), (sc_x_center + mask_x_offset, sc_y_center), color, 1)
#         cv2.imshow("image", image_w_subcolumns)
#         cv2.waitKey(1)
#
#         if keyboard.is_pressed('ctrl+shift+alt+1'):
#             time.sleep(0.01)
#             annotate_mode = OP_SIMPLE
#         elif keyboard.is_pressed('ctrl+shift+alt+4'):
#             time.sleep(0.01)
#             annotate_mode = OP_COMBINE_W_H
#         # elif keyboard.is_pressed('ctrl+shift+alt+C'):
#         #     if mask_x_end - 1 > x_start:
#         #         mask_x_offset -= 1
#         # elif keyboard.is_pressed('ctrl+shift+alt+G'):
#         #     if mask_x_end + 1 < sc_x_center:
#         #         mask_x_offset += 1
#         if keyboard.is_pressed('esc'):
#             time.sleep(0.5)
#             current_image_index = old_image_index
#             drawing_subcolumns = False
#             print("Canceled.")
#             return False, image, None, None
#     cv2.rectangle(image_w_subcolumns, temp_bboxes[list(temp_bboxes.keys())[-1]][0], (temp_bboxes[list(temp_bboxes.keys())[-1]][1][0], sc_y_center), color, 2)
#     cv2.line(image_w_subcolumns, (sc_x_center, sc_y_center), (sc_x_center, temp_bboxes[list(temp_bboxes.keys())[-1]][0][1]), color, 2)
#     cv2.imshow("image", image_w_subcolumns)
#     cv2.waitKey(1)
#     x_start, y_start, x_end, y_end = 0,0,0,0
#     drawing_subcolumns = True
#     drawing_sc_rows = True
#     if annotate_mode in [OP_SIMPLE, OP_COMBINE_W_H]:
#         color = BBOX_COLOR[annotate_mode]
#     else:
#         color = RED
#     # cv2.setMouseCallback("image", setSCRowsCoordiates, [[temp_bboxes[list(temp_bboxes.keys())[-1]][0], (temp_bboxes[list(temp_bboxes.keys())[-1]][1][0], sc_y_center)], sc_x_center])
#     cv2.setMouseCallback("image", scanAndSetSCRowsCoordiates, [[temp_bboxes[list(temp_bboxes.keys())[-1]][0], (temp_bboxes[list(temp_bboxes.keys())[-1]][1][0], sc_y_center)], sc_x_center])
#     while drawing_subcolumns:
#         image_w_sc_rows = image_w_subcolumns.copy()
#         if drawing_sc_rows is True:
#             cv2.line(image_w_sc_rows, (x_start, y_start), (x_end, y_end), color, 1)
#             cv2.imshow("image", image_w_sc_rows)
#             cv2.waitKey(1)
#
#         if drawing_sc_rows is False:
#             code = generateCode()
#             temp_bboxes[code] = [(boundary[0][0], temp_bboxes[list(temp_bboxes.keys())[-1]][1][1]), (sc_x_center, y_end)]
#             code = generateCode()
#             temp_bboxes[code] = [(sc_x_center, temp_bboxes[list(temp_bboxes.keys())[-1]][0][1]), (boundary[1][0], y_end)]
#             cv2.line(image_w_sc_rows, (x_start, y_start), (x_end, y_end), color, 2)
#             cv2.imshow("image", image_w_sc_rows)
#             cv2.waitKey(1)
#             image_w_subcolumns = image_w_sc_rows
#             drawing_sc_rows = True
#             # cv2.setMouseCallback("image", setSCRowsCoordiates, [[(x_start, y_start), (temp_bboxes[list(temp_bboxes.keys())[-1]][1][0], sc_y_center)], sc_x_center])
#             cv2.setMouseCallback("image", scanAndSetSCRowsCoordiates, [[(x_start, y_start), (temp_bboxes[list(temp_bboxes.keys())[-1]][1][0], sc_y_center)], sc_x_center])
#
#         if keyboard.is_pressed('esc'):
#             time.sleep(0.5)
#             current_image_index = old_image_index
#             drawing_subcolumns = False
#             temp_bboxes = {}
#             print("Canceled.")
#             return False, image, None, None
#     if annotate_mode == OP_COMBINE_W_H:
#         grid_header = header
#     else:
#         grid_header = None
#     k = int(current_image_index + (len(temp_bboxes) - 1)/2)
#     for i in range(len(temp_bboxes)):
#         key = list(temp_bboxes.keys())[i]
#         temp_bbox = list(temp_bboxes.values())[i]
#         temp_bbox = list(temp_bboxes.values())[i]
#         bboxes[key] = temp_bbox
#         masks[key] = [(mask_x_start, temp_bbox[0][1]), (mask_x_end, temp_bbox[1][1])]
#         if i != 0:
#             if grid_ordering == "horizontal":
#                 addAnnotation(code=key, shape=SHAPE_BBOX, operation=annotate_mode, column_pos=column_pos, index=current_image_index, grid=True, header=grid_header)
#                 if odds_only:
#                     current_image_index += 2
#                 else:
#                     current_image_index += 1
#             elif grid_ordering == "vertical":
#                 if i % 2 == 1:
#                     addAnnotation(code=key, shape=SHAPE_BBOX, operation=annotate_mode, column_pos=column_pos, index=current_image_index, grid=True, header=grid_header)
#                     if odds_only:
#                         current_image_index += 2
#                     else:
#                         current_image_index += 1
#                 else:
#                     addAnnotation(code=key, shape=SHAPE_BBOX, operation=annotate_mode, column_pos=column_pos, index=k, grid=True, header=grid_header)
#                     k += 1
#         else:
#             addAnnotation(code=key, shape=SHAPE_LINE, operation=annotate_mode, column_pos=column_pos, index=None, header=grid_header)
#     if grid_ordering == "vertical":
#         current_image_index = k
#     bboxes.update(temp_bboxes)
#     code = generateCode()
#     bboxes[code] = [(boundary[0][0], sc_y_center), (boundary[1][0], sc_y_center)]
#     addAnnotation(code=code, shape=SHAPE_LINE, operation=annotate_mode, column_pos=column_pos, index=None)
#     temp_bboxes.pop(list(temp_bboxes.keys())[0])
#     for key, temp_bbox in zip(temp_bboxes.keys(), temp_bboxes.values()):
#             x_0, y_0, x_1, y_1 = temp_bbox[0][0], temp_bbox[0][1], temp_bbox[0][0], temp_bbox[0][1]
#             l_x_0, l_y_0, l_x_1, l_y_1 = x_0 - 28, y_0, x_1 - 2, y_1 + 20
#             cv2.rectangle(image_w_subcolumns, (l_x_0, l_y_0), (l_x_1, l_y_1), color, -1)
#             cv2.putText(image_w_subcolumns, str(annotations[key]["index"]).zfill(3), (l_x_0 + 2, l_y_0 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1, cv2.LINE_AA)
#             cv2.imshow("image", image_w_subcolumns)
#             cv2.waitKey(1)
#     if sc_y_center >= boundary[1][1]:
#         drawing = False
#     label_ready = False
#     return True, image_w_subcolumns, [boundary[0], (boundary[1][0], sc_y_center)], annotate_mode  # outer_boundary already global

