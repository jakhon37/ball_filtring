

from ctypes import pointer
import json
from ball_utils import im_read, im_save, make_circle, make_rect, read_json
import cv2
from symbol import except_clause

# draw circles around each ball 
def draw_center_on_image(ball_data, img, color):
    frame, radius, color2, thickness = img, 10, (5, 55, 255), 2 
    for i, d in enumerate(ball_data):
        center_coordinates = d[3],d[4]
        img = make_circle(frame, center_coordinates, radius, color, thickness)
    return img
# draw ball center as points on image 
def draw_point_on_image(points, img):
    frame, radius, color, thickness = img, 5, (255, 255, 255), -1 
    for i, d in enumerate(points):
        center_coordinates = d[0],d[1]
        img = make_circle(frame, center_coordinates, radius, color, thickness)
    return img

# find initial ball movement area in front of person 
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

# filter only balls inside initial ball movement area 
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


# find last key ball before initial ball movement 
def find_intl_ball(intl_balls): # frame_k, conf, dm, cx, cy, x1, y1, x2, y2
    # -----------------------------------------------------------------
    # finding avarage x y centers in intial position 
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
    
    return initial_move

# after detection of ball movement / tracking the ball / not completed 
def ball_track(ball_data, initial_move):
    print('function ball_track ...')
    filtered_intl_balls = []

    for i, bal in enumerate(ball_data):
        try:
            if initial_move[0]==ball_data[i][0] and initial_move[3]-ball_data[i+1][3]>0 and initial_move[3]-ball_data[i+2][3]>0:
                print('ball is moving to left side')
            elif initial_move[0]==ball_data[i][0] and initial_move[3]-ball_data[i+1][3]<0 and initial_move[3]-ball_data[i+2][3]<0:
                print('ball is moving to right side')
                print(initial_move, ball_data[i+1],  ball_data[i+2])
            elif initial_move[0]==ball_data[i][0] and initial_move[3]-ball_data[i+1][3]==0 and initial_move[3]-ball_data[i+2][3]==0:
                print('ball is moving stright ')
                print(initial_move, ball_data[i+1],  ball_data[i+2])
                break
            
            
            if initial_move[0]==ball_data[i][0] and initial_move[3]-ball_data[i+2][3]>0 and initial_move[3]-ball_data[i+3][3]>0:
                print('ball is moving to left side, / false detection with ball 2')
            elif initial_move[0]==ball_data[i][0] and initial_move[3]-ball_data[i+2][3]<0 and initial_move[3]-ball_data[i+3][3]<0:
                print(initial_move[0], ball_data[i+2][3], ball_data[i+3][3])
                print('ball is moving to right side  / false detection with ball 2')
                print(initial_move, ball_data[i+1],  ball_data[i+2])
            if initial_move[0]==ball_data[i][0] :
                print(initial_move, ball_data[i+1],  ball_data[i+2])
        except:
            print('exception')
            pass
    
    
    return



# filter ball if diamter of second ball is bigger than first one  
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



# main function to use above functions and process ball info and write outputs on image 
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

    initial_move = find_intl_ball(list_initial_balls)


    # draw ceters on image 
    list_ball_info = list_ball_info
    img = draw_center_on_image(list_ball_info, img, color=(5, 55, 255))        
  #  img = draw_center_on_image(list_initial_balls, img, color=(255, 55, 255)) 
    #img = draw_center_on_image(filtered_initial_balls, img, color=(255, 55, 255)) 
    img = draw_center_on_image(list_initial_balls, img, color=(255, 55, 55)) 
    img = draw_center_on_image([initial_move], img, color=(155, 255, 155)) 
          
    img = draw_point_on_image(points, img)        
    img = make_rect(img, points[0], points[3], color=(155, 255, 133), thickness=2)
    ball_track(list_ball_info, initial_move)
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