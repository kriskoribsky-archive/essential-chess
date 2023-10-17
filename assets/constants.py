# function for blending RGB colors (takes dictionary containing RGB colors with their combining ratios respectively as an argument)
def combine_rgb(rgb_data_dict):
    colors = list(rgb_data_dict.items())
    total_ratio = sum(rgb_data_dict.values())

    red, green, blue = 0, 0, 0

    for color, ratio in colors:
        red += color[0]*ratio
        green += color[1]*ratio
        blue += color[2]*ratio

    return (int(red/total_ratio), int(green/total_ratio), int(blue/total_ratio))

# screen parameters
SCREEN_MULTIPLIER = 2/3
FPS = 144

# board parameters
COLS = ROWS = 8
PIECE_SIZE = 0.8 # size of a chess piece relative to the size of the tile
PLAY_TIME = 10 # in minutes

# colors
WHITE_CLR = (255, 255, 255)
BLACK_CLR = (0, 0, 0)
GREY_CLR = (50, 50, 50, 200)
BROWN_CLR = (143, 85, 23)
LIGHT_GREY_CLR = (150, 150, 150)
TRANSPARENT_CLR = (0, 0, 0, 0)

LIGHT_SQUARE_CLR = (191, 154, 109) # light square color
DARK_SQUARE_CLR = (125, 79, 24) # dark square color

SELECTION_CLR = (173, 171, 35, 150) # square hightlight color

TARGET_SQUARE_CLR = (255, 255, 255, 200) # drag and drop square border

AVAILABLE_MOVES_CLR = (60, 122, 61, 150) # squares for available moves (with aplha transparency)

SELECTED_SQUARE_CLR = (*AVAILABLE_MOVES_CLR[:3:1], 100) # square for selected piece (same color as available moves but with lesser transparency)

CHECK_COLOR = (186, 39, 64, 150) # color of square while king is in check

# pygame mouse button IDs
LEFT_MOUSE = 1
MIDDLE_MOUSE = 2
RIGHT_MOUSE = 3

# FEN strings
START_POS = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
POS_1 = "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"
POS_2 = "rn2kbr1/2Bp1p1p/bp4p1/3Pn3/8/2N1qN2/PPP1Q2P/R3K2R w KQq - 0 14"
POS_3 = "r4b1R/p2k1b2/Pp1P4/PNpP1P2/8/8/5P1P/2K5 w - - 2 36"
POS_4 = "4k2r/r4p2/p7/2p1n3/Pp3ppp/1P6/3p4/b5K1 b k - 3 41"
POS_5 = "4k3/2p5/8/8/8/3N1R2/7P/4K3 w - - 0 1"
CUSTOM_POS = "r2q4/p2k1p2/b3n2p/1p1N4/P4PQ1/8/4K2P/1R1R4 b - - 0 1"
EN_PASSANT_POS = "rnbqkbnr/pp4pp/8/3PP3/2pP4/5Bp1/PP2P2P/RNBQK1NR b KQkq d3 0 8"
