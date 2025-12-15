from typing import Optional


class Pieces:
    def __init__(self):
        self.colour = None
        self.points = None
        self.position = None
        self.directions = None

    def possible_legal_moves(self, board) -> list[int]:
        return []


class Pawn(Pieces):
    def __init__(self, colour, position):
        super().__init__()
        self.colour = colour
        self.points = 1
        self.position = position
        self.directions = 1 if colour == "white" else -1

    def possible_legal_moves(self, board):
        moves = []
        # Pawn moves forward one square
        forward = self.position + self.directions * 8
        if 0 <= forward < 64 and board.board[forward] is None:
            moves.append(forward)
            # Pawn can move two squares on its first move
            if (
                self.colour == "white" and self.position >= 8 and self.position < 16
            ) or (
                self.colour == "black" and self.position >= 48 and self.position < 56
            ):
                double_forward = forward + self.directions * 8
                if board.board[double_forward] is None:
                    moves.append(double_forward)
        # Pawn captures diagonally
        capture_left = self.position + self.directions * 7
        capture_right = self.position + self.directions * 9
        if 0 <= capture_left < 64:
            target = board.board[capture_left]
            if target is not None and target.colour != self.colour:
                moves.append(capture_left)
        if 0 <= capture_right < 64:
            target = board.board[capture_right]
            if target is not None and target.colour != self.colour:
                moves.append(capture_right)
        return moves

    def possible_legal_moves_bitboard(self, bitboard, own_pieces):
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
    def __init__(self, colour, position):
        super().__init__()
        self.colour = colour
        self.points = 5
        self.position = position
        self.directions = [8, -8, 1, -1]

    def possible_legal_moves(self, board):
        moves = []
        for direction in self.directions:
            current_position = self.position
            while True:
                current_position += direction
                if not (0 <= current_position < 64):
                    break
                if direction == 1 and current_position % 8 == 0:
                    break
                if direction == -1 and current_position % 8 == 7:
                    break
                target = board.board[current_position]
                if target is None:
                    moves.append(current_position)
                else:
                    if target.colour != self.colour:
                        moves.append(current_position)
                    break
        return moves

    def possible_legal_moves_bitboard(self, bitboard, own_pieces):
        return (
            bitboard << 8 | bitboard >> 8 | bitboard << 1 | bitboard >> 1
        ) & ~own_pieces


class Knight(Pieces):
    def __init__(self, colour, position):
        super().__init__()
        self.colour = colour
        self.points = 3
        self.position = position
        self.directions = [15, 17, 10, 6, -15, -17, -10, -6]

    def possible_legal_moves(self, board):
        moves = []
        for direction in self.directions:
            current_position = self.position + direction
            if 0 <= current_position < 64:
                target = board.board[current_position]
                if target is None or target.colour != self.colour:
                    moves.append(current_position)
        return moves

    def possible_legal_moves_bitboard(self, bitboard, own_pieces):
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

    def possible_legal_moves(self, board):
        moves = []
        for direction in self.directions:
            current_position = self.position
            while True:
                current_position += direction
                if not (0 <= current_position < 64):
                    break
                if direction in [9, -7] and current_position % 8 == 0:
                    break
                if direction in [7, -9] and current_position % 8 == 7:
                    break
                target = board.board[current_position]
                if target is None:
                    moves.append(current_position)
                else:
                    if target.colour != self.colour:
                        moves.append(current_position)
                    break
        return moves

    def possible_legal_moves_bitboard(self, bitboard, own_pieces):
        return (
            bitboard << 9 | bitboard >> 7 | bitboard << 7 | bitboard >> 9 & ~own_pieces
        )


class Queen(Pieces):
    def __init__(self, colour, position):
        super().__init__()
        self.colour = colour
        self.points = 9
        self.position = position

    def possible_legal_moves(self, board):
        moves = []
        rook = Rook(self.colour, self.position)
        bishop = Bishop(self.colour, self.position)
        moves.extend(rook.possible_legal_moves(board))
        moves.extend(bishop.possible_legal_moves(board))
        return moves


class King(Pieces):
    def __init__(self, colour, position):
        super().__init__()
        self.colour = colour
        self.points = 0
        self.position = position
        self.directions = [8, -8, 1, -1, 9, 7, -9, -7]

    def possible_legal_moves(self, board):
        moves = []
        for direction in self.directions:
            current_position = self.position + direction
            if 0 <= current_position < 64:
                target = board.board[current_position]
                if target is None or target.colour != self.colour:
                    moves.append(current_position)
        return moves


class Board:
    def __init__(self):
        self.board: list[Optional[Pieces]] = [None] * 64
        self.bitboard: list[bytearray] = [bytearray(64) for _ in range(12)]
        self.moves: list[str] = []
        self.setup_board()

    def setup_board(self):
        bitstring = bytearray(64)
        for i in range(8):
            self.board[8 + i] = Pawn("white", 8 + i)
            self.board[48 + i] = Pawn("black", 48 + i)
            self.bitboard[0][8 + i] = 1
            self.bitboard[1][48 + i] = 1

        self.board[0] = Rook("white", 0)
        self.board[7] = Rook("white", 7)
        self.board[56] = Rook("black", 56)
        self.board[63] = Rook("black", 63)
        self.bitboard[2][0] = 1
        self.bitboard[2][7] = 1
        self.bitboard[8][56] = 1
        self.bitboard[8][63] = 1

        self.board[1] = Knight("white", 1)
        self.board[6] = Knight("white", 6)
        self.board[57] = Knight("black", 57)
        self.board[62] = Knight("black", 62)
        self.bitboard[3][1] = 1
        self.bitboard[3][6] = 1
        self.bitboard[9][57] = 1
        self.bitboard[9][62] = 1

        self.board[2] = Bishop("white", 2)
        self.board[5] = Bishop("white", 5)
        self.board[58] = Bishop("black", 58)
        self.board[61] = Bishop("black", 61)
        self.bitboard[4][2] = 1
        self.bitboard[4][5] = 1
        self.bitboard[10][58] = 1
        self.bitboard[10][61] = 1

        self.board[3] = Queen("white", 3)
        self.board[59] = Queen("black", 59)
        self.bitboard[5][3] = 1
        self.bitboard[11][59] = 1

        self.board[4] = King("white", 4)
        self.board[60] = King("black", 60)
        self.bitboard[6][4] = 1
        self.bitboard[12][60] = 1
