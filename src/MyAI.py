# ======================================================================
# FILE:        MyAI.py
#
# AUTHOR:      Abdullah Younis
#
# DESCRIPTION: This file contains your agent class, which you will
#              implement. You are responsible for implementing the
#              'getAction' function and any helper methods you feel you
#              need.
#
# NOTES:       - If you are having trouble understanding how the shell
#                works, look at the other parts of the code, as well as
#                the documentation.
#
#              - You are only allowed to make changes to this portion of
#                the code. Any changes to other portions of the code will
#                be lost when the tournament runs your code.
# ======================================================================

from Agent import Agent

class MyAI ( Agent ):

    def __init__ ( self ):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================
        #-----variables about position----
        self.x = 0
        self.y = 0
        self.direction = 1 # 0 is up 1 is right ....
        self.move_num = 0
        #-----variables about game state----
        self.have_gold = False
        self.wumpus_alive = True
        self.last_action=None
        self.have_arrow=True
        self.hunting_wumpus=False
        #----variables about the board----
        self.width = 8
        self.height = 8
        self.board = [[-1 for x in range(8) ] for  _ in range(8)]
        #we know the first one is safe
        self.board[0][0] = 0
        #----path to retrace after you get the gold
        self.trail = []
        self.path_direction = 1
         
        #----used to be able to plan steps you know are safe and need to be taken befor the next descision---
        self.queue = []


        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================

    def getAction( self, stench, breeze, glitter, bump, scream ):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================
        #default action to be nothing so we know when a intelegent descision has been made
        

        #if the place starts out as a 
        if(self.move_num == 0):
            #if its stench we can actually use our arrow to determine its exact location
            if(breeze):
                return Agent.Action.CLIMB
            if(stench):
                #try to shoot your shot to determine the location of the wumpus
                self.shoot_your_shot()
                self.have_arrow=False
        
        if(scream):
            self.wumpus_alive = False 
        #update variables
        self.move_num +=1
        action = None
        reason = "NONE"

        #handle hitting the walls
        if(bump):
            #print("BUMP____________________")
            self.handle_walls()
        
        #take the queue action if it exits 
        if(len(self.queue) > 0):
            action,reason =  self.follow_queue()
            #print(reason)
            return action
        
        
        if(self.move_num >= 50):
            self.return_to_exit()
            return self.getAction(stench,breeze,glitter,bump,scream)
        
        #in this position we want to analyze the world around us 
        self.update_board(stench,breeze)
        
        #print("player X:",self.x,"Y:",self.y,"Dir:",self.direction)
        #self.print_board()

        #if there is gold pick it up
        if(glitter):
            #setup the queue so we go home
            self.return_to_exit()
            return Agent.Action.GRAB
        
        best_pos = self.find_next_position()
        #otherwise we want to move to a new safe square
        if(best_pos == -1):
            #we are just leaving
            #print("No good actions")
            return self.getAction(stench,breeze,glitter,bump,scream)

        if(best_pos != None):
            self.path_to_position(best_pos[0],best_pos[1])

        #call ourselves to get acces to the queue
        action,reason =  self.follow_queue()
        #print(reason)
        return action
        

        

        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================
    
    # ======================================================================
    # YOUR CODE BEGINS
    # ======================================================================

    #IMPLEMENT PRIORITY QUEUE TO SELECT THE NEXT BEST PLACE TO VISIt
    def shoot_your_shot(self):
        #Shoot a shot to the right, if it kills the wumpus you're safe otherwise
        #move forward and avoid the position to the top
        self.board[1][0] = 101 #assume there is a wumpus at the top
        self.board[0][1] = 1
        #if there is thats great, otherwise we will shoot it and kill it and then it won't matter
        self.queue.append((Agent.Action.SHOOT,"shoot wumpus"))

    def distance_from_player(self,x,y):
        return (self.x-x)**2 + (self.y-y)**2


    def position_probability(self,position_num): 
        danger = 0
        str_pos = "00"+str(position_num)
        items = [int(x) for x in str_pos[::-1]]
        visited_sides =  items[0]
        pits = items[1]
        wumpuses = items[2]

        if(wumpuses != visited_sides):
            wumpuses = 0
        if(pits != visited_sides):
            pits = 0
        
        
        if(self.wumpus_alive):
            if(wumpuses >=2):
                #we know this is the exact position of the wumpus
                #so lets shoot it if its convienent
                return 42 
            danger+=10*wumpuses# this is is a safe spot and the best to move to to
            
        danger += 10*pits
            
        return danger 
        
    def find_next_position(self):
        #goes to the lowest non zero position, the safest place to go to
        best_val = 20000
        best_pos = None
        worst_val = -20000
        for y in range(self.height):
            for x in range(self.width):
                val = self.board[y][x]
                if(val == 0 or val == -1):
                    continue
                val = self.position_probability(self.board[y][x])
                if(val == 42 and self.have_arrow):
                    #there is a wumpus in this position, shoot it if its convienent
                    if(self.x == x):
                        if(self.y < y):
                            self.ShootInDirection(0)
                        else:
                            self.ShootInDirection(2)
                    if(self.y == y):
                        if(self.x < x):
                            self.ShootInDirection(1)
                        else:
                            self.ShootInDirection(3)
                    return None

                if(val < best_val):
                    best_pos =(x,y)
                    best_val = val
                    best_val = val
                if(val > worst_val):
                    worst_val = val
                if(val == best_val):
                    if(self.distance_from_player(*best_pos) > self.distance_from_player(x,y)):
                        
                        best_pos =(x,y)
                        best_val = val
        #print("best position is %d,%d"%best_pos)
        #if(best_val == worst_val and best_val >=10):
        if(best_val >= 10):#*((self.move_num//10)+1)):
            self.return_to_exit()
            return -1
        
        return best_pos

    def path_to_position(self,x,y):
        #we can only move on safe tiles (t%10 == 0)
        #we start on this
        #print("pathing to",x,y)
        path =self.path_recursively(self.x,self.y,x,y,[]) 
        #print("The found path was", path)
        previous_dir = self.direction
        for direction in path:
            self.moveDirection_NonRelative(previous_dir,direction,"pathing to position %d,%d"%(x,y))
            previous_dir = direction
        #print("that path is",self.queue)



    def path_recursively(self,cur_x,cur_y,goal_x,goal_y,visited): 
        best_path = None
        for direction,delta_x,delta_y in [[0,0,1],[1,1,0],[2,0,-1],[3,-1,0]]:
            new_x = cur_x + delta_x
            new_y = cur_y + delta_y
            if((new_x,new_y) in visited):
                continue #don't spawn something for visited nodes
            if(new_x == goal_x and new_y == goal_y):
                return [direction]
            
            if(self.board[new_y][new_x] != 0):
                continue #don't spawn somethign on unsafe paths


            path = self.path_recursively(new_x,new_y,goal_x,goal_y,visited + [(cur_x,cur_y)])

            if(path == -1):
                continue #we don't want to propigate dead heads
            if(best_path == None):
                best_path = [direction] + path
            elif(len(path) < len(best_path)):
                best_path = [direction] + path
         
            
        if(best_path == None):
            #if we got here none of the paths we spawned worked out
            return -1

        return best_path
        


    #handle updaing the board
    
    def handle_box(self,new_x,new_y,breeze,stench):
        cur_val = self.board[new_y][new_x] 
        if(cur_val%10 == 0):
            return #don't update safe one
        if(cur_val == -1):
            cur_val = 0
        
        #keep track of the number of tiles we have visited with the first num
        cur_val += 1 
        if(breeze):
            cur_val += 10
        if(stench):
            cur_val += 100
        self.board[new_y][new_x] = cur_val

    def print_board(self,):
        [[[print("%8d"%x,end="") for x in y],print()] for y in self.board]
        return
    
    def update_weights(self,breeze,stench): 
        #The three areas we haven't been two around us are now dangerous
        
        #----- three values for value -----#
        #0: we have explored an adjencent square and there was no smell so its safe
        #10: theres a pit nearby
        #100: theres a wumpus nearby=
        #set the box we are standing on to be 1 
        for d,(x,y) in enumerate([(0,1),(1,0),(0,-1),(-1,0)]):
            new_x = self.x +x
            new_y = self.y +y
            if(new_x < 0 or new_x >= self.width):
                continue
            if(new_y < 0 or new_y >= self.height):
                continue
            self.handle_box(new_x,new_y,breeze,stench)

    def update_board(self,breeze,stench): 
    #used to keep the board update and let our safe search function make good desisions
        #we are here so the position we are standing is safe
        self.board[self.y][self.x] = 0
        self.update_weights(breeze,stench)

                
    def handle_walls(self):
        if(self.direction == 0):
            #facing up
            self.y += -1
            self.height = self.y+1
        if(self.direction == 1):
            #facing right
            self.x += -1
            self.width = self.x+1
        if(self.direction == 2):
            #facing down 
            self.y += 1
            self.height = self.y
        if(self.direction == 3):
            #facing left
            self.x += 1
         

                    
    #used when the player moved to keep our variables acurate
    def updatePosition(self):
        #we are moving forward in the direction we are facing
        #we are moving forward in the direction we are facing
        self.trail.append(self.direction)
        if(self.direction == 0):
            self.y +=1
        if(self.direction == 1):
            self.x +=1
        if(self.direction == 2):
            self.y -=1
        if(self.direction == 3):
            self.x -=1 

    def ShootInDirection(self,output_direction):
        input_direction = self.direction
        delta = (input_direction-output_direction)%4
        if(delta == 3):
            self.queue.append([Agent.Action.TURN_RIGHT,"lineing up shot"])
        else:
            for i in range(delta):
                self.queue.append([Agent.Action.TURN_LEFT,"Lineing up shot"])

        self.queue.append([Agent.Action.SHOOT,"360 no scope"])
        self.have_arrow=False

    #helper function to move north,south, east,west 
    def moveDirection_NonRelative(self,input_direction,output_direction,reason):
        #print("turning from",input_direction,"to",output_direction)
        delta = (input_direction-output_direction)%4
        if(delta == 0):
            self.queue.append([Agent.Action.FORWARD,reason])
            return
        if(delta == 3):
            self.queue.append([Agent.Action.TURN_RIGHT,reason])
        else:
            for i in range(delta):
                self.queue.append([Agent.Action.TURN_LEFT,reason])

        
        self.queue.append([Agent.Action.FORWARD,reason])

    def moveDirection(self,direction,reason):
        #determine the direction you are right now and where to go from ther
        self.moveDirection_NonRelative(self.direction,direction,reason)

    #THIS IS OUR SEARCH ALGORITHM it makes us visit as many places as possible
    



    #ALLOWS the game to be broken up into bigger actions than the actuators

    def follow_queue(self):
        action,reason = self.queue.pop(0)
        self.last_action= action
        if(action == Agent.Action.FORWARD):
            self.updatePosition()
        if(action == Agent.Action.TURN_LEFT):
            self.direction = (self.direction-1)%4
        if(action == Agent.Action.TURN_RIGHT):
            self.direction = (self.direction+1)%4
        return action,reason
        
    
    #END OF GAME MOVE BACK TO THE START AND CLIMB OUT
        
    def return_to_exit(self):    
        #for every item in the trail reverse it and add it to the queue
        self.path_to_position(0,0)
        self.queue.append([Agent.Action.CLIMB,"we out"])

        

        
    
    
    # ======================================================================
    # YOUR CODE ENDS
    # ======================================================================
