from boardstate import *
from guiget import *
import random
import time

#This code was specifically developed using the 2048 game
#at http://gabrielecirulli.github.io/2048/ running on Mozilla Firefox.
#It has been tested on a few different version of Windows.  Depending on the
#version of windows, it may or may not require the window running 2048
#to be in the foreground.

#the window running 2048 must have the entire 4x4 game board on the screen,
#preferably centered, but does not need to take up the entire screen,
#and the score and new game buttons don't need to be visible.
#You can start this code with the game board in any state, it doesn't
#need to start with a new game.  It will however crash out and exit from the
#script if you lose or win the game.

#This code does require the win32 python libraries to be installed, in
#addition to python 2.7

def solve_recursive(board,cycles):

#recursively find the best move to take given the state of the board
#cycle is the number of iterations to run for.

    #examine all possible moves I might take

    possible_next_states = [(slide_down(board),'DOWN'),
                            (slide_up(board),'UP'),
                            (slide_right(board),'RIGHT'),
                            (slide_left(board),'LEFT')]

    best_score = 0.0
    best_moves = list()

    for state,move in possible_next_states:
        if state != board: #moves which did not change the board state are not allowed
            aggregate_score = 0.0

            free = state.count(None) #count number of open cells remaining

            #open cells remaining is our only metric of success.  This code does
            #not care about arrangement of cells, points scored, or highest number
            #on the board.  Open cells alone is enough to do well at this game

            if cycles > 0 and free > 0: #iterations left and cells open?
                #get a list of all states that the board might be in after our move
                
                possible_next_states = get_next_boardstates(state)

                #note that if there are no open cells, this list will be empty.

                n = len(possible_next_states)

                if n > 0: #game can continue?
                    for next_state in possible_next_states:

                        #get score and best move for each following state
                        
                        score,best = solve_recursive(next_state,cycles-1)
                        aggregate_score = aggregate_score + score
                            
                    aggregate_score = aggregate_score / n

            else: #out of iterations, or no cells free.  Return this board state's score
                aggregate_score = free

            #make a list of the highest-scoring moves

            if aggregate_score >= best_score:
                if best_score != aggregate_score:
                    best_moves = [move]
                    best_score = aggregate_score
                else:
                    best_moves.append(move)

    if len(best_moves) == 0: #no moves remaining, game is over at this state
        return 0.0,None

    else:
        #pick a random move from our highest-scoring choices.
        
        return best_score,random.choice(best_moves)
    
#find the window running 2048 by name

#note that this only works in Firefox at the moment, if you are using a different browser
#you can probably get it to work by changing the name this looks for

window = win32ui.FindWindow(None, '2048 - Mozilla Firefox')
dc = window.GetWindowDC()

done = False

while not done:

    #get the contents of the board
    
    board = get_board_contents(dc)

    free = board.count(None)
    
    print_board(board)

    solve_start_time = time.time()

    #vary the number of iterations allowed based on the number of free cells.

    if (free < 2):
        depth = 5
    elif (free < 4):
        depth = 4
    elif (free < 10):
        depth = 3
    else:
        depth = 2

    print free,'free cells, solving with recursion depth =',depth

    #run a recursive predictor to determine the best move

    score,best = solve_recursive(board,depth)

    print 'best move',best,'score',score,'ran for',time.time() - solve_start_time,'seconds'

    print

    #convert the best move to a windows key command

    if (best == 'DOWN'):
        move = win32con.VK_DOWN
    elif (best == 'UP'):
        move = win32con.VK_UP
    elif (best == 'RIGHT'):
        move = win32con.VK_RIGHT
    elif (best == 'LEFT'):
        move = win32con.VK_LEFT
    else:
        done = True

    #and send it to the window

    if not done:
        window.PostMessage(win32con.WM_KEYDOWN, move, 0)
        time.sleep(0.1)
        window.PostMessage(win32con.WM_KEYUP, move, 0)
        time.sleep(0.5)
