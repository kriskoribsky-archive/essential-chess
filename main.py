import sys
import os
import math
import pygame
import time
import string
from collections import Counter
# import threading --> WIP promotion menu dynamic highlight

# tkinter is used as temporary GUI while showing draw options/checkmate
import tkinter as tk
from tkinter import messagebox



# from assets.constants import *
from assets.constants import (SCREEN_MULTIPLIER, FPS, COLS, ROWS, 
                            WHITE_CLR, BLACK_CLR, GREY_CLR, LIGHT_GREY_CLR, TRANSPARENT_CLR, BROWN_CLR,
                            LIGHT_SQUARE_CLR, DARK_SQUARE_CLR, SELECTION_CLR, TARGET_SQUARE_CLR, AVAILABLE_MOVES_CLR, SELECTED_SQUARE_CLR,
                            PIECE_SIZE,
                            LEFT_MOUSE, MIDDLE_MOUSE, RIGHT_MOUSE,
                            START_POS, POS_1, POS_2, POS_3, POS_4, POS_5, CUSTOM_POS, EN_PASSANT_POS)

# from assets.images import *
from assets.images import (BOARD_BG, NOTATION_SYSTEM, CHECK_BACKGROUND,
                        WHITE_KING, WHITE_QUEEN, WHITE_BISHOP, WHITE_KNIGHT, WHITE_ROOK, WHITE_PAWN,
                        BLACK_KING, BLACK_QUEEN, BLACK_BISHOP, BLACK_KNIGHT, BLACK_ROOK, BLACK_PAWN)

# from assets.sounds import *
from assets.sounds import (MOVE_SOUND, CAPTURE_SOUND, CASTLE_SOUND, MATCH_END_SOUND)





















