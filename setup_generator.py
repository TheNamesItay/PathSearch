from numpy import random
from main import run

LSP = 1
SNAKE = 2
GAME_TYPE = LSP

BLOCKS_FRAC = 0.7

CHANGE_SETUP = True
GENERATE_BLOCKS = False
SETUP_MODE = True

PATH = (0, 1, 2, 3, 13, 23, 24, 25, 14, 15, 26, 27, 28, 39, 38, 46, 56, 57, 69, 82, 93, 92, 91, 80, 67, 66, 79, 78, 77, 76, 88, 87, 86, 74, 75, 63, 51, 52, 53, 45, 34, 35)

OUTPUT_FILE = "setup.txt"

GRID_W = 0
GRID_H = 0

BLOCKS = []

BLOCK_X = 0
BLOCK_Y = 1

GRID = []
EDGES = []

N = 0


def parseBlock(row):
    global BLOCKS
    parts = row.split()
    cords = []
    if len(parts) > 1:
        for cord in parts[1].split(','):
            cords += [int(cord)]
    if len(cords) == 2:
        BLOCKS += [cords]


def parseHeight(row):
    global GRID_H
    parts = row.split()
    if len(parts) == 2:
        GRID_H = int(parts[1])


def parseWidth(row):
    global GRID_W
    parts = row.split()
    if len(parts) == 2:
        GRID_W = int(parts[1])


def is_block(x, y):
    for b in BLOCKS:
        if b[BLOCK_X] == x and b[BLOCK_Y] == y:
            return True
    return False


def get_node_name(s):
    for x in range(GRID_W):
        for y in range(GRID_H):
            if GRID[y][x] == s:
                return "(" + str(x) + ", " + str(y) + ")"
    return "-1"


with open('options.txt', 'r') as fp:
    if CHANGE_SETUP:
        for line in fp:
            if len(line) == 1:
                continue
            if line[1] == 'B':
                parseBlock(line)
            if line[1] == 'H':
                parseHeight(line)
            if line[1] == 'W':
                parseWidth(line)

    if CHANGE_SETUP and GENERATE_BLOCKS:
        block_num = random.randint(GRID_H * GRID_W * BLOCKS_FRAC)
        block_xs = random.randint(GRID_W, size=block_num)
        block_ys = random.randint(GRID_H, size=block_num)
        BLOCKS = set(zip(block_xs, block_ys))
        for i in range(block_num):
            print("#B " + str(block_xs[i]) + "," + str(block_ys[i]))

    # set up grid
    counter = 0
    for y in range(GRID_H):
        row = []
        for x in range(GRID_W):
            if is_block(x, y):
                row += [-1]
            else:
                row += [counter]
                counter += 1
        GRID += [row]
    N = counter - 1

    # set up edges
    for y in range(GRID_H):
        for x in range(GRID_W):
            if not is_block(x, y):
                if (x+1) < GRID_W and not is_block(x+1, y):
                    EDGES += [[(x, y), (x+1, y)]]
                if (y+1) < GRID_H and not is_block(x, y+1):
                    EDGES += [[(x, y), (x, y+1)]]

    # to file.txt
    print_out = ""

    if SETUP_MODE:
        nodes_setup = ""
        for i in range(N+1):
            if GAME_TYPE == LSP:
                nodes_setup += "#V" + str(i) + " C" + str(i) + " \n"
        print_out += nodes_setup

        edges_setup = ""
        for edge in EDGES:
            x1 = edge[0][0]
            x2 = edge[1][0]
            y1 = edge[0][1]
            y2 = edge[1][1]
            node1 = GRID[y1][x1]
            node2 = GRID[y2][x2]
            edges_setup += "#E " + str(node1) + " " + str(node2) + " \n"
        print_out += edges_setup
    else:
        for node in PATH:
            name = get_node_name(node)
            print_out += name + "  "
        print_out += "\nPATH LENGTH: " + str(len(PATH))
    if CHANGE_SETUP:
        with open(OUTPUT_FILE, 'w+') as output_file:
            output_file.write(print_out)
            output_file.close()
    # print empty grid
    for y in range(GRID_H):
        row = ""
        for x in range(GRID_W):
            if is_block(x, y):
                row += "#\t"
            else:
                row += "-\t"
        print(row)

    PATH = run()
    print("path length: " + str(len(PATH)))

    # print grid
    for y in range(GRID_H):
        row = ""
        for x in range(GRID_W):
            if GRID[y][x] in PATH:
                row += str(PATH.index(GRID[y][x])) + "\t"
            elif is_block(x, y):
                row += "#\t"
            else:
                row += "-\t"
        print(row)

    print('successfully created ', OUTPUT_FILE)







