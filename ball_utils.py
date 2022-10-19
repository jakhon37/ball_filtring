

import json
import cv2


def read_json(path):
    with open(path) as file:
        json_data = json.load(file)
    return json_data


def im_read(img_path):
    img = cv2.imread(img_path)
    return img
    
def im_save(img, path, name):
    img_out = (f"{path}/out_{name}.jpg")
    cv2.imwrite(img_out, img)  # Save image localy 
    



def make_circle(frame, center_coordinates, radius, color, thickness):
    frame = cv2.circle(frame, center_coordinates, radius, color, thickness)
    return frame 

def make_rect(frame, start_point, end_point, color, thickness):
    frame  = cv2.rectangle(frame, start_point, end_point, color, thickness)
    return frame