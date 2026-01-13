from typing import Optional

# Files
FILE_A = 0x0101010101010101
FILE_H = 0x8080808080808080
NOT_FILE_A = 0xFEFEFEFEFEFEFEFE
NOT_FILE_H = 0x7F7F7F7F7F7F7F7F
NOT_FILE_AB = 0xFCFCFCFCFCFCFCFC
NOT_FILE_GH = 0x3F3F3F3F3F3F3F3F

# Ranks
RANK_2 = 0x000000000000FF00
RANK_7 = 0x00FF000000000000


class Pieces:
    def __init__(self):
        self.colour = None
        self.points = None


class Pawn(Pieces):
    def __init__(self, colour):
        super().__init__()
        self.colour = colour
        self.points = 1

    def possible_legal_moves_white(self, pawns, enemy_pieces, empty):
        one_step = (pawns << 8) & empty

        two_step = ((one_step & (RANK_2 << 8)) << 8) & empty

        captures_left = (pawns << 7) & NOT_FILE_H & enemy_pieces
        captures_right = (pawns << 9) & NOT_FILE_A & enemy_pieces

        return one_step | two_step | captures_left | captures_right

    def possible_legal_moves_black(self, pawns, enemy_pieces, empty):
        one_step = (pawns >> 8) & empty

        two_step = ((one_step & (RANK_7 >> 8)) >> 8) & empty

        captures_left = (pawns >> 9) & NOT_FILE_H & enemy_pieces
        captures_right = (pawns >> 7) & NOT_FILE_A & enemy_pieces

        return one_step | two_step | captures_left | captures_right

    def possible_legal_moves(self, bitboard, enemy_pieces, empty):
        if self.colour == "white":
            return self.possible_legal_moves_white(bitboard, enemy_pieces, empty)
        else:
            return self.possible_legal_moves_black(bitboard, enemy_pieces, empty)


def _slide_straight(bitboard, own_pieces, occupied):
    moves = 0
    # north
    cur = bitboard
    while True:
        cur = (cur << 8) & 0xFFFFFFFFFFFFFFFF
        if not cur:
            break
        moves |= cur
        if cur & occupied:
            break
    # south
    cur = bitboard
    while True:
        cur = cur >> 8
        if not cur:
            break
        moves |= cur
        if cur & occupied:
            break
    # east
    cur = bitboard
    while True:
        cur = (cur & NOT_FILE_H) << 1 & 0xFFFFFFFFFFFFFFFF
        if not cur:
            break
        moves |= cur
        if cur & occupied:
            break
    # west
    cur = bitboard
    while True:
        cur = (cur & NOT_FILE_A) >> 1
        if not cur:
            break
        moves |= cur
        if cur & occupied:
            break
    return moves & ~own_pieces


def _slide_diag(bitboard, own_pieces, occupied):
    moves = 0
    # north-east
    cur = bitboard
    while True:
        cur = (cur & NOT_FILE_H) << 9 & 0xFFFFFFFFFFFFFFFF
        if not cur:
            break
        moves |= cur
        if cur & occupied:
            break
    # north-west
    cur = bitboard
    while True:
        cur = (cur & NOT_FILE_A) << 7 & 0xFFFFFFFFFFFFFFFF
        if not cur:
            break
        moves |= cur
        if cur & occupied:
            break
    # south-east
    cur = bitboard
    while True:
        cur = (cur & NOT_FILE_H) >> 7
        if not cur:
            break
        moves |= cur
        if cur & occupied:
            break
    # south-west
    cur = bitboard
    while True:
        cur = (cur & NOT_FILE_A) >> 9
        if not cur:
            break
        moves |= cur
        if cur & occupied:
            break
    return moves & ~own_pieces


class Rook(Pieces):
    def __init__(self, colour):
        super().__init__()
        self.colour = colour
        self.points = 5

    def possible_legal_moves(self, bitboard, own_pieces, occupied):
        return _slide_straight(bitboard, own_pieces, occupied)


class Bishop(Pieces):
    def __init__(self, colour):
        super().__init__()
        self.colour = colour
        self.points = 3

    def possible_legal_moves(self, bitboard, own_pieces, occupied):
        return _slide_diag(bitboard, own_pieces, occupied)


class Queen(Pieces):
    def __init__(self, colour):
        super().__init__()
        self.colour = colour
        self.points = 9

    def possible_legal_moves(self, bitboard, own_pieces, occupied):
        return _slide_straight(bitboard, own_pieces, occupied) | _slide_diag(
            bitboard, own_pieces, occupied
        )


class Knight(Pieces):
    def __init__(self, colour):
        super().__init__()
        self.colour = colour
        self.points = 3

    def possible_legal_moves(self, bitboard, own_pieces):
        return (
            ((bitboard & NOT_FILE_A) << 15)
            | ((bitboard & NOT_FILE_H) << 17)
            | ((bitboard & NOT_FILE_AB) << 10)
            | ((bitboard & NOT_FILE_GH) << 6)
            | ((bitboard & NOT_FILE_H) >> 15)
            | ((bitboard & NOT_FILE_A) >> 17)
            | ((bitboard & NOT_FILE_GH) >> 10)
            | ((bitboard & NOT_FILE_AB) >> 6)
        ) & ~own_pieces


class King(Pieces):
    def __init__(self, colour):
        super().__init__()
        self.colour = colour
        self.points = 0

    def possible_legal_moves(self, bitboard, own_pieces):
        return (
            ((bitboard << 8) & 0xFFFFFFFFFFFFFFFF)
            | (bitboard >> 8)
            | ((bitboard & NOT_FILE_H) << 1 & 0xFFFFFFFFFFFFFFFF)
            | ((bitboard & NOT_FILE_A) >> 1)
            | ((bitboard & NOT_FILE_H) << 9 & 0xFFFFFFFFFFFFFFFF)
            | ((bitboard & NOT_FILE_A) << 7 & 0xFFFFFFFFFFFFFFFF)
            | ((bitboard & NOT_FILE_H) >> 7)
            | ((bitboard & NOT_FILE_A) >> 9)
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
