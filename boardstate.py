import random
import time

#print out the state of a board for debugging

def print_board(board):
    if board != None:
        for i in range(4):
            row = board[i * 4:i * 4 + 4]
            for cell in row:
                if cell == None:
                    print ' -- ',
                elif cell < 10:
                    print '  ' + str(cell) + ' ',
                elif cell < 100:
                    print ' ' + str(cell) + ' ',
                elif cell < 1000:
                    print ' ' + str(cell),
                else:
                    print cell,
            print
        print

#get all possible next board states that the game might generate after taking a move

def get_next_boardstates(board):
    next_states = list()

    for i in range(16):
        if board[i] == None:
            new_state = board[:i] + [2] + board[i+1:]
            next_states.append(new_state)
            new_state = board[:i] + [4] + board[i+1:]
            next_states.append(new_state)

    return next_states

#generate a random board starting state
#only used for simulations for testing purposes

def make_random_start_state():
    return  random.choice(get_next_boardstates(random.choice(get_next_boardstates([None] * 16))))

#predict what the board will look like in response to a move

#the slide commands are the most time-sensitive part of the code.
#these routines account for about half of the predictive solver algorithm
#so have been carefully tweaked for speed.

#we perform the sliding 4 cells at a time, with dedicated routines for
#sliding to the left and sliding to the right.

def slide_row_left(row0,row1,row2,row3):
    if row0 is None:
        if row1 is None:
            if row2 is None:
                return [row3,None,None,None]
            elif row2 == row3:
                return [row2 + row3,None,None,None]
            else:
                return [row2,row3,None,None]
        else:
            if row2 is None:
                if row3 == row1:
                    return [row1 + row3,None,None,None]
                else:
                    return [row1,row3,None,None]
            else:
                if row2 == row1:
                    return [row1 + row2,row3,None,None]
                elif row2 == row3:
                    return [row1,row2 + row3,None,None]
                else:
                    return [row1,row2,row3,None]
    elif row1 is None:
        if row2 is None:
            if row0 == row3:
                return [row0 + row3,None,None,None]
            else:
                return [row0,row3,None,None]
        elif row0 == row2:
            return [row0 + row2,row3,None,None]
        elif row2 == row3:
            return [row0,row2 + row3,None,None]
        else:
            return [row0,row2,row3,None]
    elif row2 is None:
        if row0 == row1:
            return [row0 + row1,row3,None,None]
        elif row1 == row3:
            return [row0,row1 + row3,None,None]
        else:
            return [row0,row1,row3,None]
    elif row0 == row1:
        if row2 == row3:
            return [row0 + row1,row2 + row3,None,None]
        else:
            return [row0 + row1,row2,row3,None]
    elif row1 == row2:
        return [row0,row1 + row2,row3,None]
    elif row2 == row3:
        return [row0,row1,row2 + row3,None]
    else:
        return [row0,row1,row2,row3]

def slide_row_right(row0,row1,row2,row3):
    if row3 is None:
        if row2 is None:
            if row1 is None:
                return [None,None,None,row0]
            elif row1 == row0:
                return [None,None,None,row1 + row0]
            else:
                return [None,None,row0,row1]
        else:
            if row1 is None:
                if row0 == row2:
                    return [None,None,None,row2 + row0]
                else:
                    return [None,None,row0,row2]
            else:
                if row1 == row2:
                    return [None,None,row0,row2 + row1]
                elif row1 == row0:
                    return [None,None,row1 + row0,row2]
                else:
                    return [None,row0,row1,row2]
    elif row2 is None:
        if row1 is None:
            if row3 == row0:
                return [None,None,None,row3 + row0]
            else:
                return [None,None,row0,row3]
        elif row3 == row1:
            return [None,None,row0,row3 + row1]
        elif row1 == row0:
            return [None,None,row1 + row0,row3]
        else:
            return [None,row0,row1,row3]
    elif row1 is None:
        if row3 == row2:
            return [None,None,row0,row3 + row2]
        elif row2 == row0:
            return [None,None,row2 + row0,row3]
        else:
            return [None,row0,row2,row3]
    elif row3 == row2:
        if row1 == row0:
            return [None,None,row1 + row0,row3 + row2]
        else:
            return [None,row0,row1,row3 + row2]
    elif row2 == row1:
        return [None,row0,row2 + row1,row3]
    elif row1 == row0:
        return [None,row1 + row0,row2,row3]
    else:
        return [row0,row1,row2,row3]

def slide_left(board):

    return slide_row_left(board[0],board[1],board[2],board[3]) + \
           slide_row_left(board[4],board[5],board[6],board[7]) + \
           slide_row_left(board[8],board[9],board[10],board[11]) + \
           slide_row_left(board[12],board[13],board[14],board[15])

def slide_right(board):

    return slide_row_right(board[0],board[1],board[2],board[3]) + \
           slide_row_right(board[4],board[5],board[6],board[7]) + \
           slide_row_right(board[8],board[9],board[10],board[11]) + \
           slide_row_right(board[12],board[13],board[14],board[15])

#slide up and slide down are slightly less efficient because the values need
#to be unpacked and repacked in a slightly more complex way.
#but we can at least reuse the slide left and slide right code.

def slide_up(board):

    new_row0 = slide_row_left(board[0],board[4],board[8],board[12])
    new_row1 = slide_row_left(board[1],board[5],board[9],board[13])
    new_row2 = slide_row_left(board[2],board[6],board[10],board[14])
    new_row3 = slide_row_left(board[3],board[7],board[11],board[15])
    
    return [new_row0[0],new_row1[0],new_row2[0],new_row3[0],
            new_row0[1],new_row1[1],new_row2[1],new_row3[1],
            new_row0[2],new_row1[2],new_row2[2],new_row3[2],
            new_row0[3],new_row1[3],new_row2[3],new_row3[3]]

    
def slide_down(board):

    new_row0 = slide_row_right(board[0],board[4],board[8],board[12])
    new_row1 = slide_row_right(board[1],board[5],board[9],board[13])
    new_row2 = slide_row_right(board[2],board[6],board[10],board[14])
    new_row3 = slide_row_right(board[3],board[7],board[11],board[15])
    
    return [new_row0[0],new_row1[0],new_row2[0],new_row3[0],
            new_row0[1],new_row1[1],new_row2[1],new_row3[1],
            new_row0[2],new_row1[2],new_row2[2],new_row3[2],
            new_row0[3],new_row1[3],new_row2[3],new_row3[3]]
