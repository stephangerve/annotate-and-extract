import cv2
import mss
import mss.tools
import screeninfo
import numpy as np
from LibDrawing import *




def annotateOneColumn(command, one_column_boundary_set, two_columns_boundary_set, current_image_index, header, setted_outer_boundary):
    with mss.mss() as sct:
        monitor_number = 1
        mon = sct.monitors[monitor_number]
        monitor = {
            "top": mon["top"],
            "left": mon["left"],
            "width": mon["width"],
            "height": mon["height"],
            "mon": monitor_number,
        }
        sct_img = sct.grab(monitor)


    orig_image = np.array(sct_img)
    image_w_border = cv2.rectangle(orig_image.copy(), (0, 0), (orig_image.shape[1], orig_image.shape[0]), NEON_GREEN, 4)

    cv2.namedWindow("image", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty("image", cv2.WND_PROP_TOPMOST, 1)
    screen = screeninfo.get_monitors()[0]
    cv2.moveWindow("image", screen.x - 1, screen.y - 1)
    condition, image_w_outer_boundary, outer_boundary, one_column_boundary_set, two_columns_boundary_set = drawOuterBoundary(image_w_border, command, header, one_column_boundary_set, two_columns_boundary_set, setted_outer_boundary)
    if condition:
        current_bboxes = []
        current_masks = []
        current_annotations = {}
        while True:
            condition, image_w_bboxes, annotate_mode, bboxes, masks, annotations, last_image_index, header = drawBBoxes2(orig_image, image_w_outer_boundary, outer_boundary, command, current_bboxes, current_masks, current_image_index, current_annotations, header, None)
            if condition:
                condition = delayToInspect(image_w_bboxes, outer_boundary)
                if condition:
                    cv2.destroyAllWindows()
                    return condition, orig_image, bboxes, masks, annotations, last_image_index, header
            else:
                break
    cv2.destroyAllWindows()
    return False, None, None, None, None, current_image_index, header




def annotateTwoColumns(command, one_column_boundary_set, two_columns_boundary_set, current_image_index, header, setted_outer_boundary):
    with mss.mss() as sct:
        monitor_number = 1
        mon = sct.monitors[monitor_number]
        monitor = {
            "top": mon["top"],
            "left": mon["left"],
            "width": mon["width"],
            "height": mon["height"],
            "mon": monitor_number,
        }
        sct_img = sct.grab(monitor)


    orig_image = np.array(sct_img)
    image_w_border = cv2.rectangle(orig_image.copy(), (0, 0), (orig_image.shape[1], orig_image.shape[0]), NEON_GREEN, 4)


    cv2.namedWindow("image", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty("image", cv2.WND_PROP_TOPMOST, 1)
    screen = screeninfo.get_monitors()[0]
    cv2.moveWindow("image", screen.x - 1, screen.y - 1)

    condition, image_w_outer_boundary, outer_boundary, one_column_boundary_set, two_columns_boundary_set = drawOuterBoundary(image_w_border, command, header, one_column_boundary_set, two_columns_boundary_set, setted_outer_boundary)
    if condition:
        condition, image_w_column_line, boundary_left_column, boundary_right_column = drawColumnLine(orig_image, image_w_outer_boundary, outer_boundary)
        if condition:
            annotations = {}
            bboxes = []
            masks = []
            last_image_index = current_image_index
            annotate_mode = command
            while True:
                condition, image_w_bboxes, annotate_mode, bboxes_left, masks_left, annotations, last_image_index, header = drawBBoxes2(orig_image, image_w_column_line.copy(), boundary_left_column, annotate_mode, bboxes, masks, last_image_index, annotations, header, COLUMN_LEFT)
                if condition:
                    condition, image_w_bboxes, annotate_mode, bboxes, masks, annotations, last_image_index, header = drawBBoxes2(orig_image, image_w_bboxes, boundary_right_column, annotate_mode, bboxes_left, masks_left, last_image_index, annotations, header, COLUMN_RIGHT)
                else:
                    break
                if condition:
                    condition = delayToInspect(image_w_bboxes, outer_boundary)
                    if condition:
                        cv2.destroyAllWindows()
                        return True, orig_image, bboxes, masks, annotations, last_image_index, header
                    else:
                        annotations = {}
                        bboxes = []
                        masks = []
                        last_image_index = current_image_index
                        annotate_mode = command
    cv2.destroyAllWindows()
    return False, None, None, None, None, current_image_index, header

def delayToInspect(image_w_bboxes, outer_boundary):
    global mouse_clicked
    x_0, y_0, x_1, y_1 = outer_boundary[0][0], outer_boundary[1][1], outer_boundary[0][0], outer_boundary[1][1]
    l_x_0, l_y_0, l_x_1, l_y_1 = x_0, y_0 + 2, x_1 + 35, y_1 + 22
    cv2.rectangle(image_w_bboxes, (l_x_0, l_y_0), (l_x_1, l_y_1), NEON_GREEN, -1)
    cv2.putText(image_w_bboxes, "VERIFY", (l_x_0 + 2, l_y_0 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.30, BLACK, 1, cv2.LINE_AA)
    cv2.imshow("image", image_w_bboxes)
    cv2.waitKey(1)
    mouse_clicked = False
    cv2.setMouseCallback("image", waitForMouseClick, [])
    while not mouse_clicked:
        cv2.waitKey(1)
        if keyboard.is_pressed('esc'):
            while keyboard.is_pressed('esc'):
                continue
            return False
    return True

def waitForMouseClick(event, x, y, flags, param):
    global mouse_clicked
    # if event == cv2.EVENT_LBUTTONDOWN:
    #     mouse_clicked = True
    if event == cv2.EVENT_LBUTTONUP:
        mouse_clicked = True


# def setOneColumn():
#     with mss.mss() as sct:
#         monitor_number = 1
#         mon = sct.monitors[monitor_number]
#         monitor = {
#             "top": mon["top"],
#             "left": mon["left"],
#             "width": mon["width"],
#             "height": mon["height"],
#             "mon": monitor_number,
#         }
#         sct_img = sct.grab(monitor)
#
#     color = NEON_GREEN
#     image = np.array(sct_img)
#     image_w_border = cv2.rectangle(image.copy(), (0, 0), (image.shape[1], image.shape[0]), color, 5)
#
#     cv2.namedWindow("image", cv2.WND_PROP_FULLSCREEN)
#     cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
#     cv2.setWindowProperty("image", cv2.WND_PROP_TOPMOST, 1)
#     screen = screeninfo.get_monitors()[0]
#     cv2.moveWindow("image", screen.x - 1, screen.y - 1)
#
#
#     condition, image_w_outer_boundary, outer_boundary, one_column_boundary_set, two_columns_boundary_set = drawOuterBoundary(image_w_border, False, False, None)
#     if condition:
#         cv2.imshow("image", image_w_outer_boundary)
#         cv2.waitKey(500)
#     cv2.destroyAllWindows()
#     return condition, outer_boundary, one_column_boundary_set, two_columns_boundary_set
#
#
# def setTwoColumns():
#     with mss.mss() as sct:
#         monitor_number = 1
#         mon = sct.monitors[monitor_number]
#         monitor = {
#             "top": mon["top"],
#             "left": mon["left"],
#             "width": mon["width"],
#             "height": mon["height"],
#             "mon": monitor_number,
#         }
#         sct_img = sct.grab(monitor)
#
#     color = NEON_GREEN
#     image = np.array(sct_img)
#     image_w_border = cv2.rectangle(image.copy(), (0, 0), (image.shape[1], image.shape[0]), color, 5)
#
#     cv2.namedWindow("image", cv2.WND_PROP_FULLSCREEN)
#     cv2.setWindowProperty("image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
#     cv2.setWindowProperty("image", cv2.WND_PROP_TOPMOST, 1)
#     screen = screeninfo.get_monitors()[0]
#     cv2.moveWindow("image", screen.x - 1, screen.y - 1)
#
#     condition, image_w_outer_boundary, _, one_column_boundary_set, two_columns_boundary_set = drawOuterBoundary(image_w_border, False, False, None)
#     if condition:
#         condition, image_w_column_line, _, _ = drawColumnLine(image_w_outer_boundary, outer_boundary)
#     else:
#         cv2.destroyAllWindows()
#         return
#     if condition:
#         cv2.imshow("image", image_w_column_line)
#         cv2.waitKey(500)
#     cv2.destroyAllWindows()
#     return condition, one_column_boundary_set, two_columns_boundary_set

    # condition, image_w_outer_boundary, outer_boundary, one_column_boundary_set, two_columns_boundary_set = drawOuterBoundary(image_w_border, one_column_boundary_set, two_columns_boundary_set)
    # if condition:
    #     condition, image_w_column_line, boundary_left_column, boundary_right_column = drawColumnLine(image_w_outer_boundary, outer_boundary)
    # else:
    #     cv2.destroyAllWindows()
    #     return False, None, None, None, current_image_index, header
    # if condition:
    #     while True:
    #         condition, image_w_bboxes, annotate_mode, bboxes_left, annotations, last_image_index, header = drawBBoxes(orig_image, image_w_column_line, boundary_left_column, command, [], current_image_index, {}, header)
    #         if condition:
    #             condition, _, _, bboxes_all, annotations, last_image_index, header = drawBBoxes(orig_image, image_w_bboxes, boundary_right_column, annotate_mode, bboxes_left, last_image_index, annotations, header)
    #         else:
    #             cv2.destroyAllWindows()
    #             return False, None, None, None, current_image_index, header
    #         if condition:
    #             cv2.destroyAllWindows()
    #             return True, orig_image, bboxes_all, annotations, last_image_index, header
    #         else:
    #             cv2.destroyAllWindows()
    #             return False, None, None, None, current_image_index, header
    # else:
    #     cv2.destroyAllWindows()
    #     return False, None, None, current_image_index, header
