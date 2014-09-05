import win32ui,win32con
import sys, os, time

cell_colors = dict()

cell_colors[11846093] = None
cell_colors[14345454] = 2
cell_colors[13164781] = 4
cell_colors[7975410] = 8
cell_colors[6526453] = 16
cell_colors[6257910] = 32
cell_colors[3890934] = 64
cell_colors[7524333] = 128
cell_colors[6409453] = 256
cell_colors[5294317] = 512
cell_colors[4179437] = 1024
cell_colors[3064557] = 2048
cell_colors[3291708] = 4096 #yes, numbers greater than 2048 exist.  This is the highest I've ever seen.

def get_board_dimensions(dc):

    #find where the game grid is on the window

    #This is done by looking for a square dark area surrounded by lighter areas.
    #We don't do exact color matching here as the glow effects on high-scoring tiles
    #throw that off too easily.  Instead, we add together the R,G,B components and see
    #if they are greater than 700.

    #first, get the actual size of the window

    size = dc.GetClipBox()

    h = size[3]
    w = size[2]

    #scan in from the middle of the left side till we see a dark area

    x = 25 #skip over the left border
    y = h / 2

    color = dc.GetPixel(x,y)

    while (color>>16)%256+(color>>8)%256+(color)%256 > 700 and x < w:
        x = x + 1
        color = dc.GetPixel(x,y)

    xmin = x-1 #left edge found

    #do the same from the middle of the right side

    x = w - 50 #skip the right border and scroll bar

    color = dc.GetPixel(x,y)

    while (color>>16)%256+(color>>8)%256+(color)%256 > 700 and x > 0:
        x = x - 1
        color = dc.GetPixel(x,y)

    xmax = x+1 #right edge found

    x = (xmin + xmax) / 2 #now we start in the middle of the board horizontally and scan up and down

    color = dc.GetPixel(x,y)

    while (color>>16)%256+(color>>8)%256+(color)%256 < 700 and y < h:
        y = y + 1
        color = dc.GetPixel(x,y)

    ymax = y #found the bottom edge

    y = h / 2

    color = dc.GetPixel(x,y)

    while (color>>16)%256+(color>>8)%256+(color)%256 < 700 and y > 0:
        y = y - 1
        color = dc.GetPixel(x,y)

    ymin = y #found the top edge

    board_size = [xmin,ymin,xmax,ymax]

    return board_size

def get_board_contents(dc):
    
    failed = True

    fails = 0

    while failed:
        failed = False

        #get the board dimensions

        #we do this every time we call this code in case the window has been moved or resized
        #between turns
        
        size = get_board_dimensions(dc)
        
        board = list()

        #get the board contents

        #every number has a different background color, so instead of the more difficult
        #task of text recognition we merely have to sample a pixel in each cell and
        #look up what number that pixel corresponds to.

        #This is complicated by the fact that high-scoring numbers have glow effects applied
        #which bleed over into adjacent cells, and the number in the cell seems to vary in
        #position from computer to computer.  To make sure we actually get the cell contents
        #correctly we sample four different points inside the cell and check to see if any
        #of them match a known color.

        #We also re-sample several times in case of a failure, in case we sampled too quickly
        #and the board was still updating

        for j in range(4):
            for i in range(4):
                x = size[0] + int(((size[2] - size[0]) * 0.25) * (i + 0.5)) #horizontal center
                y = size[1] + int(((size[3] - size[1]) * 0.25) * (j + 0.25)) #above vertical center to miss number in cell
                #print i,j,x,y,dc.GetPixel(x,y)
                color = dc.GetPixel(x,y)

                if cell_colors.has_key(color):
                    board.append(cell_colors[color])
                else:
                    y = size[1] + int(((size[3] - size[1]) * 0.25) * (j + 0.3)) #above vertical center to miss number in cell
                    #print i,j,x,y,dc.GetPixel(x,y)
                    color = dc.GetPixel(x,y)

                    if cell_colors.has_key(color):
                        board.append(cell_colors[color])
                    else:
                        y = size[1] + int(((size[3] - size[1]) * 0.25) * (j + 0.7)) #below vertical center to miss number in cell
                        #print i,j,x,y,dc.GetPixel(x,y)
                        color = dc.GetPixel(x,y)

                        if cell_colors.has_key(color):
                            board.append(cell_colors[color])
                        else:
                            y = size[1] + int(((size[3] - size[1]) * 0.25) * (j + 0.75)) #below vertical center to miss number in cell
                            #print i,j,x,y,dc.GetPixel(x,y)
                            color = dc.GetPixel(x,y)

                            if cell_colors.has_key(color):
                                board.append(cell_colors[color])
                            else:
                                if fails > 2:
                                    print 'Unknown color',color,'in cell',i,j
                                board.append(None)
                                failed = True
        if failed:
            fails = fails + 1
        else:
            fails = 0

        if fails > 3: #give up.  This should never trigger.
            #failed = False
            return None
                
    return board
