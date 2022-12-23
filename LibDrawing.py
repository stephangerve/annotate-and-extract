import cv2
import time
import keyboard
import random
import string
import numpy as np
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

bboxes = {}
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
    orig_image_w_outer_boundary = image.copy()
    grid_ordering = "horizontal"
    drawing = True
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
                if annotations[key]["operation"] in [OP_SIMPLE, OP_COMBINE_W_H]:
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
    cv2.setMouseCallback("image", setBBOXCoordiates, [boundary])
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
                if annotate_mode in [OP_SIMPLE, OP_COMBINE_W_H]:
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
                condition, image, sc_boundary, sc_annotate_mode = drawSubcolumns(image_w_new_bbox, [(list(bboxes.values())[-1][0][0], list(bboxes.values())[-1][1][1]), (boundary[1][0], boundary[1][1])], annotate_mode, grid_ordering, column_pos)
            else:
                condition, image, sc_boundary, sc_annotate_mode = drawSubcolumns(image_w_new_bbox, boundary, annotate_mode, grid_ordering, column_pos)
            if condition is False:
                if annotate_mode == OP_GRID_MODE and last_annotate_mode == None:
                    annotate_mode = OP_SIMPLE
                else:
                    if last_annotate_mode is not None:
                        annotate_mode = last_annotate_mode
                cv2.setMouseCallback("image", setBBOXCoordiates, [boundary])
                if len(bboxes) > 0:
                    cv2.setMouseCallback("image", setBBOXCoordiates, [[(list(bboxes.values())[-1][0][0], list(bboxes.values())[-1][1][1]), (boundary[1][0], boundary[1][1])]])
                else:
                    cv2.setMouseCallback("image", setBBOXCoordiates, [boundary])
            else:
                annotate_mode = sc_annotate_mode
                if drawing is False:
                    image_w_new_bbox = image
                else:
                    cv2.setMouseCallback("image", setBBOXCoordiates, [[(sc_boundary[0][0], sc_boundary[1][1]), (boundary[1][0], boundary[1][1])]])

        if drawing_bbox is False:
            if annotate_mode == OP_SIMPLE:
                code = generateCode()
                bboxes[code] = [(x_start, y_start), (x_end, y_end)]
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
        elif keyboard.is_pressed('ctrl+shift+alt+y'):
            while keyboard.is_pressed('ctrl+shift+alt+y'):
                continue
            if grid_ordering == "horizontal":
                grid_ordering = "vertical"
            elif grid_ordering == "vertical":
                grid_ordering = "horizontal"
            print("grid ordering: " + grid_ordering)
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
                print("Canceled.")
                return False, None, None, None, None, annotations, last_image_index, header
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
                        return False, None, undo_annotation["operation"], bboxes, masks, annotations, undo_annotation["index"], header
                if undo_annotation["operation"] in [OP_SIMPLE, OP_APP_TO_LAST, OP_COMBINE_W_H]:
                    if undo_annotation["grid"] is True:
                        for key in reversed(list(annotations.keys())):
                            if annotations[key]["grid"] == True:
                                bboxes.pop(list(bboxes.keys())[-1])
                                masks.pop(list(bboxes.keys())[-1])
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
                        if annotations[key]["operation"] in [OP_SIMPLE, OP_COMBINE_W_H]:
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
                cv2.setMouseCallback("image", setBBOXCoordiates, [boundary])
    return True, image_w_new_bbox, annotate_mode, bboxes, masks, annotations, current_image_index, header


