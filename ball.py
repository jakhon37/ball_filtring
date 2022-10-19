

from ctypes import pointer
import json
from ball_utils import im_read, im_save, make_circle, make_rect, read_json
import cv2
from symbol import except_clause


def draw_center_on_image(ball_data, img):
    frame, radius, color, thickness = img, 10, (5, 55, 255), 2 
    for i, d in enumerate(ball_data):
        center_coordinates = d[3],d[4]
        img = make_circle(frame, center_coordinates, radius, color, thickness)
    return img
def draw_point_on_image(points, img):
    frame, radius, color, thickness = img, 10, (5, 55, 255), 2 
    for i, d in enumerate(points):
        center_coordinates = d[0],d[1]
        img = make_circle(frame, center_coordinates, radius, color, thickness)
    return img

def ball_area(pose_points):
    # [knee, big_toe, neck]
    limit_y_gorz_t = pose_points[0][1] # knee y value for searching below knee 
    limit_y_gorz_d = pose_points[1][1] # big_toe y value for searching above the right big toe 
    limit_x_vert_l = pose_points[1][0] # big toe x value for searching in right side of the person 
    limit_x_vert_r = pose_points[1][0]+ (pose_points[1][1]-pose_points[2][1]) # big toe X values + y dis between big toe and neck for searching in front of the person within 1.5 meters 
    
    pg_l, pg_r = [pose_points[1][0],limit_y_gorz_t], [limit_x_vert_r,limit_y_gorz_t] # pg1 for left top angle point knee/bigtoe , pg2 for right top angle point knee/bigtoe_y-neck_y 
    pv_l, pv_r = pose_points[1], [limit_x_vert_r,limit_y_gorz_d] # pv1 for left bottom anngle poit bigtoe, pv2 = right bottom angle poit 
    
    points = pg_l, pg_r, pv_l, pv_r
    return points



def filter_dm(ball_data, points):
    ball_fileted = []
    for i, d in enumerate(ball_data):
        try:
            # if ball_data[i][2] > ball_data[i+1][2] and ball_data[i+1][2] > ball_data[i+2][2]:
            # if ball_data[i][2] < ball_data[i+1][2]*0.8 and ball_data[i][2] < ball_data[i+2][2]*0.5 and d[0]>points[0][0] and d[0]>points[1][0] and d[1]>points[0][1] and d[1]>points[-1][1]:
            # if d[3]>points[0][0] and d[3]>points[1][0] and d[4]>points[0][1] and d[4]>points[-1][1]:
            if d[3]>points[0][0] and d[3]<points[1][0]and d[4]>points[0][1] and d[4]<points[-1][1]:
                ball_fileted.append(ball_data[i])
                print(d)
        except:
            print('no more value in list')
    print('filtering is done;;')
    return ball_fileted

def main(json_data, pose_data, img_path):
    # read inputs
    img = im_read(img_path)
    json_data = read_json(json_data)
    pose_data = read_json(pose_data)
    
    # print json data 
    list_ball_info = json_data["ball_data"]
    print('ball ceter length: ', len(list_ball_info))
    
    # key points 
    key_points = pose_data[0]["keypoints"]
    print('key points length', len(key_points))
    knee = [int(key_points[42]),int(key_points[43])]
    big_toe = [int(key_points[63]),int(key_points[64])]
    neck = [int(key_points[54]),int(key_points[55])]
    pose_points = [knee, big_toe, neck]
    points = ball_area(pose_points)
    print(points)
    
    # filter ball data 
    list_ball_info = filter_dm(list_ball_info, points)
    
    # draw ceters on image 
    list_ball_info = list_ball_info
    img = draw_center_on_image(list_ball_info, img)        
    img = draw_point_on_image(points, img)        
    img = make_rect(img, points[0], points[3], color=(155, 255, 133), thickness=2)
    
    # save image locally 
    out_path = "/".join(img_path.split("/")[0:-1])
    print(out_path)
    out_name = img_path.split("/")[-1].split(".")[0]
    im_save(img, out_path, out_name)
    
    print('main is done..')
    return

if __name__=="__main__":
    
    json_data = '/Users/jakhon37/pyProjects/ball_detection/data/06m_out/06m_info.json'
    pose_data = '/Users/jakhon37/pyProjects/ball_detection/data/alphapose-results.json'
    img = '/Users/jakhon37/pyProjects/ball_detection/data/06m_pose.jpg'
    
    
    main(json_data, pose_data, img)