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
        #----variables about the board----
        self.width = 7
        self.height = 7
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
        
        print("player X:",self.x,"Y:",self.y,"Dir:",self.direction)
        self.print_board()
        next_best = self.find_next_position()
        print("next best move:",next_best)


        if(self.move_num == 0):
            if(stench or breeze):
                return Agent.Action.CLIMB
        

        self.move_num +=1


        action = None
        reason = "NONE"

        
        if(len(self.queue) > 0):
            action,reason =  self.follow_queue()
            #print(reason)
            return action
        
        if(bump):
            self.handle_walls()
        
        if(self.move_num >= 50):
            self.return_to_exit()
            return self.getAction(stench,breeze,glitter,bump,scream)
        
        #in this position we want to analyze the world around us 
        self.update_board(stench,breeze,glitter,bump,scream)
        
        #if there is gold pick it up
        if(glitter):
            #setup the queue so we go home
            self.return_to_exit()
            return Agent.Action.GRAB
        
        #otherwise we want to move to a new safe square
        self.safeSearch()

        #call ourselves to get acces to the queue
        action,reason =  self.follow_queue()
        print(reason)
        return action
        

        

        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================
    
    # ======================================================================
    # YOUR CODE BEGINS
    # ======================================================================

    #IMPLEMENT PRIORITY QUEUE TO SELECT THE NEXT BEST PLACE TO VISIt
    def distance_from_player(self,x,y):
        return (self.x-x)**2 + (self.y-y)**2

    def position_probability(position_num):
        if(position_num %10 == 0):
            return 0 #this spot is totally safe
        if(position_num %10 == 1):
            return 1000 #this spot is unknown and completely dangerous
        danger = 10
        if(danger > 10):
            danger += position_num%100 * 25
        if(danger > 100):
            danger += position_num%1000 * 50
        return danger
        
    def find_next_position(self):
        #finds the overall lowest position and measure the best one
        best_val = -20000
        best_pos = None
        for y in range(self.height):
            for x in range(self.width):
                val = self.board[y][x]
                if(val > best_val):
                    best_pos =(x,y)
                    best_val = val
                if(val == best_val):
                    if(self.distance_from_player(*best_pos) > self.distance_from_player(x,y)):
                        best_pos =(x,y)
                        best_val = val
        #print("best position is %d,%d"%best_pos)
        return best_pos

    def path_to_pos(self,x,y):
        path = safe_path_to_position_recurse(self.x,self.y,x,y,[])

    def safe_path_to_position_bfs(self,goal_x,goal_y):
        #bfs 
        
        #create a dictonary to map 0,4

        frontier = []
        path = []
        cur_x = self.x
        cur_y = self.y
        #expand our node and add it to the frontier
        in_goal = False
        frontier.append((cur_x,cur_y))
        while(len(frontier)!=0):
            #look at the 4 nearby
            #and add any of them that are safe to the frontier 
            cur_x,cur_y = frontier.pop(0)
            print(cur_x,cur_y)
            for direction,(delta_x,delta_y) in zip([1,2,3,4],[(0,-1),(1,0),(0,1),(1,0)]):
                new_x = cur_x + delta_x
                new_y = cur_y + delta_y
                if(self.board[new_y][new_x] == 1):
                    frontier.append((new_x,new_y))
                
        
    

    #handle updaing the board
    
    def handle_box(self,new_x,new_y,breeze,stench):
        value = self.board[new_y][new_x]
        danger = breeze or stench
        if(breeze):
            value = -10
        if(stench):
            value= -1000
        if(self.board[new_y][new_x] == -1):
            #unexplored, could be danger
            self.board[new_y][new_x] = 1
        elif(self.board[new_y][new_x] < -1 and danger):
            #we have previously suspected this spot to be danger
                self.board[new_y][new_x] = self.board[new_y][new_x] * 2

    def print_board(self,):
        [[[print("%4d"%x,end="") for x in y],print()] for y in self.board[::-1]]
        return
    
    def update_weights(self,breeze,stench): 
        #The three areas we haven't been two around us are now dangerous
        
        #----- three values for value -----#
        #0: we have explored an adjencent square and there was no smell so its safe
        #10: theres a pit nearby
        #100: theres a wumpus nearby=
        #set the box we are standing on to be 1 
        for d,(x,y) in enumerate([(0,-1),(1,0),(0,1),(-1,0)]):
            new_x = self.x +x
            new_y = self.y +y
            if(new_x < 0 or new_x >= self.width):
                continue
            if(new_y < 0 or new_y >= self.height):
                continue
            self.handle_box(new_x,new_y,breeze,stench)

    
    #used to keep the board update and let our safe search function make good desisions
    def update_board(self,stench,breeze,glitter,bump,scream):
        #we are here so the position we are standing is safe
        self.board[self.y][self.x] = 0
        self.update_weights(breeze,stench)

                
    def handle_walls(self):
        if(self.direction == 0):
            #facing up
            self.y += -1
            self.height = self.y
        if(self.direction == 1):
            #facing right
            self.y += -1
            self.width = self.x
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
        
    #helper function to move north,south, east,west 
    def moveDirection(self,direction,reason):
        #determine the direction you are right now and where to go from there
        delta = self.direction - direction
        if(delta == 0):
            self.queue.append([Agent.Action.FORWARD,reason])
            return
        direction  = Agent.Action.TURN_LEFT
        if(delta < 0):
            direction = Agent.Action.TURN_RIGHT
        self.queue.extend([[direction,reason] for _ in range(abs(delta))])
        self.queue.append([Agent.Action.FORWARD,reason])

    #THIS IS OUR SEARCH ALGORITHM it makes us visit as many places as possible
    
    def safeSearch(self):
        #uses self.danger to search the next optimial move  
        #simple model, find the direction that is the highest values actual move
        best_move = -1000
        best_dir = 1
        for d,(x,y) in enumerate([(0,1),(1,0),(0,-1),(-1,0)]):
            new_x = self.x +x
            new_y = self.y +y
            if(new_x < 0 or new_x > self.width):
                continue
            if(new_y < 0 or new_y > self.height):
              continue
            if(self.board[new_y][new_x] > best_move): #and self.board[new_y][new_x] < 1 ):
                best_dir = d
                best_move = self.board[new_y][new_x]
            #print("Choice %d:"%d,self.board[new_y][new_x])
        
        #print("we chose %d"%best_dir)
        self.moveDirection(best_dir,"safeSearch going towards %d"%best_dir)
        



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
        for i in self.trail[::-1]:
            ##print("undoing %d",i)
            self.moveDirection((i+2)%4,"returning home")
        self.queue.append([Agent.Action.CLIMB,"returning home"])

        

        
    
    
    # ======================================================================
    # YOUR CODE ENDS
    # ======================================================================
