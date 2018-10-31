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
        #-----variables about game state----
        self.have_gold = False
        self.wumpus_alive = True
        self.last_action=None
        #----variables about the board----
        self.width = 7
        self.height = 7
        self.board = [[-1 for x in range(7) ] for  _ in range(7)]
        self.board[0][0] = 100
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
        action = None
        reason = "NONE"
        #print("Descision being made on:")
        #print("bump:",bump,"breeze",breeze,"glitter",glitter)

        
        if(bump):
            print("whoa we hit a wall")
            if(self.direction == 0):
                #we hit the top
                self.y = self.y-1
                self.height = self.y
                print("height",self.height)
            if(self.direction == 1):
                #we hit the right side
                self.x = self.x-1
                self.width = self.x
                print("width:",self.width)
            if(self.direction==2):
                self.y = self.y+1
            if(self.direction==3):
                self.x = self.x+1

        

        #we must follow the queue in case it has changed
        if(len(self.queue) > 0):
            reason = "QUEUE"
            action= self.follow_queue() 
            print(action)
            
        if(self.last_action!= Agent.Action.TURN_LEFT):
            self.update_board(stench,breeze,glitter,bump,scream)
            [[[print("%3d"%i,end=" ") for i in x],print()] for x in self.board]

        #handling the opening cases
        if(self.x == self.y and self.x == 0):
            if(stench or breeze):
                reason = "BAD START MOVE FORWARD 50/50 shot"
                #This is a really bad case we don't really know anyting but there is a hazard 
                #where we are standing so we will just walk forward and take the 50/50 chance
                self.moveDirection(1)
                action = self.follow_queue()
                return action

        #we found the gold, now we will pick it up
        if(glitter):
            reason = "FOUND GOLD"
            action = Agent.Action.GRAB
            self.have_gold=True
            self.return_to_exit()
            return action

        #once we have the gold we just want to go back the exact
        #way we came
        if(self.have_gold):
            reason = "we have the gold we are leaving"
            self.return_to_exit()
            action = self.follow_queue()

        
        #the wumpus has been killed
        if(scream):
            self.wumpus_alive = False

        #nothing has been chosen so we will do a regular search for one step
        if(action == None):
            reason="NOTHING TO DO WE EXPLORED"
            #if nothing has been chosen then we pick a random direction
            self.safeSearch()
            #self.SnakeMovement(bump)
            action =  self.follow_queue()

        print(reason)

        return action
        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================
    
    # ======================================================================
    # YOUR CODE BEGINS
    # ======================================================================

    def handle_box(self,new_x,new_y,breeze,stench):
        value = 30
        danger = breeze or stench
        if(breeze):
            value -=100
        if(stench):
            value-= 42
        if(self.board[new_y][new_x] == -1):
            #we belive that this spot could be a hole
            self.board[new_y][new_x] = value 
        elif(self.board[new_y][new_x] < -1 and danger):
            #we have previously suspected this spot to be a hole
                self.board[new_y][new_x] = self.board[new_y][new_x] * 2

    
    def update_weights(self,breeze,stench): 
        #The three areas we haven't been two around us are now dangerous
        
        #----- three values for value -----#
        #30: we have explored an adjencent square and there was no smell so its safe
        #-100: theres a pit nearby
        #-42: theres a wumpus nearby=
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
        self.board[self.y][self.x] = 1
        self.update_weights(breeze,stench)

                

                    
    #used when the player moved to keep our variables acurate
    def updatePosition(self):
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
    def moveDirection(self,direction):
        #determine the direction you are right now and where to go from there
        delta = self.direction - direction
        if(delta == 0):
            self.queue.append(Agent.Action.FORWARD)
            return
        direction  = Agent.Action.TURN_LEFT
        if(delta < 0):
            direction = Agent.Action.TURN_RIGHT
        self.queue.extend([direction for _ in range(abs(delta))])
        self.queue.append(Agent.Action.FORWARD)

    #THIS IS OUR SEARCH ALGORITHM it makes us visit as many places as possible
    
    def safeSearch(self):
        #uses self.danger to search the next optimial move  
        #simple model, find the direction that is the highest values actual move
        best_move = -100
        best_dir = 1
        for d,(x,y) in enumerate([(0,1),(1,0),(0,-1),(-1,0)]):
            new_x = self.x +x
            new_y = self.y +y
            if(new_x < 0 or new_x > self.width):
                continue
            if(new_y < 0 or new_y > self.height):
              continue
            if(self.board[new_y][new_x] > best_move):# and self.board[new_y][new_x] != 1 ):
                best_dir = d
                best_move = self.board[new_y][new_x]
            print("Choice %d:"%d,self.board[new_y][new_x])
        
        print("we chose %d"%best_dir)
        self.moveDirection(best_dir)
        


    def SnakeMovement(self,bump):
        if(bump):
            if(self.direction == 1):
                self.moveDirection(self.direction-1)
                self.queue.append(Agent.Action.TURN_LEFT)
            if(self.direction == 3):
                self.moveDirection(self.direction+1)
                self.queue.append(Agent.Action.TURN_RIGHT)
        else:
            self.moveDirection(self.direction)

    #ALLOWS the game to be broken up into bigger actions than the actuators

    def follow_queue(self):
        action = self.queue.pop(0)
        self.last_action= action
        if(action == Agent.Action.FORWARD):
            self.updatePosition()
        if(action == Agent.Action.TURN_LEFT):
            self.direction = (self.direction-1)%4
        if(action == Agent.Action.TURN_RIGHT):
            self.direction = (self.direction+1)%4
        return action
        
    
    #END OF GAME MOVE BACK TO THE START AND CLIMB OUT
        
    def return_to_exit(self):    
        #for every item in the trail reverse it and add it to the queue
        for i in self.trail[::-1]:
            self.moveDirection((i+2)%2)

        

        
    
    
    # ======================================================================
    # YOUR CODE ENDS
    # ======================================================================
