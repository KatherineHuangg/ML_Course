"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import math
import random as rd
import pickle
from os import path
import math
def ml_loop(side: str):
    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    check_direction=False
    p2 =False
    person=False
    Pdirect=0
    set_init_direct=0
    filelog=path.join(path.dirname(__file__),'save','seg_data.pickle')
    with open (filelog,'rb')as file:
        log=pickle.load(file)
    filelog=path.join(path.dirname(__file__),'save','block_go2.pickle')
    with open (filelog,'rb')as file:
        blocker=pickle.load(file)
    # file_p1 = path.join(path.dirname(__file__)+"\\save\\"+"Model_1.pickle")
    model=Ball_place_model(blocker,log)
    def move_to(player, pred) : #move platform to predicted position to catch ball 
        if player == '1P':  
            if scene_info["platform_1P"][0]==5 and pred>5 and pred<30 and scene_info["ball_speed"][1]>0:
                return  0      
            elif  scene_info["platform_1P"][0]==155 and pred<195 and pred>160 and scene_info["ball_speed"][1]>0:
                return 0
            if scene_info["platform_1P"][0]+20 > pred :  return 2 # goes left
            elif scene_info["platform_1P"][0]+20 <pred :  return 1 # goes right
            else :  return 0 # NONE
        else :
            if scene_info["platform_2P"][0]+75  > pred : return 2 # goes left
            elif scene_info["platform_2P"][0]+75 <pred : return 1 # goes right
            else : return 0 # NONE
    def cut_the_ball():
        tmp=rd.randint(0,2)
        # if scene_info["ball_speed"][0]<0 : return 2 # goes left
        # elif scene_info["ball_speed"][0]>0: return 1 # goes right
        # else : return 1 # NONE
        if tmp==2: return 2 # goes left
        elif tmp==1: return 1 # goes right
        else : return 1 # NONE


    def ml_loop_for_1P(): 
        # model.Change_frame(scene_info["ball"])   #check now y frame
        if scene_info["ball_speed"][1]>0: 
            model.checkup=False
            if scene_info["ball"][1]+scene_info["ball_speed"][1]>=415 :
                if scene_info["ball"][0] ==0 or scene_info["ball"][1]==195:
                    #print("leave")
                    return 0
                ball_hit_place=[scene_info["ball"][0]+scene_info["ball_speed"][0],-415]
                # if ball_hit_place[0]>195:   ball_hit_place[0]=195
                # elif ball_hit_place[0]<0:   ball_hit_place[0]=0
                if ball_hit_place[0]>=195 or ball_hit_place[0]<=0:
                    return 0
                model.pre_point=ball_hit_place[0]
                yy=scene_info["ball_speed"][1]   #go up
                speed_up=True
                reverse=True
                if scene_info["ball_speed"][0]>0 :                
                    speed_up= model.UP_Move_check(scene_info["frame"],[yy+3,yy],ball_hit_place)
                    if not speed_up and scene_info["platform_1P"][0]<160:
                        # #print("speed up speed >0")
                        model.temp=True
                        return 1
                    elif ball_hit_place[0]<190:
                        reverse=model.UP_Move_check(scene_info["frame"],[-yy,yy],ball_hit_place) 
                        if not reverse:
                            # #print("reverse speed>0")
                            model.temp=True
                            return 2                      
                        # #print("none false")
                        model.temp=False
                        return 0  
                    model.temp=False
                    # #print("none no re")   
                    return 0         
                else:       
                    speed_up=model.UP_Move_check(scene_info["frame"],[-(yy+3),yy],ball_hit_place)
                    if not speed_up and scene_info["platform_1P"][0]>0:
                        # #print("speed up speed <0")
                        model.temp=True
                        return 2
                    elif ball_hit_place[0]>5:
                        reverse=model.UP_Move_check(scene_info["frame"],[yy,yy],ball_hit_place)
                        if not reverse:
                            model.temp=True
                            # #print("reverse speed<0")
                            return 1
                        model.temp=False
                        # #print("none false")
                        return 0
                    model.temp=False
                    # #print("none no re")
                    return 0             
            elif model.now_speed==True or (scene_info["frame"]-150)%200==0:    #the ball goes down  
                #slice system          
                model.checkdown+=1                           
                model.now_speed=False
                model.pre_point=model.Down_Move_check(scene_info["frame"],list(scene_info["ball_speed"]),[scene_info["ball"][0],-scene_info["ball"][1]])            
                # #print(model.pre_point)
                    
            elif scene_info["ball"][1]>260 and model.checkdown!=0:
                ww=model.Down_Move_check(scene_info["frame"],list(scene_info["ball_speed"]),[scene_info["ball"][0],-scene_info["ball"][1]]) 
                model.checkdown=0
                if model.pre_point!=ww:
                    #print(model.pre_point,ww,"Down Check twice!!!!!!!!!")
                    model.pre_point=ww
            return move_to(player='1P',pred=model.pre_point)                               
        else:
            model.now_speed=True
            if model.checkup==False and scene_info["ball"][1]<240:
                #print(scene_info["frame"],scene_info["ball"],"seeeeeeee")
                test,model.slope=model.Check_Waiting_Place(list(scene_info["ball_speed"]),list(scene_info["ball"]))
                #print(model.pre_point,test,scene_info["ball_speed"],scene_info["platform_1P"],"=======================")              
                # if test>160-abs(scene_info["ball_speed"][0]):
                #     model.uppoint=150
                # elif test<40+abs(scene_info["ball_speed"][0]):
                #     model.uppoint=50
                # else:
                #     if model.slop<0:
                #         model.uppoint=80
                #     else:
                #         model.uppoint=120
                if scene_info["ball_speed"][1]>=-24:
                    model.uppoint =(test*2+100)//3 
                else:
                    model.uppoint=test         
                model.checkup=True 
            elif scene_info["ball"][1]>=150 :
                return move_to(player='1P',pred=100)
                
           
            else:
                return move_to(player='1P',pred=model.uppoint)  
                
                
                

    def ml_loop_for_2P():  # as same as 1P
        if scene_info["ball_speed"][1] < 0 : 
            abs_speedX=abs(scene_info["ball_speed"][0])  #將speed設為正
            now_direct=0
            yseg = math.ceil((scene_info["platform_2P"][1]+30-scene_info["ball"][1] ) / scene_info["ball_speed"][1])  # 幾個frame以後會需要接  # x means how many frames before catch the ball
            if scene_info["ball_speed"][0]>0:  #球往右邊跑，等等由左邊開始計算
                xseg = math.ceil((195-scene_info["ball"][0])/abs_speedX) 
                now_direct=1
            else:                               #球往左邊跑，等等由右邊開始計算
                xseg = math.ceil(scene_info["ball"][0]/abs_speedX)   # 目前的xreg
                now_direct=0
            x_range_seg=math.ceil(195/abs_speedX)  #現在速度的xrangeseg
            last_reg=abs(int(yseg-xseg)%int(x_range_seg) )#最後的reg
            bound = abs(int((yseg-xseg)//x_range_seg +now_direct)%2)
            
            pred =abs(195*bound-last_reg*abs_speedX)
            if yseg<xseg:
                pred=scene_info["ball"][0]+yseg*scene_info["ball_speed"][0]
            # #print(pred,now_direct,yseg,xseg,last_reg,x_range_seg,bound,scene_info["ball"])    
            if scene_info["ball"][1]+scene_info["ball_speed"][1]<=80: return cut_the_ball()          
            else: return move_to(player = '2P',pred = pred)
        else : 
            
            return move_to(player = '2P',pred = 100)
                
            


    # 2. Inform the game process that ml process is ready
    comm.ml_ready()
    tmp=0
    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False
            start_frame=rd.randint(0,20)
            Pdirect=0
            person=True
            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information
        if scene_info["frame"]<=3:
            if scene_info["blocker"][0]>85:
                model.init_block_direction=0
            elif scene_info["blocker"][0]<85:
                model.init_block_direction=1
            
            
        # 3.4 Send the instruction for this frame to the game process
        if not ball_served and scene_info["frame"]>=150:
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})

            ball_served = True
            continue
        elif scene_info["frame"]<150:
            person=True
            if scene_info["ball"][1]>150:
                preson=True
            else:
                preson=False
            if person==True and side=="1P" or person==False and side=="2P":          
                if Pdirect==0:
                    comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                else:
                    comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
        else:
            if side == "1P":
                command = ml_loop_for_1P()  
                # if scene_info["ball"][1]>=415 or scene_info["ball"][1]==80:
                #     # temp=scene_info["ball_speed"][1]
                #     #print(command,scene_info["frame"],scene_info["ball"],scene_info["ball_speed"],scene_info["platform_1P"])                                                          
                # # if scene_info["ball"][1]==260 and scene_info["ball_speed"][1]>0:
                # #     #print(model.temp,scene_info["frame"],scene_info["ball"],scene_info["ball_speed"],"UP Check twice!!!!!!!!!!!")                                                          
                if command == 0:             
                    comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
                elif command == 1:
                    # if scene_info["ball"][1]==415:
                    #     #print("right")         
                    comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                else :
                    # if scene_info["ball"][1]==415:
                    #     #print("left")     
                    comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
            else:
                command = ml_loop_for_2P()
                if command == 0:               
                    comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
                elif command == 1:
                    comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                else :
                    comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
            