class GameWindow:
    def __init__(self):
        # initialize all pygame modules
        pygame.init()

        pygame.display.set_icon(pygame.image.load("assets/resources/icons/icon.png"))
        pygame.display.set_caption("Essential Chess [Aplha release 1.9.2021 by: NotRareOne]")

        # user's display video mode
        user_screen = pygame.display.Info()

        self.width = int(user_screen.current_w*SCREEN_MULTIPLIER)
        self.height = int(user_screen.current_h*SCREEN_MULTIPLIER)

        

    def run(self):
        # time monitoring (FPS)
        self.clock = pygame.time.Clock()

        # create new board (white is default side)
        self.chess_board = ChessBoard(COLS, ROWS, "white")

        # render screen
        self.initialize_screen(self.width, self.height)

        # load initial position from FEN string
        self.chess_board.load_fen(START_POS)

        # generate new moves for side to move
        self.chess_board.generate_moves(self.chess_board.active_color, self.chess_board.default_side, self.chess_board.board_repr)

        # create playing board
        self.initialize_board()
        
        # recent moves for square highlight
        self.recent_moves = []

        # FEN board positions for threefold repetition detection
        self.positions = [" ".join(START_POS.rstrip().split()[:4])]

        run = True
        while run:
            self.clock.tick(FPS)
            self.update_fps(self.clock.get_fps())

            selected_piece = None
        
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE:

                    self.initialize_screen(event.w, event.h, startup=False)
                    self.update_board()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT_MOUSE:
                    x, y = self.get_mouse_pos()
                    selected_piece = self.select_piece(x, y)
                
                # to prevent issue explained in description.txt (issues in making)
                elif event.type == pygame.WINDOWFOCUSGAINED:
                    pygame.display.flip()

            self.hover_cursor(self.get_mouse_pos())

            if selected_piece:
                self.handle_movement(selected_piece)
    


    # called when resizing screen and on startup
    def initialize_screen(self, width, height, startup=True):

        # create function local var with existing Chessboard object
        board = self.chess_board

        def initialize_coords(self):
            coord_width = board.col_coords[0].get_width()
            coord_height = board.row_coords[0].get_height()

            # edges of the playing board
            initial_x = board.board_rect.x 
            initial_y = board.board_rect.y 

            # reverse the order of the coordinates if default side is black
            if board.default_side == "black":
                board.col_coords = board.col_coords[::-1]
                board.row_coords = board.row_coords[::-1]

            # coords representing columns (a-h), calculations for centering the coords
            for i in range(COLS):
                x = initial_x + (i+1)*self.tile_width - self.tile_width//2 - coord_width//2
                y = initial_y + board.board_rect.height + self.tile_height//8

                self.screen.blit(board.col_coords[i], (x, y))
            
            # coords representing rows (1-8), calculations for centering the coords
            for i in range(ROWS):
                x = initial_x - self.tile_width//8 - coord_width
                y = initial_y + (i+1)*self.tile_height - self.tile_height//2 - coord_height//2

                self.screen.blit(board.row_coords[i], (x, y))



        self.screen = pygame.display.set_mode(size=(width, height), flags=pygame.RESIZABLE)
        board.render_elements()

        # assign tile sizes for this object also for later use
        self.tile_width = board.tile_width
        self.tile_height = board.tile_height

        self.board_width = board.board_rect.width
        self.board_height = board.board_rect.height

        # background
        self.screen.blit(board.background, (0, 0))

        # game notation system picture
        # self.screen.blit(board.game_notation, (self.tile_width//8, self.tile_height//8))

        # coordinates
        initialize_coords(self)

        if startup == False:
            # update piece sizes with the new tile size after resize
            for row in board.board_repr:
                for piece in row:
                    if isinstance(piece, Piece):
                        piece.rect = piece.create_rect(board.tile_width, board.tile_height)
                        piece.image = piece.create_image(board.tile_width, board.tile_height)


        # update the whole screen
        pygame.display.flip()
        
        # if startup == False:
        #     print("updating screen")
        # else:
        #     print("initializing screen")



    # called only on startup
    def initialize_board(self):
        # create function local var with existing Chessboard object
        board = self.chess_board

        # tiles
        board.board_surface.blit(board.tile_surface, (0, 0))

        # pieces
        board.blit_pieces(board.board_surface, board.board_repr)

        # playing board
        self.screen.blit(board.board_surface, board.board_rect)

        # update only the playing board part of the display
        pygame.display.update(board.board_rect)

        # print("initializing board")


    # called when resizing, by another methods (e.g. handle movement)
    def update_board(self):
        # create function local var with existing Chessboard object                 
        board = self.chess_board

        # tiles
        board.board_surface.blit(board.tile_surface, (0, 0))

        # previous move highlight square
        for square in self.recent_moves:
            board.board_surface.blit(board.highlight_square, (square[1]*self.tile_width, square[0]*self.tile_height))

        # pieces
        board.blit_pieces(board.board_surface, board.board_repr)

        # playing board
        self.screen.blit(board.board_surface, board.board_rect)

        # update only the playing board part of the display
        pygame.display.update(board.board_rect)

        # print("updating board")

    # function for displaying the fps (top-right
    def update_fps(self, fps):
        # create function local var with existing Chessboard object
        board = self.chess_board

        surface = board.fps_font.render("FPS: "+str(int(fps)), True, WHITE_CLR, BROWN_CLR)
        
        blit_dest = board.fps_blit_dest

        # surface for deleting previous FPS value
        delete = board.fps_delete_surface

        # remove old fps value
        self.screen.blit(delete, blit_dest)

        # add new fps
        self.screen.blit(surface, blit_dest)

        # update only the screen part of FPS counter
        pygame.display.update((blit_dest), (delete.get_width(), delete.get_height()))

    # changing default system cursor to hand when user hovers over any piece
    def hover_cursor(self, cursor_pos):
        # using select_piece() method to check whether cursor collides with any of the piece's rectangles + if it is the right side (side to move)
        piece = self.select_piece(cursor_pos[0], cursor_pos[1])

        if piece and piece.color == self.chess_board.active_color:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)



    # select piece on board, takes x and y values located on the playing board (returns object of a class Piece)
    def select_piece(self, x, y):
        # cursor on a piece check
        for row in self.chess_board.board_repr:
            for piece in row:
                if isinstance(piece, Piece) and piece.rect.collidepoint(x, y):
                    return piece
        else:
            return None

    # select tile on board (returns row and col int)
    def select_tile(self, x, y):
        row = max(min(math.floor(y/self.tile_height), 7), 0)
        col = max(min(math.floor(x/self.tile_width), 7), 0)

        return row, col

    # method for getting mouse position relative to game board window
    def get_mouse_pos(self):
        x, y = pygame.mouse.get_pos()

        x = x - self.chess_board.board_rect.x
        y = y - self.chess_board.board_rect.y

        return x, y

    def handle_promotion(self, piece, row, col):
        # create function local var with existing Chessboard object
        board = self.chess_board

        # method for selecting promotion piece based on mouse cursor position
        def select_promotion():
            x, y = pygame.mouse.get_pos()
            x -= promotion_menu.x
            y -= promotion_menu.y

            for key in promotion_rects.keys():
                if promotion_rects.get(key).collidepoint(x, y):
                    return key
            
            return None

        # method for highlighting promotion piece while hovering over it (possibly using multithreading)
        def highlight_promotion(promotion_piece):
            piece_image = promotion_rects.get(promotion_piece)
            pass




        self.screen.blit(board.darken, (board.board_rect.x, board.board_rect.y))
                    
        promotion_rects = board.white_promotion_rects if piece.color == "w" else board.black_promotion_rects
        image = board.white_promotion if piece.color == "w" else board.black_promotion

        blit_x = board.board_rect.x + col*self.tile_width
        blit_y = board.board_rect.y if row == 0 else board.board_rect.y + 4*self.tile_height

        promotion_menu = self.screen.blit(image, (blit_x, blit_y))

        pygame.display.update(board.board_rect)

        promotion = None

        # wait until the user selects promotion piece or clicks somewhere else
        while pygame.event.wait().type != pygame.MOUSEBUTTONDOWN:
            # call this method to ensure the game is running at a stable framerate
            self.clock.tick(FPS)
            self.update_fps(self.clock.get_fps())


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE:
                    self.initialize_screen(event.w, event.h, startup=False)
                    self.update_board()
                    return
                 
                # to prevent issue explained in description.txt (issues in making)
                elif event.type == pygame.WINDOWFOCUSGAINED:
                    pygame.display.flip()

            promotion = select_promotion()

            if promotion:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                highlight_promotion(promotion)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
            pygame.display.update(board.board_rect)
            
        # user clicked
        else:
            return promotion

    # method for revising castling privileges
    def revoke_castling(self, active_color, moved_piece, king_pos, castling_rights, board):
        # white
        if active_color == "w":
            # if king moved remove both castling privileges of given color
            if moved_piece.type == "k":
                return castling_rights.replace("K", "").replace("Q", "") # using nested replace because replace("KQ", "") wouldn't work in case of single char - "K"
            
            else:
                # kingside
                if king_pos[1] == abs(moved_piece.col-3):
                    return castling_rights.replace("K", "")
                # queenside
                elif (king_pos[0], king_pos[1]) == (moved_piece.row, abs(moved_piece.col-4)):
                    return castling_rights.replace("Q", "")
        
        #black
        else:
            # if king moved remove both castling privileges of given color
            if moved_piece.type == "k":
                return castling_rights.replace("k", "").replace("q", "")
            
            else:
                # kingside
                if (king_pos[0], king_pos[1]) == (moved_piece.row, abs(moved_piece.col-3)):
                    return castling_rights.replace("k", "")
                # queenside
                elif (king_pos[0], king_pos[1]) == (moved_piece.row, abs(moved_piece.col-4)):
                    return castling_rights.replace("q", "")
        
        return castling_rights



     # check if move is in piece's available moves
    def evaluate_move(self, selected_piece, target_square):
        for move in selected_piece.moves:
            if move.coords == target_square:
                return move

        return False



    # stalemate detection
    def stalemate(self, message, forced=False):
        # create tkinter window and immediately hide it (tkinter's built in message box needs parent window to display)
        window = tk.Tk()
        window.withdraw()

        if not forced:
            question = messagebox.askquestion(title="Draw offer", message=f"Do you want to claim draw by {message}?", icon="question")
            if question == "yes":
                MATCH_END_SOUND.play()
                question = messagebox.askquestion(title="Draw", message=f"You drew by {message}. Do you want to play again?", icon="question")
                if question == "yes":
                    pygame.display.quit()
                    GameWindow().run()
                else:
                    pygame.quit()
                    sys.exit()
        else:
            MATCH_END_SOUND.play()
            question = messagebox.askquestion(title="Draw", message=f"You drew by {message}. Do you want to play again?")
            if question == "yes":
                pygame.display.quit()
                GameWindow().run()
            else:
                pygame.quit()
                sys.exit()


    # checkmate detection
    def checkmate(self):
        MATCH_END_SOUND.play()
        
        # create tkinter window and immediately hide it (tkinter's built in message box needs parent window to display)
        window = tk.Tk()
        window.withdraw()

        question = messagebox.askquestion(title="Checkmate", message="Checkmate! Do you want to play again?")
        if question == "yes":
            pygame.display.quit()
            GameWindow().run()
        else:
            pygame.quit()
            sys.exit()



    # piece movement handling, board updating
    def handle_movement(self, selected_piece):
        # create function local var with existing Chessboard object
        board = self.chess_board


        if selected_piece.color != board.active_color:
            return

        checkmate = False

        # tiles
        board.board_surface.blit(board.tile_surface, (0, 0))

        # selected square
        board.board_surface.blit(board.selected_square, (selected_piece.col*self.tile_width, selected_piece.row*self.tile_height))

        # previous move hightlight squares
        for square in self.recent_moves:
            board.board_surface.blit(board.highlight_square, (square[1]*self.tile_width, square[0]*self.tile_height))

        # available moves
        for move in selected_piece.moves:
            x_move = move.coords[1]*self.tile_width    # cols
            y_move = move.coords[0]*self.tile_height   # rows

            if self.select_piece(x_move, y_move):
                board.board_surface.blit(board.available_capture, (x_move, y_move))
            else:
                board.board_surface.blit(board.available_move, (x_move, y_move))

        # pieces
        board.blit_pieces(board.board_surface, board.board_repr)

        # playing board
        self.screen.blit(board.board_surface, board.board_rect)
        
        # update only the playing board part of the display to see changes while this loop is running
        pygame.display.update(board.board_rect)

        # remove selected piece from board representation (temporarily for creating moving piece animation)
        board.remove_piece(selected_piece.row, selected_piece.col)

        # drag and drop
        while pygame.event.wait().type != pygame.MOUSEBUTTONUP:
            # call this method to ensure the game is running at a stable framerate
            self.clock.tick(FPS)
            self.update_fps(self.clock.get_fps())
        
            x, y = self.get_mouse_pos()

            # restrict the x, y values for visual piece movement
            x = max(min(x, self.board_width-self.tile_width/2), 0+self.tile_width/2)
            y = max(min(y, self.board_height-self.tile_height/2), 0+self.tile_height/2)

            row, col = self.select_tile(x, y)

            # tiles
            board.board_surface.blit(board.tile_surface, (0, 0))

            # selected square
            board.board_surface.blit(board.selected_square, (selected_piece.col*self.tile_width, selected_piece.row*self.tile_height))

            # previous move hightlight squares
            for square in self.recent_moves:
                board.board_surface.blit(board.highlight_square, (square[1]*self.tile_width, square[0]*self.tile_height))

            # target square border
            board.board_surface.blit(board.target_border, (col*self.tile_width, row*self.tile_height))

            # available moves
            for move in selected_piece.moves:
                x_move = move.coords[1]*self.tile_width    # cols
                y_move = move.coords[0]*self.tile_height   # rows

                if self.select_piece(x_move, y_move):
                    board.board_surface.blit(board.available_capture, (x_move, y_move))
                else:
                    board.board_surface.blit(board.available_move, (x_move, y_move))

            # pieces
            board.blit_pieces(board.board_surface, board.board_repr)
            # moving piece
            board.board_surface.blit(selected_piece.image, (x-selected_piece.image.get_width()/2, y-selected_piece.image.get_height()/2))

            # playing board
            self.screen.blit(board.board_surface, board.board_rect)
            
            # update only the playing board part of the display to see changes while this loop is running
            pygame.display.update(board.board_rect)

        else:
            x, y = self.get_mouse_pos()

            x = max(min(x, self.board_width-self.tile_width/2), 0+self.tile_width/2)
            y = max(min(y, self.board_height-self.tile_height/2), 0+self.tile_height/2)

            # return selected piece back to the board representation
            board.remove_piece(selected_piece.row, selected_piece.col, add_new=False)
            board.add_piece(selected_piece.row, selected_piece.col, selected_piece)

            target_piece = self.select_piece(x, y)
            row, col = self.select_tile(x, y)

            move_check = self.evaluate_move(selected_piece, (row, col))

            if move_check and board.board_rect.collidepoint(pygame.mouse.get_pos()):

                # promotion move
                if (row == 0 or row == 7) and selected_piece.type == "p":
                  
                    promotion = self.handle_promotion(selected_piece, row, col)

                    if promotion:
                        # clear and add new recent moves
                        self.recent_moves.clear()
                        self.recent_moves.append((selected_piece.row, selected_piece.col))
                        self.recent_moves.append((row, col))

                        char = promotion.upper() if selected_piece.color == "w" else promotion.lower()
                
                        promoted_piece = Piece(row, col, char, board.piece_images.get(char), self.tile_width, self.tile_height, board.piece_values)

                        # remove the pawn
                        board.remove_piece(selected_piece.row, selected_piece.col)

                        # add new promoted piece
                        board.remove_piece(row, col, add_new=False)
                        board.add_piece(row, col, promoted_piece)

                    else:
                        self.update_board()
                        return

                
                # normal move/capture
                else:
                    # clear and add new recent moves
                    self.recent_moves.clear()
                    self.recent_moves.append((selected_piece.row, selected_piece.col))
                    self.recent_moves.append((row, col))

                    #these actions will change selected piece's row and col attributes as well as change piece's position in board_repr
                    board.remove_piece(selected_piece.row, selected_piece.col)
                    board.remove_piece(row, col, add_new=False)

                    # add selected piece to its new position
                    board.add_piece(row, col, selected_piece)

                    # create new rect for piece since it was moved to another position 
                    selected_piece.rect = selected_piece.create_rect(self.tile_width, self.tile_height)

                board.enpassant_square = None

                # check if move is en passant (in case it is the enemy piece needs to be removed explicitly/directly)
                if move_check.enpassant_piece:
                    board.remove_piece(move_check.enpassant_piece[0], move_check.enpassant_piece[1])
                # check if pawn move created new en passant target square
                if move_check.enpassant_new:
                    board.enpassant_square = move_check.enpassant_new
                if move_check.capture:
                    CAPTURE_SOUND.play()
                elif move_check.castling_rook:
                    # move rook
                    old_pos = move_check.castling_rook[0]
                    new_pos = move_check.castling_rook[1]

                    rook = board.board_repr[old_pos[0]][old_pos[1]]
                
                    board.remove_piece(old_pos[0], old_pos[1])
                  
                    board.remove_piece(new_pos[0], new_pos[1], add_new=False)
                    board.add_piece(new_pos[0], new_pos[1], rook)
                
                    rook.rect = rook.create_rect(self.tile_width, self.tile_height)

                    CASTLE_SOUND.play()
                else:
                    MOVE_SOUND.play()


                # check if king or any of the rooks moved (castling privileges)
                if selected_piece.type == "k" or selected_piece.type == "r":
                    # selected_piece.castling = False
                    
                    # adjust castling privileges after moving king or rook
                    if board.castling:
                        board.castling = self.revoke_castling(board.active_color, selected_piece, board.king_pos, board.castling, board.board_repr)
                
                # reset check
                for row in board.board_repr:
                    for piece in row:
                        if isinstance(piece, Piece) and piece.type == "k" and piece.color == board.active_color:
                            piece.in_check = False
                            break

                # incrementing halfmove counter according to chess rules + clearing positions (threefold repetition handling) for better perf as they won't repeat
                if move_check.capture == True or selected_piece.type == "p":
                    board.halfmove_counter = 0
                    self.positions.clear()
                else:
                    board.halfmove_counter += 1

                # fullmove counter
                board.fullmove_counter += 1

                # change active color (using ternary conditional operator)
                board.active_color = "w" if board.active_color == "b" else "b"

                # generate new moves after making a move and return whether checkmate/stalemate is on the board
                termination = board.generate_moves(board.active_color, board.default_side, board.board_repr)

                self.update_board()

                # stalemate detection (50 move rule)
                if board.halfmove_counter >= 50:
                    self.stalemate("fifty-move rule")

                # stalemate detection (threefold repetition)
                fen_string = board.export_fen(board.board_repr, board.active_color, board.castling, board.enpassant_square, board.halfmove_counter, board.fullmove_counter)
                self.positions.append(" ".join(fen_string.rstrip().split()[:4]))

                if Counter(self.positions).most_common(1)[0][1] == 3:
                    self.stalemate("three-fold repetition")
                    self.positions = [self.positions[-1]]


                if termination == "checkmate":
                    self.checkmate()
                elif termination:
                    self.stalemate(termination, forced=True)


            else:
                self.update_board()


