def drawSubcolumns(image, boundary, annotate_mode, grid_ordering, column_pos=None):
    global sc_x_center, sc_y_center
    global drawing_boundary, drawing_subcolumns, drawing, drawing_sc_rows
    global x_start, y_start, x_end, y_end
    global bboxes
    global masks
    global current_image_index
    global annotations
    global label_ready
    global header
    global mask_x_offset
    temp_bboxes = {}
    old_image_index = current_image_index
    cv2.setMouseCallback("image", setSubcolumnsCoordiates, [boundary])
    drawing_subcolumns = True
    image_w_subcolumns = image.copy()
    code = generateCode()
    temp_bboxes[code] = [(boundary[0][0], boundary[0][1]), (boundary[1][0], boundary[0][1])]
    if annotate_mode == OP_GRID_MODE:
        annotate_mode = OP_SIMPLE
    x_0, y_0, x_1, y_1 = boundary[0][0], boundary[0][1], boundary[0][0], boundary[0][1]
    l_x_0, l_y_0, l_x_1, l_y_1 = x_0 - 28, y_0, x_1 - 2, y_1 + 20
    while drawing_subcolumns:
        if annotate_mode in [OP_SIMPLE, OP_COMBINE_W_H]:
            color = BBOX_COLOR[annotate_mode]
        else:
            color = RED
        image_w_subcolumns = image.copy()
        cv2.rectangle(image_w_subcolumns, (l_x_0, l_y_0), (l_x_1, l_y_1), color, -1)
        cv2.putText(image_w_subcolumns, "GRID", (l_x_0 + 2, l_y_0 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.30, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.rectangle(image_w_subcolumns, temp_bboxes[list(temp_bboxes.keys())[-1]][0], (temp_bboxes[list(temp_bboxes.keys())[-1]][1][0], sc_y_center), color, 1)
        cv2.line(image_w_subcolumns, (sc_x_center, sc_y_center), (sc_x_center, temp_bboxes[list(temp_bboxes.keys())[-1]][0][1]), color, 1)

        mask_x_start, mask_x_end = x_start, x_start + mask_x_offset
        im_region_left = image_w_subcolumns[y_start:sc_y_center, mask_x_start:mask_x_end]
        im_region_right = image_w_subcolumns[y_start:sc_y_center, sc_x_center:sc_x_center + mask_x_offset]
        white_rect = np.ones(im_region_left.shape, dtype=np.uint8) * 150
        masked_reg_left = cv2.addWeighted(im_region_left, 0.5, white_rect, 0.5, 1.0)
        masked_reg_right = cv2.addWeighted(im_region_right, 0.5, white_rect, 0.5, 1.0)
        image_w_subcolumns[y_start:sc_y_center, mask_x_start:mask_x_end] = masked_reg_left
        image_w_subcolumns[y_start:sc_y_center, sc_x_center:sc_x_center + mask_x_offset] = masked_reg_right
        cv2.rectangle(image_w_subcolumns, (mask_x_start, y_start), (mask_x_end, sc_y_center), color, 1)
        cv2.rectangle(image_w_subcolumns, (sc_x_center, y_start), (sc_x_center + mask_x_offset, sc_y_center), color, 1)
        cv2.imshow("image", image_w_subcolumns)
        cv2.waitKey(1)

        if keyboard.is_pressed('ctrl+shift+alt+1'):
            time.sleep(0.01)
            annotate_mode = OP_SIMPLE
        elif keyboard.is_pressed('ctrl+shift+alt+4'):
            time.sleep(0.01)
            annotate_mode = OP_COMBINE_W_H
        # elif keyboard.is_pressed('ctrl+shift+alt+C'):
        #     if mask_x_end - 1 > x_start:
        #         mask_x_offset -= 1
        # elif keyboard.is_pressed('ctrl+shift+alt+G'):
        #     if mask_x_end + 1 < sc_x_center:
        #         mask_x_offset += 1
        if keyboard.is_pressed('esc'):
            time.sleep(0.5)
            current_image_index = old_image_index
            drawing_subcolumns = False
            print("Canceled.")
            return False, image, None, None
    cv2.rectangle(image_w_subcolumns, temp_bboxes[list(temp_bboxes.keys())[-1]][0], (temp_bboxes[list(temp_bboxes.keys())[-1]][1][0], sc_y_center), color, 2)
    cv2.line(image_w_subcolumns, (sc_x_center, sc_y_center), (sc_x_center, temp_bboxes[list(temp_bboxes.keys())[-1]][0][1]), color, 2)
    cv2.imshow("image", image_w_subcolumns)
    cv2.waitKey(1)
    x_start, y_start, x_end, y_end = 0,0,0,0
    drawing_subcolumns = True
    drawing_sc_rows = True
    if annotate_mode in [OP_SIMPLE, OP_COMBINE_W_H]:
        color = BBOX_COLOR[annotate_mode]
    else:
        color = RED
    cv2.setMouseCallback("image", setSCRowsCoordiates, [[temp_bboxes[list(temp_bboxes.keys())[-1]][0], (temp_bboxes[list(temp_bboxes.keys())[-1]][1][0], sc_y_center)], sc_x_center])
    while drawing_subcolumns:
        image_w_sc_rows = image_w_subcolumns.copy()
        if drawing_sc_rows is True:
            cv2.line(image_w_sc_rows, (x_start, y_start), (x_end, y_end), color, 1)
            cv2.imshow("image", image_w_sc_rows)
            cv2.waitKey(1)

        if drawing_sc_rows is False:
            code = generateCode()
            temp_bboxes[code] = [(boundary[0][0], temp_bboxes[list(temp_bboxes.keys())[-1]][1][1]), (sc_x_center, y_end)]
            code = generateCode()
            temp_bboxes[code] = [(sc_x_center, temp_bboxes[list(temp_bboxes.keys())[-1]][0][1]), (boundary[1][0], y_end)]
            cv2.line(image_w_sc_rows, (x_start, y_start), (x_end, y_end), color, 2)
            cv2.imshow("image", image_w_sc_rows)
            cv2.waitKey(1)
            image_w_subcolumns = image_w_sc_rows
            drawing_sc_rows = True
            cv2.setMouseCallback("image", setSCRowsCoordiates, [[(x_start, y_start), (temp_bboxes[list(temp_bboxes.keys())[-1]][1][0], sc_y_center)], sc_x_center])

        if keyboard.is_pressed('esc'):
            time.sleep(0.5)
            current_image_index = old_image_index
            drawing_subcolumns = False
            temp_bboxes = {}
            print("Canceled.")
            return False, image, None, None
    if annotate_mode == OP_COMBINE_W_H:
        grid_header = header
    else:
        grid_header = None
    k = int(current_image_index + (len(temp_bboxes) - 1)/2)
    for i in range(len(temp_bboxes)):
        key = list(temp_bboxes.keys())[i]
        temp_bbox = list(temp_bboxes.values())[i]
        temp_bbox = list(temp_bboxes.values())[i]
        bboxes[key] = temp_bbox
        masks[key] = [(mask_x_start, temp_bbox[0][1]), (mask_x_end, temp_bbox[1][1])]
        if i != 0:
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
        else:
            addAnnotation(code=key, shape=SHAPE_LINE, operation=annotate_mode, column_pos=column_pos, index=None, header=grid_header)
    if grid_ordering == "vertical":
        current_image_index = k
    bboxes.update(temp_bboxes)
    code = generateCode()
    bboxes[code] = [(boundary[0][0], sc_y_center), (boundary[1][0], sc_y_center)]
    addAnnotation(code=code, shape=SHAPE_LINE, operation=annotate_mode, column_pos=column_pos, index=None)
    temp_bboxes.pop(list(temp_bboxes.keys())[0])
    for key, temp_bbox in zip(temp_bboxes.keys(), temp_bboxes.values()):
            x_0, y_0, x_1, y_1 = temp_bbox[0][0], temp_bbox[0][1], temp_bbox[0][0], temp_bbox[0][1]
            l_x_0, l_y_0, l_x_1, l_y_1 = x_0 - 28, y_0, x_1 - 2, y_1 + 20
            cv2.rectangle(image_w_subcolumns, (l_x_0, l_y_0), (l_x_1, l_y_1), color, -1)
            cv2.putText(image_w_subcolumns, str(annotations[key]["index"]).zfill(3), (l_x_0 + 2, l_y_0 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow("image", image_w_subcolumns)
            cv2.waitKey(1)
    if sc_y_center >= boundary[1][1]:
        drawing = False
    label_ready = False
    return True, image_w_subcolumns, [boundary[0], (boundary[1][0], sc_y_center)], annotate_mode  # outer_boundary already global

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
    if two_columns_boundary_set:
        image_w_column_line = cv2.rectangle(image, column_line[0], column_line[1], NEON_GREEN, 2)
        cv2.imshow("image", image_w_column_line)
        cv2.waitKey(1)
        boundary_left_column = [(boundary[0][0], boundary[0][1]), (column_line[1][0], boundary[1][1])]
        boundary_right_column = [(column_line[0][0], boundary[0][1]), (boundary[1][0], boundary[1][1])]
    else:
        drawing_column_line = True
        cv2.setMouseCallback("image", setColumnLineCoordiates, [boundary])
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


########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
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
