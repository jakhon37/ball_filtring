

from ctypes import pointer
import json
from ball_utils import im_read, im_save, make_circle, make_rect, read_json
import cv2
from symbol import except_clause


def draw_center_on_image(ball_data, img, color):
    frame, radius, color2, thickness = img, 10, (5, 55, 255), 2 
    for i, d in enumerate(ball_data):
        center_coordinates = d[3],d[4]
        img = make_circle(frame, center_coordinates, radius, color, thickness)
    return img
def draw_point_on_image(points, img):
    frame, radius, color, thickness = img, 5, (255, 255, 255), -1 
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


def initial_balls(ball_data, points):
    initial_ball_list = []
    for i, d in enumerate(ball_data):
        try:
            if d[3]>points[0][0] and d[3]<points[1][0]and d[4]>points[0][1] and d[4]<points[-1][1]:
                initial_ball_list.append(ball_data[i])
        except:
            print(f'iteration is done..')
    print(f'initial balls found: {len(initial_ball_list)}')
    return initial_ball_list



def find_intl_ball(intl_balls): # frame_k, conf, dm, cx, cy, x1, y1, x2, y2
    # -----------------------------------------------------------------
    # finding avarage x y centers indie intial position 
    x_center = []
    y_center = []
    for i in intl_balls:
        x_center.append(i[3])
    for i in intl_balls:
        y_center.append(i[4])
    avg_x = sum(x_center)/len(x_center)
    avg_y = sum(y_center)/len(y_center)
    print(f'avarage x: {avg_x} and y: {avg_y}')
    # -----------------------------------------------------------------
    
    # -----------------------------------------------------------------
    # find last right ball in initial position 
    for i in range(len(intl_balls)):
        if avg_x+15 >= intl_balls[-i-1][3]>=avg_x-15 and avg_y+15 >= intl_balls[-i-1][4]>=avg_y-15:
            initial_move = intl_balls[-i-1]
            break #continue
    print('initial move ' , initial_move)
    # -----------------------------------------------------------------


    filtered_intl_balls = []
    dropped_intl_balls = []
    im_w, im_h = 1080, 1920
    print('number of intl balls ',len(intl_balls))
    scale = 10.000001
    scale2 = 0.001
    print('scale ratio : ', im_w*scale)
    ubn_ball = 0
    for i, b in enumerate(intl_balls):
        try: 
            if not ubn_ball:
                ubn_ball  = intl_balls[i]
                print('ubn ball ', ubn_ball)
           # print(b)
            if intl_balls[i][3]<=intl_balls[i-1][3]-im_w*scale2: # im_w*0.02 = 21
                print(b)
                dropped_intl_balls.append(b) 

            if intl_balls[i][3]>=intl_balls[i-1][3]-im_w*scale <= intl_balls[i+1][3] and intl_balls[i][3]<=intl_balls[i-1][3]+im_w*scale or intl_balls[i][4]>=intl_balls[i-1][4]-im_w*scale and intl_balls[i][4]<=intl_balls[i-1][4]+im_w*scale: # im_w*0.02 = 21
                if  ubn_ball[3]>=intl_balls[i-1][3]-im_w*scale and ubn_ball[3]<=intl_balls[i-1][3]+im_w*scale or ubn_ball[4]>=intl_balls[i-1][4]-im_w*scale and ubn_ball[4]<=intl_balls[i-1][4]+im_w*scale:
                    #filtered_intl_balls.append(b)
                    ubn_ball  = intl_balls[i]
                    #print(b)

                else:
                    print('still false detection')
                    # dropped_intl_balls.append(b)
                    #pass
            else:
                print(b)
                ubn_ball = intl_balls[i]
                before_ubn = intl_balls[i-1]
                #if intl_balls[i][3]<=intl_balls[i-1][3]-im_w*scale2 or intl_balls[i][3]>=intl_balls[i-1][3]+im_w*scale2 or intl_balls[i][4]<=intl_balls[i-1][4]-im_w*scale2 or intl_balls[i][4]>=intl_balls[i-1][4]+im_w*scale2: # im_w*0.02 = 21
                if intl_balls[i][3]<=intl_balls[i-1][3]-im_w*scale2: # im_w*0.02 = 21
                    dropped_intl_balls.append(b)

          #  if intl_balls[i][3]>65:
           #     print(intl_balls[i])
                
            """     
            print(intl_balls[i][3])
            print(f"{intl_balls[i][3]} >= {intl_balls[i-1][3]-(im_w*scale)}")
            print(f"{intl_balls[i][3]} <= {intl_balls[i-1][3]+im_w*scale}")
            print(intl_balls[i][4])
            print(f"{intl_balls[i][4]}>={intl_balls[i-1][4]-im_w*scale}")
            print(f"{intl_balls[i][4]}<={intl_balls[i-1][4]+im_w*scale}")
            """
        except:
            print('excepting, need second ball position too') 

   # print(len(filtered_intl_balls))
   # print('scale ', im_w*scale)
    print('filtered intl balls ',len(filtered_intl_balls))
    print('dropped intl balls ',len(dropped_intl_balls))

    return filtered_intl_balls, dropped_intl_balls, initial_move