class Ball_place_model():
    #left init_dir=1 ,right init_dir=0   
    def __init__(self,data,seg_data): 
        self.data=data
        self.seg_data=seg_data
        self.init_block_direction=0
        self.pre_point=100
        self.now_speed=True
        self.checkdown=0
        self.checkup=False
        self.uppoint=100
        self.slop=-1
        self.temp=False
    #check_block_place
    def Block_Predict(self,frame)->int:    
        if frame<300:
            if self.init_block_direction==0:
                return -(self.data[frame,1]-85)+85,-self.data[frame,2]
            else:
                return self.data[frame,1],self.data[frame%114+114,2]
        else:
            if self.init_block_direction==0:
                return -(self.data[frame%114+114,1]-85)+85,-self.data[frame%114+114,2]
            else:
                return self.data[frame%114+114,1],self.data[frame%114+114,2]
 
    #x=(y-y0)/m+x0     
    def Check_Horizontal(self,start_point,block_line,m):
            x=(block_line[0][1]-start_point[1])/m +start_point[0]  
            # #print(x,block_line[0][1],"check_horizontal_line")
            if x>195 and x<200:
                x=195
            if x+5-block_line[0][0]>=0 and block_line[1][0]-x>=0:   
                x=(block_line[2]-start_point[1])/m +start_point[0]                 
                return [x,block_line[0][1]]        
            else:
                # #print(x,block_line[0][1],m,"not_hit_check_horizontal_line")
                return False
   

    def Check_wall(self,start_point,m,ball_speed,limit):
        y=m*(limit-start_point[0])+start_point[1] 
        if (y-start_point[1])%ball_speed[1]!=0:           
            y= start_point[1]+((y-start_point[1])//ball_speed[1]+1)*ball_speed[1]
        ball_place=[limit,y]       
        return ball_place


    def Check_Vertical(self,start_point,block_line,m,ball_speed,direction=0,seg_range=0):
        y=m*(block_line[0][0]-start_point[0])+start_point[1]
        if y-3>-235:
            return False
        if y-3+235<=0 and y+260>=0 and block_line[2]<=y:
            # if block_line[2]==y:
            #     return [block_line[0][0],block_line[2]+ball_speed[1]]
            return [block_line[0][0],block_line[2]]
        bug=0
        while block_line[2]>-260:
            if bug>4:
                #print("verticalbug")
                break
            else:
                bug+=1
            block_line[0][0]=block_line[0][0]+3*direction
            if m<0:           #left line
                if block_line[0][0]<=-5:
                    block_line[0][0]=-5
                    direction=-direction
                elif block_line[0][0]>=165:
                    block_line[0][0]=165
                    direction=-direction
            else:           #right line
                if block_line[0][0]<=30:
                    block_line[0][0]=30
                    direction=-direction
                elif block_line[0][0]>=200:
                    block_line[0][0]=200
                    direction=-direction
            y=m*(block_line[0][0]-start_point[0])+start_point[1]
            if y+235<=0 and y+260>=0 and block_line[2]+ball_speed[1]<=y: #block_line[2]-5+ball_speed[1]*(i-1)>=y:  
                # if y==block_line[2]:
                #     #print("test",y)
                #     return False 
                    
                # else:
                return [block_line[0][0],block_line[2]+ball_speed[1]]                    
            block_line[2]+=ball_speed[1]
        return False
            
    #if will touch  the block , hit to the opposite side
    def UP_Move_check(self,frame,ball_speed,ball_place):             
            seg_frame=self.seg_data[self.seg_data[:,0]==abs(ball_speed[0])+abs(ball_speed[1])][0]       #find the seg data     
            m=ball_speed[1]/ball_speed[0]       #斜率
            if ball_place[0]==0:    m=abs(m)
            elif ball_place[0]==195:    m=-abs(m)
            hor_y=-415+seg_frame[2]*ball_speed[1]       #downer line y_place
            placex,block_direction=self.Block_Predict(frame+1+seg_frame[2])     #frame:last frame before hit plateform 
            downer_line=[[placex-5,-260],[placex+30,-260],hor_y]      #y=260  
            # #print(placex,self.init_block_direction,"---up_check-----------")   
            bug=0                             
            while ball_place[1]<hor_y:          
                Hit= self.Check_Horizontal(ball_place,downer_line,m)
                if Hit==False:
                    if m>0:
                        ball_place= self.Check_wall(ball_place,m,ball_speed,195)                       
                    else:
                        ball_place= self.Check_wall(ball_place,m,ball_speed,0)                     
                    m=-m                    
                else:   return True
                
                if bug>5:
                    #print("upbug")
                    break
                else:
                    bug+=1
            return False
    
    def Down_Move_check(self,frame,ball_speed,ball_place):   
        seg_frame=self.seg_data[self.seg_data[:,0]==abs(ball_speed[0])+abs(ball_speed[1])][0]  #find the seg data     
        ball_speed[1]=-ball_speed[1]     
        m=ball_speed[1]/ball_speed[0]    
        if ball_place[0]==0:    m=abs(m)
        elif ball_place[0]==195:    m=-abs(m)
        if ball_place[1]!=-80:   
            last=math.ceil((-235-ball_place[1])/ball_speed[1])
            platseg=math.ceil((-415-ball_place[1])/ball_speed[1])
            hor_y=ball_place[1]+last*ball_speed[1]
            platform_y=ball_place[1]+platseg*ball_speed[1]
        else:
            hor_y=-80+seg_frame[2]*ball_speed[1]
            last=seg_frame[2] 
            platform_y=-80+seg_frame[1]*ball_speed[1]
        
        placex,block_direction=self.Block_Predict(frame+last)  #------------------------yseg
        
        left_line=[[placex-5,-235],[placex-5,-260],hor_y]         #x=placex-5
        right_line=[[placex+30,-235],[placex+30,-260],hor_y]      #x=placx+30       
        platform_line=[[-40,platform_y],[235,platform_y],-415]
        upper_line=[[placex,hor_y],[placex+30,hor_y],-240]
        # if ball_place[1]==-80:  
        #     #print(frame+last,frame,ball_speed,ball_place,placex,self.init_block_direction,"down check frame")
        vertical_check=False
        Hit=False
        bug=0
        while ball_place[1]>platform_y:         
            if bug>6:
                #print("downbug")
                break
            else:
                bug+=1
            if ball_place[1]>-260 and vertical_check==False:               
                if m<0:                                             #right
                    Hit=self.Check_Vertical(ball_place,left_line,m,ball_speed,block_direction,seg_frame[3])
                else:
                    Hit=self.Check_Vertical(ball_place,right_line,m,ball_speed,block_direction,seg_frame[3])
                # if Hit==False and ball_place[1]>hor_y:  #check upper
                #     Hit=self.Check_Horizontal(ball_place,upper_line,m)
                #     if Hit!= False:
                #         #print(Hit[0] ,"hit the upper")
                #         return -Hit[0] 
            else:
                Hit=False
            if Hit==False:
                if m<0:
                    Hit=self.Check_wall(ball_place,m,ball_speed,195)
                    # #print(Hit,"wall195")
                else:
                    Hit=self.Check_wall(ball_place,m,ball_speed,0)
                    # #print(Hit,"wall0")
                if Hit[1]>platform_y:
                    ball_place=Hit
                else:
                    # ball_place= self.Check_Horizontal(ball_place,platform_line,m)    
                    ball_place[0]=ball_place[0]+(-415-ball_place[1])/m
                    if ball_place[0]>195:
                       ball_place[0]=195
                    elif ball_place[0]<0:
                        ball_place[0]=0 
                    # #print(ball_place[0],"ball_place")                                   
                    return ball_place[0]
            else:    
                ball_place=Hit
                vertical_check=True
                if ball_place[0]<0:
                    ball_place[0]=0
                    continue
                elif ball_place[0]>195:
                    ball_place[0]=195
                    continue
                # #print(ball_place,m,"---verticla_done")
            m=-m  

    def Check_Waiting_Place(self,ball_speed,ball_place):
        seg_frame=self.seg_data[self.seg_data[:,0]==abs(ball_speed[0])+abs(ball_speed[1])][0]  #find the seg data          
        ball_speed[1]=-ball_speed[1]
        ball_place[1]=-ball_place[1]
        m=ball_speed[1]/ball_speed[0]
        if ball_place[1]==-415:
            platform_y=-415+seg_frame[1]*ball_speed[1]
        else:
            plat_seg=math.ceil((-80-ball_place[1])/ball_speed[1])
            platform_y=ball_place[1]+plat_seg*ball_speed[1]
        tmp=0
        bug=0
        while ball_place[1]<-80:
            if bug>5:
                #print("checkbug")
                break
            else:
                bug+=1
            if m<0:
                Hit=self.Check_wall(ball_place,m,ball_speed,0)
            else:
                Hit=self.Check_wall(ball_place,m,ball_speed,195)
            if Hit[1]>=-80:             
                ball_place[0]=ball_place[0]+(platform_y-ball_place[1])/m
                if ball_place[0]>195:   ball_place[0]=195
                elif ball_place[0]<0:   ball_place[0]=0 
                return ball_place[0] ,m          
            else:
                ball_place=Hit               
                m=-m
        

        