class ChessBoard:
    def __init__(self, cols, rows, default_side):
        self.COLS = cols
        self.ROWS = rows

        # dictionary for combining piece types with their images
        self.piece_images = {"K": WHITE_KING, "Q": WHITE_QUEEN, "B": WHITE_BISHOP, "N": WHITE_KNIGHT, "R": WHITE_ROOK, "P": WHITE_PAWN,
                            "k": BLACK_KING, "q": BLACK_QUEEN, "b": BLACK_BISHOP, "n": BLACK_KNIGHT, "r": BLACK_ROOK, "p": BLACK_PAWN}

        # dictionary for defining value to each piece
        self.piece_values = {"k": 0, "q": 9, "r": 5, "b": 3, "n": 3, "p": 1}

        # which side is user playing on (black/white)
        self.default_side = default_side

        # default system font for displaying text
        self.default_font = pygame.font.get_default_font()

        # coordinates - first are coords for columns, then rows
        self.internal_coords = [[str(i) for i in range(COLS)], [str(i) for i in range(ROWS)]]
                                # for looping trough ascii lowercase aplhabet in case of greater number of COLS than its own length
        self.algebraic_coords = [[str(string.ascii_lowercase[i%len(string.ascii_lowercase)]) for i in range(COLS)], [str(i) for i in range(ROWS, 0, -1)]]

        # load all move offsets for every piece type
        self.offsets = AllMoves("chess")
        self.offsets.load_moves()
    

    def render_elements(self):

        def draw_tiles(surface, tile_width, tile_height, light_clr, dark_clr):
            # light squares
            for row in range(ROWS):
                for col in range(row%2, COLS, 2):
                    pygame.draw.rect(surface, LIGHT_SQUARE_CLR, (col*tile_width, row*tile_height, tile_width, tile_height))
                    
            # dark squares
            for row in range(ROWS):
                for col in range(abs(row%2-1), COLS, 2):
                    pygame.draw.rect(surface, DARK_SQUARE_CLR, (col*tile_width, row*tile_height, tile_width, tile_height))

        # helping function for creating Pygame Surface objects (without any special arguments)
        def create_surface(width, height, color=False):

            surface = pygame.Surface((width, height))

            # if length of the color arg is 4 it means that the surface requested includes surface aplha
            if color:
                if len(color) == 4:
                    surface = surface.convert_alpha()

                surface.fill(color)

            return surface

            

        # screen width, height
        width =  pygame.display.get_surface().get_width()
        height = pygame.display.get_surface().get_height()

        # tile size 
        self.tile_width = width//16
        self.tile_height = height//9

        # wooden background
        self.background = pygame.transform.scale(BOARD_BG, (width, height))

        # game notation system
        self.game_notation = pygame.transform.scale(NOTATION_SYSTEM, (width//5, height//5))

        # coordinates
        self.col_coords = []
        self.row_coords = []

        coordinate_font_size = (self.tile_height + self.tile_width)//8

        for coord in self.algebraic_coords[0]:
            font = pygame.font.Font(self.default_font, coordinate_font_size)
            font_surface = font.render(coord, True, WHITE_CLR)
            self.col_coords.append(font_surface)
        
        for coord in self.algebraic_coords[1]:
            font = pygame.font.Font(self.default_font, coordinate_font_size)
            font_surface = font.render(coord, True, WHITE_CLR)
            self.row_coords.append(font_surface)

        # fps counter (top-right)
        fps_font_size = coordinate_font_size//2

        self.fps_font = pygame.font.Font(self.default_font, fps_font_size)

        fps_size = self.fps_font.render(f"FPS: {FPS}", False, WHITE_CLR).get_size()
        self.fps_blit_dest = (width-fps_size[0]-self.tile_width//8, self.tile_height//8)

        self.fps_delete_surface = create_surface(fps_size[0], fps_size[1], BROWN_CLR)
        
        # playing board
        self.board_rect = pygame.Rect(0, 0, self.tile_width*COLS, self.tile_height*ROWS)
        self.board_rect.center = (width/2, height/2)

        self.board_surface = create_surface(self.board_rect.width, self.board_rect.height)
        
        # tiles
        self.tile_surface = create_surface(self.board_rect.width, self.board_rect.height)
        draw_tiles(self.tile_surface, self.tile_width, self.tile_height, LIGHT_SQUARE_CLR, DARK_SQUARE_CLR)

        # target square border surface
        self.target_border = create_surface(self.tile_width, self.tile_height, TRANSPARENT_CLR)
                                                                        
        # calculations in the end are to ensure the final width is odd number so that it is centered nicely
        pygame.draw.rect(self.target_border, TARGET_SQUARE_CLR, (0, 0, self.tile_width, self.tile_height), 
                            width=math.floor((self.tile_width+self.tile_height)/24)//2*2+1)

        # previous moves highlight
        self.highlight_square = create_surface(self.tile_width, self.tile_height, SELECTION_CLR)

        # selected square highlight
        self.selected_square = create_surface(self.tile_width, self.tile_height, SELECTED_SQUARE_CLR)

        # centered circle for available moves's squares
        self.available_move = create_surface(self.tile_width, self.tile_height, TRANSPARENT_CLR)

        pygame.draw.circle(self.available_move, AVAILABLE_MOVES_CLR, (self.available_move.get_width()/2, self.available_move.get_height()/2), 
                            (self.tile_width+self.tile_height)//16)
        
        # 4 corner quarter circles for available captures's square
        self.available_capture = create_surface(self.tile_width, self.tile_height, TRANSPARENT_CLR)

        pygame.draw.circle(self.available_capture, AVAILABLE_MOVES_CLR, (0, 0), (self.tile_width+self.tile_height)//16, draw_bottom_right=True)
        pygame.draw.circle(self.available_capture, AVAILABLE_MOVES_CLR, (self.tile_width, 0), (self.tile_width+self.tile_height)//16, draw_bottom_left=True)
        pygame.draw.circle(self.available_capture, AVAILABLE_MOVES_CLR, (0, self.tile_height), (self.tile_width+self.tile_height)//16, draw_top_right=True)
        pygame.draw.circle(self.available_capture, AVAILABLE_MOVES_CLR, (self.tile_width, self.tile_height), (self.tile_width+self.tile_height)//16, draw_top_left=True)

        # surface for darkening the screen while pawn promotion
        self.darken = create_surface(self.board_rect.width, self.board_rect.height, (0, 0, 0, 150))

        # pawn promotion menu
        promotion_piece_size = (int(self.tile_width*PIECE_SIZE**2), int(self.tile_height*PIECE_SIZE**2))
        radius = (self.tile_height+self.tile_width)//4.3
        center_x = self.tile_width/2
        center_y = self.tile_height/2

        self.white_promotion = create_surface(self.tile_width, self.tile_height*4, TRANSPARENT_CLR)
        self.white_promotion_rects = {}
        white_promotion_images = {"q": WHITE_QUEEN, "n": WHITE_KNIGHT, "r": WHITE_ROOK, "b": WHITE_BISHOP}

        self.black_promotion = create_surface(self.tile_width, self.tile_height*4, TRANSPARENT_CLR)
        self.black_promotion_rects = {}
        black_promotion_images = {"q":BLACK_QUEEN, "n":BLACK_KNIGHT, "r":BLACK_ROOK, "b":BLACK_BISHOP}

        for index, key in enumerate(white_promotion_images.keys() if self.default_side == "white" else reversed(white_promotion_images.keys())):

            image_name = white_promotion_images.get(key)
            piece_image = pygame.transform.scale(image_name, promotion_piece_size)

            self.white_promotion_rects.update({key: pygame.draw.circle(self.white_promotion, LIGHT_GREY_CLR, (center_x, index*self.tile_height+center_y), radius)})

            self.white_promotion.blit(piece_image, ((self.tile_width-promotion_piece_size[0])/2, index*self.tile_height+(self.tile_height-promotion_piece_size[1])/2))
            
        for index, key in enumerate(black_promotion_images.keys() if self.default_side == "black" else reversed(black_promotion_images.keys())):

            image_name = black_promotion_images.get(key)
            piece_image = pygame.transform.scale(image_name, promotion_piece_size)

            self.black_promotion_rects.update({key: pygame.draw.circle(self.black_promotion, LIGHT_GREY_CLR, (center_x, index*self.tile_height+center_y), radius)})

            self.black_promotion.blit(piece_image, ((self.tile_width-promotion_piece_size[0])/2, index*self.tile_height+(self.tile_height-promotion_piece_size[1])/2))

        # check background
        self.check_background = pygame.transform.scale(CHECK_BACKGROUND, (self.tile_width, self.tile_height))


    # add piece to board (takes object of a class Piece as an argument)
    def add_piece(self, row, col, piece=None):
        if piece:
            self.board_repr[row].insert(col, piece) # add piece to board representation
            piece.row, piece.col = row, col         # change piece's row and col as well
        else:
            self.board_repr[row].insert(col, None)
    
    # safely remove the piece from the board and replace it with NoneType object (takes object of a class Piece as an argument)
    def remove_piece(self, row, col, add_new=True):
        self.board_repr[row].pop(col)
        # add NoneType object
        if add_new:
            self.add_piece(row, col)

    # method for drawing pieces onto given surface (takes list of pieces containing objects of a class Piece as an argument)
    def blit_pieces(self, surface, piece_list):
        for row in range(self.COLS):
            for col in range(self.ROWS):
                piece = piece_list[row][col]

                if isinstance(piece, Piece): 
                    # if king is in check also blit check background
                    if piece.type == "k" and piece.in_check == True:
                        surface.blit(self.check_background, (piece.rect.x, piece.rect.y))



                    # blit image onto the surface (in the middle of the tile, y value is slightly offsetted to bottom)
                    surface.blit(piece.image, (piece.rect.x+(self.tile_width-piece.image.get_width())/2, 
                                                piece.rect.y+(self.tile_height-piece.image.get_height())/1.8))

    # Forsyth-Edwards Notation (FEN) which describes chess position in one-line ASCII string
    def load_fen(self, fen_string):

        # create internal board represetation
        self.board_repr = [[] for row in range(ROWS)]

        fen_string = fen_string.rstrip().split()
        
        # piece placement
        piece_placement = fen_string[0]

        row = 0
        col = 0

        for char in piece_placement:
            if char in self.piece_images:
                image = self.piece_images.get(char)
                piece = Piece(row, col, char, image, self.tile_width, self.tile_height, self.piece_values)
                self.add_piece(row, col, piece)
                col += 1

            elif char.isdecimal():
                for i in range(int(char)):
                    self.add_piece(row, col)
                    col += 1

            elif char == "/":
                row += 1
                col = 0

        # side to move
        self.active_color = fen_string[1]

        # castling ability (kingside, queenside)
        self.castling = fen_string[2]

        # en passant target square (calculations to match the board_repr coordination system)
        self.enpassant_square = (7-(int(fen_string[3][1])-1), string.ascii_lowercase.index(fen_string[3][0])) if len(fen_string[3])==2 else None

        # halfmove clock
        self.halfmove_counter = int(fen_string[4])

        # fullmove counter
        self.fullmove_counter = int(fen_string[5])

    

    def export_fen(self, board_state, side_to_move, castling_rights, en_passant, halfmove_counter, fullmove_counter):

        fen_string = ""

        spaces = 0
        
        # piece placement
        for row in board_state:
            for piece in row:
                if piece is None:
                    spaces += 1

                elif isinstance(piece, Piece):
                    if spaces:
                        fen_string += str(spaces)
                        spaces = 0                

                    fen_string += piece.type.upper() if piece.color == "w" else piece.type

            if spaces:
                fen_string += str(spaces)
                spaces = 0  

            fen_string += "/"

        fen_string = fen_string.rstrip("/")

        # side to move
        fen_string += f" {side_to_move}"

        # castling ability
        castling_rights = castling_rights if castling_rights else "-"

        fen_string += f" {castling_rights}"

        # en passant target square
        en_passant = string.ascii_lowercase[en_passant[1]]+str(8-en_passant[0]) if en_passant else "-"

        fen_string += f" {en_passant}"

        # halfmove clock
        fen_string += f" {halfmove_counter}"

        # fullmove counter
        fen_string += f" {fullmove_counter}"

        return fen_string



    # return all pseudo-legal moves
    def pseudo_legal(self, active_color, default_side, board):

        color = "b" if active_color == "w" else "w"

        pseudo_legal_moves = []

         # check if move is legal and add move to piece's available moves
        def append_move(row, col, offset):
            row, col = row+offset[0], col+offset[1]

            pseudo_legal_moves.append((row, col))


        # check pseudo-legal validity of a move
        def check_move(row, col, offset):
            row, col = row+offset[0], col+offset[1]
        
            if 0 <= row < ROWS and 0 <= col < COLS:
                if isinstance(board[row][col], Piece) and board[row][col].color != color:
                    return "capture"
                elif board[row][col] is None:
                    return "move"
           
            return False

        sliding_pieces = {"r": self.offsets.rook, "b": self.offsets.bishop, "q": self.offsets.queen}

        for row in range(ROWS):
            for col in range(COLS):

                piece = board[row][col]

                if isinstance(piece, Piece):

                    if piece.color == color:

                        # pawn
                        if piece.type == "p":

                            offsets = self.offsets.white_pawn if color == "w" else self.offsets.black_pawn

                            # pawn pushes
                            if check_move(row, col, offsets[0][0]) == "move":
                                append_move(row, col, offsets[0][0])

                                if check_move(row, col, offsets[0][1]) == "move" and color == "w" and row == 6:
                                    append_move(row, col, offsets[0][1])

                                elif check_move(row, col, offsets[0][1]) == "move" and color == "b" and row == 1:
                                    append_move(row, col, offsets[0][1])
                            
                            # captures + en passant (also adding potential attacking square for pawn)
                            for capture in offsets[1]:
                                if check_move(row, col, capture) == "capture" or check_move(row, col, capture) == "move":
                                    append_move(row, col, capture)
                                elif (row+capture[0], col+capture[1]) == self.enpassant_square:
                                    append_move(row, col, capture)
                        
                        # sliding pieces (e. g. rook, bishop, queen)
                        elif piece.type in sliding_pieces:

                            offsets = sliding_pieces.get(piece.type)

                            for offset in offsets:

                                direction = list(offset)

                                while check_move(row, col, direction) == "move":
                                    append_move(row, col, direction)

                                    direction[0] += offset[0]
                                    direction[1] += offset[1]
                                   
                                else:
                                    if check_move(row, col, direction) == "capture":
                                        append_move(row, col, direction)

                        # knight
                        elif piece.type == "n":
                            for offset in self.offsets.knight:
                                if check_move(row, col, offset) == "move":
                                    append_move(row, col, offset)

                                elif check_move(row, col, offset) == "capture":
                                    append_move(row, col, offset)
                        
                        # king
                        if piece.type == "k":
                            for offset in self.offsets.king:
                                if check_move(row, col, offset) == "move":
                                    append_move(row, col, offset)

                                elif check_move(row, col, offset) == "capture":
                                    append_move(row, col, offset)

        return pseudo_legal_moves

   

    # generate legal moves
    def generate_moves(self, active_color, default_side, board):

        # check if move is legal and add move to piece's available moves
        def add_move(row, col, offset, capture=False, enpassant_new=None, enpassant_piece=None, castling_rook=None):
            # use checkmate var defined in the outher/parent function (generate_moves)
            nonlocal checkmate

            new_row, new_col = row+offset[0], col+offset[1]
            old_row, old_col = row, col

            # if king is moving also change king position
            if piece.type == "k":
                king = new_row, new_col
            else:
                king = self.king_pos

            # generate move ahead
            old_piece = board[new_row][new_col]

            board[old_row][old_col] = None
            board[new_row][new_col] = piece

            pre_generated = self.pseudo_legal(self.active_color, self.default_side, board)

            # move is legal if king isn't attacked after making a move
            if king not in pre_generated:
                board[old_row][old_col] = piece
                board[new_row][new_col] = old_piece

                piece.moves.append(PieceMove((new_row, new_col), capture, enpassant_new, enpassant_piece, castling_rook))

                checkmate = False

            else:
                board[old_row][old_col] = piece
                board[new_row][new_col] = old_piece

        # check pseudo-legal validity of a move
        def check_move(row, col, offset):
            row, col = row+offset[0], col+offset[1]

            if 0 <= row < ROWS and 0 <= col < COLS:
                if isinstance(board[row][col], Piece) and board[row][col].color != active_color:
                    return "capture"
                elif board[row][col] is None:
                    return "move"
           
            return False

        # check if king is in check
        def find_king_pos(color):
            # find king position
            for row in range(ROWS):
                for col in range(COLS):
                    if isinstance(board[row][col], Piece) and board[row][col].type == "k" and board[row][col].color == color:
                        return row, col

        # method for checking in castling move is available for a given color's king
        def check_castling(king, row, col):

            # calculates whether king isn't passing trough a square that is attacked by an enemy piece
            def is_safe(row, col):
                if (row, col) not in opponent_moves and check_move(row, col, (0, 0)) == "move":
                    return True
            
                return False

            if king.color == "w":
                queen_side, king_side = "Q", "K"
            else:
                queen_side, king_side = "q", "k"

            if king_side in self.castling or queen_side in self.castling:

                # calculate number of squares from king to the edge of the board
                left = 0+col
                right = (COLS-1) - col

                # kingside is located on the right
                if left == 4:
                    # kingside
                    rook = self.board_repr[row][col+3]

                    if isinstance(rook, Piece) and rook.type == "r" and king_side in self.castling:
                        if is_safe(row, col+1) and is_safe(row, col+2):
                            # castling arg format -> [(odl rook coords), (new rook coords)]
                            add_move(row, col+2, (0, 0), castling_rook=[(row, col+3), (row, col+1)])

                    # queenside
                    rook = self.board_repr[row][col-4]

                    if isinstance(rook, Piece) and rook.type == "r" and queen_side in self.castling:
                        if is_safe(row, col-1) and is_safe(row, col-2) and check_move(row, col-3, (0, 0)) == "move":
                            add_move(row, col-2, (0, 0), castling_rook=[(row, col-4), (row, col-1)])

                # kingside is located on the left
                else:
                   # kingside
                    rook = self.board_repr[row][col-3]

                    if isinstance(rook, Piece) and rook.type == "r" and king_side in self.castling:
                        if is_safe(row, col-1) and is_safe(row, col-2):
                            # castling arg format -> [(odl rook coords), (new rook coords)]
                            add_move(row, col-2, (0, 0), castling_rook=[(row, col-3), (row, col-1)])

                    # queenside
                    rook = self.board_repr[row][col+4]

                    if isinstance(rook, Piece) and rook.type == "r" and queen_side in self.castling:
                        if is_safe(row, col+1) and is_safe(row, col+2) and check_move(row, col+3, (0, 0)) == "move":
                            add_move(row, col+2, (0, 0), castling_rook=[(row, col+4), (row, col+1)])

        # checkmate detection
        checkmate = True

        # insufficient material detection
        no_pawns = True
        only_knights = True

        # all piece values on the board
        board_value = 0

        # all piece values of the side to move
        current_value = 0

        self.king_pos = find_king_pos(active_color)

        # opponent pseudo-legal moves
        opponent_moves = self.pseudo_legal(active_color, default_side, board)

        sliding_pieces = {"r": self.offsets.rook, "b": self.offsets.bishop, "q": self.offsets.queen}

        for row in range(ROWS):
            for col in range(COLS):

                piece = board[row][col]

                if isinstance(piece, Piece):
                    # reset pre-existing moves of the piece
                    piece.moves = []

                    if piece.color == active_color:

                        # pawn
                        if piece.type == "p":

                            offsets = self.offsets.white_pawn if active_color == "w" else self.offsets.black_pawn

                            # pawn pushes
                            if check_move(row, col, offsets[0][0]) == "move":
                                add_move(row, col, offsets[0][0])

                                if check_move(row, col, offsets[0][1]) == "move" and active_color == "w" and row == 6:
                                    add_move(row, col, offsets[0][1], enpassant_new=(row-1, col))

                                elif check_move(row, col, offsets[0][1]) == "move" and active_color == "b" and row == 1:
                                    add_move(row, col, offsets[0][1], enpassant_new=(row+1, col))
                            
                            # captures + en passant
                            for capture in offsets[1]:
                                if check_move(row, col, capture) == "capture":
                                    add_move(row, col, capture, capture=True)
                                elif (row+capture[0], col+capture[1]) == self.enpassant_square:
                                    add_move(row, col, capture, capture=True, enpassant_piece=(row, col+capture[1]))
                        
                        # sliding pieces (e. g. rook, bishop, queen)
                        elif piece.type in sliding_pieces:

                            offsets = sliding_pieces.get(piece.type)

                            for offset in offsets:

                                direction = list(offset)

                                while check_move(row, col, direction) == "move":
                                    add_move(row, col, direction)

                                    direction[0] += offset[0]
                                    direction[1] += offset[1]
                                   
                                else:
                                    if check_move(row, col, direction) == "capture":
                                        add_move(row, col, direction, capture=True)

                        # knight
                        elif piece.type == "n":
                            for offset in self.offsets.knight:
                                if check_move(row, col, offset) == "move":
                                    add_move(row, col, offset)

                                elif check_move(row, col, offset) == "capture":
                                    add_move(row, col, offset, capture=True)
                        
                        # king
                        if piece.type == "k":
                            # determine whether king is in check
                            if (row, col) in opponent_moves:
                                piece.in_check = True

                            for offset in self.offsets.king:
                                if check_move(row, col, offset) == "move":
                                    add_move(row, col, offset)

                                elif check_move(row, col, offset) == "capture":
                                    add_move(row, col, offset, capture=True)

                            # check if castle move is available
                            check_castling(piece, row, col)

                        current_value += piece.value

                    board_value += piece.value

                    # check if there is at least single pawn on the board
                    if piece.type == "p":
                        no_pawns = False

                    # check if there are only 2 kings and 2 knights of the same color on the board (in which case, checkmate can't be forced, although is possible)
                    if piece.type != "n" and piece.type != "k":
                        only_knights = False

        enemy_value = board_value - current_value

        # checkmate detection in new generated moves
        if checkmate and board[self.king_pos[0]][self.king_pos[1]].in_check:
            return "checkmate"
        elif checkmate:
            return "stalemate"
        # insufficient mating material
        elif no_pawns and current_value <= 3 and enemy_value <= 3:
            return "insufficient material"
        elif only_knights and board_value == 6:
            return "insufficient material"

        return False

    




class Piece:
    def __init__(self, row, col, fen_piece_type, image, tile_width, tile_height, piece_values):
        # row and col of the piece (these values will be changing according to position on the board)
        self.row = row
        self.col = col

        self.tile_width = tile_width
        self.tile_height = tile_height

        # convert multicase piece type format to only lowercase and then differentiate color
        self.type = fen_piece_type.lower()

        if fen_piece_type.isupper():
            self.color = "w"
        else:
            self.color = "b"

        self.rect = self.create_rect(tile_width, tile_height)

        # save the default image for future potential resizing (because some of the transforms are considered destructive - they lose pixel data every time they are performed)
        self.default_image = image

         # create image for given piece
        self.image = self.create_image(tile_width, tile_height)

        # list for storing current possible moves for the piece
        self.moves = []

        # assign piece value
        self.value = piece_values.get(fen_piece_type.lower())

        if self.type == "k":
            self.in_check = False
        
    # method for defining custom representation of the object which belongs to this class
    def __repr__(self):
        return f"{self.type}.{self.color}"

    # create pygame rectangle
    def create_rect(self, tile_width, tile_height):
        x = self.col*tile_width
        y = self.row*tile_height

        return pygame.Rect(x, y, tile_width, tile_height)

    # create image for the given piece
    def create_image(self, tile_width, tile_height, rel_size=PIECE_SIZE):
        # size offset for specific pieces (for reducing stretched effect)
        height_offset = 0
        width_offset = 0

        if self.type == "p":
            width_offset = 0.2
        elif self.type == "r":
            width_offset = 0.1

        piece_width = int((rel_size-width_offset)*tile_width)
        piece_height = int((rel_size-height_offset)*tile_height)

        return pygame.transform.scale(self.default_image, (piece_width, piece_height))
















# attributes representing specific move of a given piece
class PieceMove:
    def __init__(self, target_coords, capture, enpassant_new, enpassant_piece, castling_rook):
        self.coords = target_coords
        self.capture = capture
        self.enpassant_new = enpassant_new
        self.enpassant_piece = enpassant_piece
        self.castling_rook = castling_rook
        














class AllMoves:
    def __init__(self, game_type):
        self.game_type = game_type

    # all offsets for every type of piece in format (row, col) united into logical directions/groups
    def load_moves(self):
        if self.game_type == "chess":
            # specific pieces
            self.king = [(+1, +1), (-1, -1), (+1, -1), (-1, +1),
                        (+1, 0), (-1, 0), (0, +1), (0, -1)]

            self.white_pawn = [[(-1, 0), (-2, 0)], [(-1, -1), (-1, +1)]]
            self.black_pawn = [[(+1, 0), (+2, 0)], [(+1, -1), (+1, +1)]]

            self.knight = [(+2, +1), (+2, -1), (-2, +1), (-2, -1),
                            (+1, +2), (-1, +2), (+1, -2), (-1, -2)]

            # sliding pieces
            self.rook = [[+1, 0], [-1, 0], [0, +1], [0, -1]]

            self.bishop = [[+1, +1], [+1, -1], [-1, -1], [-1, +1]]

            self.queen = [[+1, 0], [-1, 0], [0, +1], [0, -1], [+1, +1], [+1, -1], [-1, -1], [-1, +1]]













if __name__ == '__main__':
    GameWindow().run()