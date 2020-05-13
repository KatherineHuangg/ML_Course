"""
The template of the script for the machine learning process in game pingpong
"""
import math
# Import the necessary modules and classes
from mlgame.communication import ml as comm
def posOrNeg(a):
    return 1 if a>0 else -1

def ml_loop(side: str):
    """
    The main loop for the machine learning process
    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```
    @param side The side which this script is executed for. Either "1P" or "2P".
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    def move_to(player, pred) : #move platform to predicted position to catch ball 
        if player == '1P':
            if scene_info["platform_1P"][0]+20  > (pred-10) and scene_info["platform_1P"][0]+20 < (pred+10): return 0 # NONE
            elif scene_info["platform_1P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left
        else :
            if scene_info["platform_2P"][0]+20  > (pred-10) and scene_info["platform_2P"][0]+20 < (pred+10): return 0 # NONE
            elif scene_info["platform_2P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left

    ball_y=419
    ball_x=50
    blocker_x = 90

    def ml_loop_for_1P(): 
        if scene_info["ball_speed"][1] > 0 : # 球正在向下 # ball goes down
            x = ( scene_info["platform_1P"][1]-scene_info["ball"][1] ) // scene_info["ball_speed"][1] # 幾個frame以後會需要接  # x means how many frames before catch the ball
            pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x)  # 預測最終位置 # pred means predict ball landing site 
            bound = pred // 200 # Determine if it is beyond the boundary
            if (bound > 0): # pred > 200 # fix landing position
                if (bound%2 == 0) : 
                    pred = pred - bound*200                    
                else :
                    pred = 200 - (pred - 200*bound)
            elif (bound < 0) : # pred < 0
                if (bound%2 ==1) :
                    pred = abs(pred - (bound+1) *200)
                else :
                    pred = pred + (abs(bound)*200)
            return move_to(player = '1P',pred = pred)
        else : # 球正在向上 # ball goes up
            return move_to(player = '1P',pred = 100)



    def ml_loop_for_2P():  # as same as 1P
        if scene_info["ball_speed"][1] > 0 : 
            return move_to(player = '2P',pred = 100)
        else : 
            x = ( scene_info["platform_2P"][1]+30-scene_info["ball"][1] ) // scene_info["ball_speed"][1] 
            pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x) 
            bound = pred // 200 
            if (bound > 0):
                if (bound%2 == 0):
                    pred = pred - bound*200 
                else :
                    pred = 200 - (pred - 200*bound)
            elif (bound < 0) :
                if bound%2 ==1:
                    pred = abs(pred - (bound+1) *200)
                else :
                    pred = pred + (abs(bound)*200)
            return move_to(player = '2P',pred = pred)

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

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

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            ball_served = True
            dir_y = 0
            dir_x = 0
            lastpos_x = scene_info['ball'][0]
            lastpos_y = scene_info['ball'][1]
            platform_x = scene_info['platform_1P'][0] + 20
            rebound_x = 0
            rebound_y = 0
            lastdir_x = 0
        
        else:

            
            dir_x=ball_x-scene_info['ball'][0] ##上一個球的位置-目前球的位置為方向,負往右正往左
            #print(scene_info,ball)
            dir_y=ball_y-scene_info['ball'][1] ##負往下正往上
            
            dir_blocker_x = blocker_x - scene_info['blocker'][0] #負向右正向左

            ball_x = scene_info['ball'][0] ##目前(x,y)
            ball_y = scene_info['ball'][1]
            blocker_x = scene_info['blocker'][0]

            platform_x = scene_info['platform_1P'][0] + 20

            pre_ball_x=ball_x
            pre_ball_y=ball_y
            pre_blocker_x = blocker_x

            if dir_y < 0:##球向下才要預測
                if ball_y>410:
                    if dir_x<0:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})                        
                    elif dir_x>0:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                    else:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
                elif dir_x>0:
                    while pre_ball_y<400:
                        pre_ball_x -= dir_x
                        pre_ball_y -= dir_y

                    if pre_ball_x >= 200:
                        pre_ball_x = 400 - pre_ball_x
                        dir_x= 0 - dir_x
                    elif pre_ball_x <= 0:
                        pre_ball_x = 0 - pre_ball_x
                        dir_x= 0 - dir_x

                    
                    if pre_ball_x > platform_x:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                    elif pre_ball_x < platform_x:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                    else:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
                
                elif ball_y > 250:#開始預測
                
                    while pre_ball_y<400:
                        pre_ball_x -= dir_x
                        pre_ball_y -= dir_y

                    if pre_ball_x >= 200:
                        pre_ball_x = 400 - pre_ball_x
                        dir_x= 0 - dir_x
                    elif pre_ball_x <= 0:
                        pre_ball_x = 0 - pre_ball_x
                        dir_x= 0 - dir_x

                    
                    if pre_ball_x > platform_x:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                    elif pre_ball_x < platform_x:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                    else:
                        comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})

            else :#球往上不預測
                if platform_x < 100:
                    comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                elif platform_x >100:
                    comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                else:
                    comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})

            