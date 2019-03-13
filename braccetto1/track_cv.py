import cv2
import numpy as np
import sys
import math
import os
import logging
import geom_util as geom
import roi
import track_conf as tconf

#default gray threshold
T = tconf.threshold
Roi = roi.ROI()

def balance_frame(image):
    global T
    ret = None
    direction = 0
    try:
        for i in range(0, tconf.th_iterations):
            rc, gray = cv2.threshold(image, T, 255, 0)
            crop = Roi.crop_roi(gray)
            nwh = cv2.countNonZero(crop)
            perc = int(100 * nwh / Roi.get_area())
            if perc > tconf.white_max:
                if T > tconf.threshold_max:
                    break
                if direction == -1:
                    ret = crop
                    break
                T += 10
                direction = 1
            elif perc < tconf.white_min:
                if T < tconf.threshold_min:
                    break
                if  direction == 1:
                    ret = crop
                    break
                T -= 10
                direction = -1
            else:
                ret = crop
                break
    except:
        ret = crop
    return ret

def adjust_brightness(img, level):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    b = np.mean(img[:,:,2])
    if b == 0:
        return img
    r = level / b
    c = img.copy()
    c[:,:,2] = c[:,:,2] * r
    return cv2.cvtColor(c, cv2.COLOR_HSV2BGR)

def prepare_frame(image):
    global Roi
    global T
    height, width = image.shape[:2]
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # blurred = cv2.GaussianBlur(gray, (9, 9), 0)
    bgr = [60, 60, 80]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_hue = np.array([bgr[0]-T, bgr[1]-T, bgr[2]-T])
    upper_hue = np.array([bgr[0]+T, bgr[1]+T, bgr[2]+T])
    mask = cv2.inRange(hsv, lower_hue, upper_hue)
    blurred = cv2.GaussianBlur(mask, (9, 9), 0)

    cv2.imshow('image',image)
    cv2.imshow('blurred',blurred)
    cv2.imshow('mask',mask)
    # cv2.waitKey(0)
    # exit(-1)
    cv2.waitKey(1)

    if Roi.get_area() == 0:
        Roi.init_roi(width, height)
    return balance_frame(blurred), width, height

def find_main_countour(image):
    im2, cnts, hierarchy = cv2.findContours(image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    C = None
    if cnts is not None and len(cnts) > 0:
         C = max(cnts, key = cv2.contourArea)
    if C is None:
        return None, None
    rect = cv2.minAreaRect(C)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    box = geom.order_box(box)
    return C, box

def handle_frame(image, fout=None, show=False):
    # image = cv2.imread(path)
    if image is None:
        # logging.warning(("File not found", path))
        return None, None, None, None, None
    cropped, w, h = prepare_frame(image)
    if cropped is None:
        return None, None, None, None, None
    cont, box = find_main_countour(cropped)
    if cont is None:
        return None, None, None, None, None
    p1, p2 = geom.calc_box_vector(box)
    if p1 is None:
        return None, None, None, None, None
    angle = geom.get_vert_angle(p1, p2, w, h)
    shift = geom.get_horz_shift(p1[0], w)
    draw = fout is not None or show
    if draw:
        cv2.drawContours(image, [cont], -1, (0,0,255), 3)
        cv2.drawContours(image,[box],0,(255,0,0),2)
        cv2.line(image, p1, p2, (0, 255, 0), 3)
        msg_a = "Angle {0}".format(int(angle))
        msg_s = "Shift {0}".format(int(shift))
        cv2.putText(image, msg_a, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        cv2.putText(image, msg_s, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
    if fout is not None:
        cv2.imwrite(fout, image)
    if show:
        cv2.imshow("image", image)
        cv2.imshow("cropped", cropped)
        cv2.waitKey(1)
    return image, angle, shift, w, h
'''
def prepare_frame2(image):
    height, width = image.shape[:2]
    crop = image[3 * height / 4: height, width / 4:3 * width/ 4]
    crop = adjust_brightness(crop, tconf.brightness)
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)
    rc, gray = cv2.threshold(blurred, tconf.threshold, 255, 0)
    return gray, width / 2, height / 4

def handle_frame2(image, fout=None, show=False):
    # image = cv2.imread(path)
    if image is None:
        logging.warning(("File not found", path))
        return None, None, None, None, None
    height, width = image.shape[:2]
    cropped, w, h = prepare_frame2(image)
    if cropped is None:
        return None, None, None, None, None
    cont, box = find_main_countour(cropped)
    if cont is None:
        return None, None, None, None, None
    p1, p2 = geom.calc_box_vector(box)
    if p1 is None:
        return None, None, None, None, None
    angle = geom.get_vert_angle(p1, p2, w, h)
    shift = geom.get_horz_shift(p1[0], w)
    draw = fout is not None or show
    if draw:
        w_offset = (width - w) / 2
        h_offset = (height - h)
        dbox = geom.shift_box(box, w_offset, h_offset)
        cv2.drawContours(image,[dbox],0,(255,0,0),2)
        dp1 = (p1[0] + w_offset, p1[1] + h_offset)
        dp2 = (p2[0] + w_offset, p2[1] + h_offset)
        cv2.line(image, dp1, dp2, (0, 255, 0), 3)
        msg_a = "Angle {0}".format(int(angle))
        msg_s = "Shift {0}".format(int(shift))
        cv2.putText(image, msg_a, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        cv2.putText(image, msg_s, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
    if fout is not None:
        cv2.imwrite(fout, image)
    if show:    
        cv2.imshow("image", image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            return None, None, None, None, None
    return image, angle, shift, w, h
'''
# if __name__ == '__main__':
#     logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
#     pic = "1"
#     if len(sys.argv) > 1:
#         pic = sys.argv[1]

#     """
#     fname = "photos/" + pic + ".jpg"
#     angle, shift = handle_frame2(fname, fout="out.jpg", show=True)
#     print "Angle", angle, "Shift", shift
#     """
#     for f in os.listdir("test"):
#         a, s = handle_frame("test/" + f, show=True)
#                                    