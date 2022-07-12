import sys
import json
import curses
import numpy as np
from typing import Union, Type, Tuple, List

# constants
FILENAME = 'patterns.json'
PAT_NAME = sys.argv[1] if len(sys.argv) > 1 else 'default'
PAT_FORMAT = sys.argv[2] if len(sys.argv) > 2 else 'ai'
TOGGLE_MAP = {
    1: 0,
    0: 1,
    True: False,
    False: True
}
KEY_MOVEMENT_MAP = {
    259: (0, -1),
    258: (0, 1),
    260: (-1, 0),
    261: (1, 0)
}

def tryinput(*args, **kwargs):
    try:
        return input(*args, **kwargs)
    except KeyboardInterrupt:
        exit()

if len(sys.argv) <= 2: print('Warning: no name specified. Correct usage:\n   python main.py <pattern-name>\n')
# get size
size = list(map(int, tryinput('Size of the pattern (w,h): ').split(',')))

# function to parse lines into a given mode
def lineParser(l, format_):
    if format_ == 'as':
        return [str(n) for n in l]
    if format_ == 's':
        return ''.join(str(n) for n in l)
    if format_ == 'i':
        return int(''.join(str(n) for n in l), 2)

# mother class, holds the preset name and the matrix
class Preset:
    def __init__(self, name: str, size: Union[Tuple, List, int], mode: type = int):
        if type(size) == int:
            size = (size, size)

        # mode can be int or bool since matrix is binary
        if mode not in [int, bool]:
            raise ValueError('mode must be int or bool')
        
        self.name = name
        # initialize empty matrix
        self.mat = np.zeros(size, dtype=mode)
        
    # function to toggle a bit at given pos
    def toggleAt(self, x: int, y: int):
        self.mat[x, y] = TOGGLE_MAP[self.mat[x, y]]
        
    def isSet(self, x: int, y: int):
        return bool(self.mat[x, y])
        
    # function to convert the matrix to a string
    def toStr(self, charOn='██', charOff='  '):
        return '\n'.join(''.join(charOn if self.mat[xi, yi] else charOff for xi in range(0, self.mat.shape[0])) for yi in range(self.mat.shape[1]))
        
    # function to save the pattern in a JSON format to a file
    def saveMat(self, filename=FILENAME, format_='ai'):
        # formats:
        # ai - array of ints     ex. [0, 1, 1, 0] (default)
        # as - array of strings  ex. ['1', '1', '0', '0']
        # s  - single string     ex. '1111'
        # i  - decimal int       ex. 5
        
        if not np.any(self.mat):
            emptyMatWarning = tryinput('Warning: the pattern is empty. Do you wish to save it anyway? (y/N) ')
            if emptyMatWarning in ['n', 'no', '']:
                exit()
        
        with open(filename, 'r') as f:
            data = json.load(f)
            
        # if a pattern with the same name has already been saved in the file
        if self.name in data.keys():
            # n or no or blank: ask for new name
            # anything else: abort
            warningInput = tryinput(f'Warning: a pattern with the name \'{self.name}\' has already been saved in {filename}. Abort? (y/N) ').lower()
            
            if warningInput in ['n', 'no', '']:
                newName = tryinput('New name (leave blank to overwrite): ')
                
                if newName: self.name = newName
        
            else:
                exit()

        # parse the matrix
        parsed_mat = self.mat.T.tolist()
        if format_ != 'ai':
            # parse line per line
            parsed_mat = [lineParser(l, format_) for l in self.mat.T]
        
        data[self.name] = parsed_mat
        
        with open(filename, 'w') as f:
            json.dump(data, f)
        
        print(f'Successfully wrote new pattern \'{self.name}\' to {filename}.')

# holds the cursor position on the matrix as well as its state (color)
# also serves as a general input handler
class Cursor:
    def __init__(self, preset: Preset, boundaries: Union[Tuple, List], pos: list = [0, 0]):
        self.preset = preset
        # cursor boundaries
        # format: (xmin, xmax, ymin, ymax)
        self.boundaries = boundaries
        self.pos = pos
        self.color = curses.COLOR_RED
        
    # function to handle the key presses
    def update(self, key):
        # if the key is a movement key, update the cursor position
        if key in KEY_MOVEMENT_MAP.keys():
            self.pos[0] = min(max(KEY_MOVEMENT_MAP[key][1] + self.pos[0], self.boundaries[0]), self.boundaries[1] - 1)
            self.pos[1] = min(max(KEY_MOVEMENT_MAP[key][0] + self.pos[1], self.boundaries[2]), self.boundaries[3] - 1)
            # the position has changed, this tells the program to redraw the cursor
            return True
        
        # space key
        elif key == 32:
            self.preset.toggleAt(*self.pos[::-1])
        
        return False

pre = Preset(PAT_NAME, size)
cur = Cursor(preset=pre, boundaries=(0, size[0], 0, size[1]))

def main(stdscr):
    n_length = (len(str(size[0])), len(str(size[1])))
    
    stdscr.clear()
    
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
    
    # placeholders for debug infos
    stdscr.addstr(cur.pos[0], cur.pos[1] * 2, '██', cur.color)
    stdscr.addstr(size[0] + 1, 0, f'000 ')
    stdscr.addstr(size[0] + 2, 0, f'[{"0".zfill(n_length[0])}, {"0".zfill(n_length[1])}]')
    
    while True:
        # get key press
        key = stdscr.getch()
        # draw the matrix
        stdscr.addstr(0, 0, pre.toStr())
        
        # enter or escape to exit
        if key == 10 or key == 60:
            break
        
        # let cursor handle the key press
        cur.update(key)
        
        # if the pixel the cursor is on is set, change the cursor color to magenta
        # else turn it red
        if pre.isSet(*cur.pos[::-1]):
            cur.color = curses.color_pair(2)
        else:
            cur.color = curses.color_pair(1)
        
        # cursor
        stdscr.addstr(cur.pos[0], cur.pos[1] * 2, '██', cur.color)
        
        # debug
        # key pressed
        stdscr.addstr(size[0] + 1, 0, f'{str(key)} ')
        # cursor position
        stdscr.addstr(size[0] + 2, 0, f'[{str(cur.pos[0]).zfill(n_length[0])}, {str(cur.pos[1]).zfill(n_length[1])}]')
        
        stdscr.refresh()
        
curses.wrapper(main)

pre.saveMat(format_=PAT_FORMAT)