def filter_dm(ball_data, points):
    ball_fileted = []
    for i, d in enumerate(ball_data):
        try:
            if ball_data[i][2] > ball_data[i+1][2] and ball_data[i+1][2] > ball_data[i+2][2]: 
                pass
              #  print(d)
        except:
            print('no more value in list')
    print('filtering is done;;')
    return ball_fileted

def main(json_data, pose_data, img_path):
    # read inputs
    img = im_read(img_path)
    img_h, img_w, img_ch = img.shape
    print(img_w, img_h, img_ch)
    json_data = read_json(json_data)
    pose_data = read_json(pose_data)
    
    # print json data 
    list_ball_info = json_data["ball_data"]
    print('ball ceter length: ', len(list_ball_info))
    # for i in list_ball_info:
    #     print('ball ', (i))
    
    # key points 
    key_points = pose_data[0]["keypoints"]
    print('key points length', len(key_points))
    knee = [int(key_points[42]),int(key_points[43])]
    big_toe = [int(key_points[63]),int(key_points[64])]
    neck = [int(key_points[54]),int(key_points[55])]
    pose_points = [knee, big_toe, neck]
    points = ball_area(pose_points)
#    print(points)
    
    
    
    
    # filter ball data
    
    
     
    list_initial_balls = initial_balls(list_ball_info, points)
       # list_ball_info_filt = initial_balls(list_ball_info, points)

    filtered_initial_balls, dropped_intl_balls, initial_move = find_intl_ball(list_initial_balls)


    # draw ceters on image 
    list_ball_info = list_ball_info
    img = draw_center_on_image(list_ball_info, img, color=(5, 55, 255))        
  #  img = draw_center_on_image(list_initial_balls, img, color=(255, 55, 255)) 
    img = draw_center_on_image(filtered_initial_balls, img, color=(255, 55, 255)) 
    img = draw_center_on_image(dropped_intl_balls, img, color=(255, 55, 55)) 
          
    img = draw_point_on_image(points, img)        
    img = make_rect(img, points[0], points[3], color=(155, 255, 133), thickness=2)
    
    # save image locally 
    out_path = "/".join(img_path.split("/")[0:-1])
    print(out_path)
    out_name = img_path.split("/")[-1].split(".")[0]
    im_save(img, out_path, out_name)
    img_scale = 0.5
    img = cv2.resize(img, (int(img_w*img_scale), int(img_h*img_scale))) 
    cv2.imshow('image',img)
    cv2.waitKey(0)
    print('main is done..')
    return

if __name__=="__main__":
    
    json_data = 'data/06m_out/06m_info.json'
    pose_data = 'data/alphapose-results.json'
    img = 'data/06m_pose.jpg'
    
    
    main(json_data, pose_data, img)