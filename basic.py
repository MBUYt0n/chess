from typing import Optional

# Files
FILE_A = 0x0101010101010101
FILE_H = 0x8080808080808080
NOT_FILE_A = 0xFEFEFEFEFEFEFEFE
NOT_FILE_H = 0x7F7F7F7F7F7F7F7F

# Ranks
RANK_2 = 0x000000000000FF00
RANK_7 = 0x00FF000000000000


class Pieces:
    def __init__(self):
        self.colour = None
        self.points = None
        self.directions = None


class Pawn(Pieces):
    def __init__(self, colour):
        super().__init__()
        self.colour = colour
        self.points = 1
        self.directions = 1 if colour == "white" else -1

    def possible_legal_moves(self, bitboard, own_pieces):
        direction = 8 if self.colour == "white" else -8
        single_move = (bitboard << direction) & ~own_pieces
        double_move = (
            ((single_move << direction) & ~own_pieces)
            if (self.colour == "white" and (bitboard & 0x000000000000FF00))
            or (self.colour == "black" and (bitboard & 0x00FF000000000000))
            else 0
        )
        return single_move | double_move


class Rook(Pieces):
    def __init__(self, colour):
        super().__init__()
        self.colour = colour
        self.points = 5
        self.directions = [8, -8, 1, -1]

    def possible_legal_moves(self, bitboard, own_pieces):
        return (
            bitboard << 8 | bitboard >> 8 | bitboard << 1 | bitboard >> 1
        ) & ~own_pieces


class Knight(Pieces):
    def __init__(self, colour):
        super().__init__()
        self.colour = colour
        self.points = 3
        self.directions = [15, 17, 10, 6, -15, -17, -10, -6]

    def possible_legal_moves(self, bitboard, own_pieces):
        return (
            bitboard << 15
            | bitboard << 17
            | bitboard << 10
            | bitboard << 6
            | bitboard >> 15
            | bitboard >> 17
            | bitboard >> 10
            | bitboard >> 6
        ) & ~own_pieces


class Bishop(Pieces):
    def __init__(self, colour, position):
        super().__init__()
        self.colour = colour
        self.points = 3
        self.position = position
        self.directions = [9, 7, -9, -7]

    def possible_legal_moves(self, bitboard, own_pieces):
        return (
            bitboard << 9 | bitboard >> 7 | bitboard << 7 | bitboard >> 9
        ) & ~own_pieces


class Queen(Pieces):
    def __init__(self, colour, position):
        super().__init__()
        self.colour = colour
        self.points = 9
        self.position = position

    def possible_legal_moves(self, bitboard, own_pieces):
        return (
            bitboard << 8
            | bitboard >> 8
            | bitboard << 1
            | bitboard >> 1
            | bitboard << 9
            | bitboard >> 7
            | bitboard << 7
            | bitboard >> 9
        ) & ~own_pieces


class King(Pieces):
    def __init__(self, colour, position):
        super().__init__()
        self.colour = colour
        self.points = 0
        self.position = position
        self.directions = [8, -8, 1, -1, 9, 7, -9, -7]

    def possible_legal_moves(self, bitboard, own_pieces):
        return (
            bitboard << 8
            | bitboard >> 8
            | bitboard << 1
            | bitboard >> 1
            | bitboard << 9
            | bitboard >> 7
            | bitboard << 7
            | bitboard >> 9
        ) & ~own_pieces


class Board:
    def __init__(self):
        self.bitboard: list[int] = [0 for _ in range(12)]
        self.moves: list[str] = []
        self.setup_board()

    def setup_board(self):
        self.bitboard[0] = 0x000000000000FF00  # White Pawns
        self.bitboard[6] = 0x00FF000000000000  # Black Pawns

        self.bitboard[3] = 0x0000000000000081  # White Rooks
        self.bitboard[9] = 0x8100000000000000  # Black Rooks

        self.bitboard[1] = 0x0000000000000042  # White Knights
        self.bitboard[7] = 0x4200000000000000  # Black Knights

        self.bitboard[2] = 0x0000000000000024  # White Bishops
        self.bitboard[8] = 0x2400000000000000  # Black Bishops

        self.bitboard[4] = 0x0000000000000008  # White Queens
        self.bitboard[10] = 0x0800000000000000  # Black Queens

        self.bitboard[5] = 0x0000000000000010  # White Kings
        self.bitboard[11] = 0x1000000000000000  # Black Kings
