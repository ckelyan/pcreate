import os
import json
import curses
import numpy as np
from curses import wrapper

ABS_PATH = os.path.abspath(__file__)[:-7]

class Preset:
    def __init__(self, name, size):
        self.name = name
        self.mat = np.zeros((size, size), dtype=int)
        
    def update(self, posx, posy):
        newmat = self.mat.copy()
        newmat[posx, posy] = 1 if self.mat[posx, posy] == 0 else 0
        self.mat = newmat
        
    def saveMat(self, name=None):
        with open(ABS_PATH+"/savedpresets.json", "r+") as f:
            newdata = json.load(f)
            
            mat = self.mat.copy().T.tolist()
            newdata[self.name if not name else name] = mat
            
            f.seek(0)
            json.dump(newdata, f)
            f.truncate()
                
def logPos(stdscr, size, posx, posy):
    aposx = int(posx/2)
    stdscr.addstr(size+1, 0, str(f"{aposx:03d}") + " (" + str(f"{posx:03d}") + ")" + " | " + str(f"{posy:03d}"))

def main(stdscr, name="DEFAULT_PRESET_NAME", size=20):
    p = Preset(name, size)
    
    posx, posy = 0, 0
    stdscr.clear()
    
    while True:
        aposx = int(posx / 2)
        curclr = curses.COLOR_WHITE
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
        
        if p.mat[aposx, posy] == 1:
            curclr = curses.color_pair(2)
        else:
            curclr = curses.color_pair(1)
        
        view = "\n".join("".join("  " if p.mat[xi, yi] == 0 else "██" for xi in range(0, size)) for yi in range(size))
        stdscr.addstr(0, 0, view)    
        
        stdscr.addstr(posy, posx, "██", curclr)
        stdscr.refresh()
        key = stdscr.getch()
        stdscr.addstr(size, 0, f"{key:03d}")
            
        if 258 <= key <= 261:
            stdscr.addstr(posy, posx, "  ")
        
        if key == 259 and posy > 0: # UP
            posy -= 1
            logPos(stdscr, size, posx, posy)
            
        elif key == 258 and posy < size-1: # DOWN
            posy += 1
            logPos(stdscr, size, posx, posy)
            
        elif key == 261 and posx < size*2-2: # RIGHT
            posx += 2
            logPos(stdscr, size, posx, posy)
            
        elif key == 260 and posx > 0: # LEFT
            posx -= 2
            logPos(stdscr, size, posx, posy)
                
        elif key == 10 or key == 60:
            p.update(aposx, posy)
            
        elif key == 58:
            nextch = stdscr.getkey()
            if nextch == "q":
                final = ""
                while True:
                    stdscr.addstr(size, 0, f"Name: {final}")
                    nextch = stdscr.getch()
                    stdscr.refresh()
                    
                    if 97 <= nextch <= 122:
                        final += chr(nextch)
                    elif nextch == 10:
                        break
                        
                        
                break
            
    p.saveMat(final)

wrapper(main, size=40)