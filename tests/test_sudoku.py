"""Tests for the sudoku-support library."""

import pytest

from sudoku import SudokuBoard, EMPTY, SIZE


# ---------------------------------------------------------------------------
# Classic "easy" puzzle (from many textbooks / online validators)
# ---------------------------------------------------------------------------
EASY_PUZZLE = (
    "530070000"
    "600195000"
    "098000060"
    "800060003"
    "400803001"
    "700020006"
    "060000280"
    "000419005"
    "000080079"
)

EASY_SOLUTION = (
    "534678912"
    "672195348"
    "198342567"
    "859761423"
    "426853791"
    "713924856"
    "961537284"
    "287419635"
    "345286179"
)

# A puzzle with no solution
UNSOLVABLE_PUZZLE = (
    "516849732"
    "307605000"
    "000000005"
    "005030600"
    "040050060"
    "060070800"
    "000000000"
    "000000000"
    "000000001"  # second 1 in last column – makes it unsolvable
)

# Known-invalid board (two 5s in the first row)
INVALID_BOARD = (
    "550070000"
    "600195000"
    "098000060"
    "800060003"
    "400803001"
    "700020006"
    "060000280"
    "000419005"
    "000080079"
)


# ===========================================================================
# SudokuBoard construction
# ===========================================================================


class TestConstruction:
    def test_default_empty_board(self):
        board = SudokuBoard()
        for r in range(SIZE):
            for c in range(SIZE):
                assert board.get(r, c) == EMPTY

    def test_from_string_digits(self):
        board = SudokuBoard.from_string(EASY_PUZZLE)
        # Check a few known values
        assert board.get(0, 0) == 5
        assert board.get(0, 1) == 3
        assert board.get(0, 2) == EMPTY
        assert board.get(8, 8) == 9

    def test_from_string_dots(self):
        dotted = EASY_PUZZLE.replace("0", ".")
        board = SudokuBoard.from_string(dotted)
        assert board.get(0, 2) == EMPTY

    def test_from_string_with_separators(self):
        # Pipe/dash separators should be silently ignored
        formatted = (
            "5 3 0 | 0 7 0 | 0 0 0\n"
            "6 0 0 | 1 9 5 | 0 0 0\n"
            "0 9 8 | 0 0 0 | 0 6 0\n"
            "------+-------+------\n"
            "8 0 0 | 0 6 0 | 0 0 3\n"
            "4 0 0 | 8 0 3 | 0 0 1\n"
            "7 0 0 | 0 2 0 | 0 0 6\n"
            "------+-------+------\n"
            "0 6 0 | 0 0 0 | 2 8 0\n"
            "0 0 0 | 4 1 9 | 0 0 5\n"
            "0 0 0 | 0 8 0 | 0 7 9\n"
        )
        board = SudokuBoard.from_string(formatted)
        assert board.get(0, 0) == 5

    def test_from_string_wrong_length(self):
        with pytest.raises(ValueError):
            SudokuBoard.from_string("123")

    def test_grid_wrong_size(self):
        with pytest.raises(ValueError):
            SudokuBoard([[0] * 8 for _ in range(9)])

    def test_grid_invalid_value(self):
        grid = [[0] * 9 for _ in range(9)]
        grid[0][0] = 10
        with pytest.raises(ValueError):
            SudokuBoard(grid)

    def test_set_and_get(self):
        board = SudokuBoard()
        board.set(4, 4, 7)
        assert board.get(4, 4) == 7

    def test_set_invalid_value(self):
        board = SudokuBoard()
        with pytest.raises(ValueError):
            board.set(0, 0, 10)


# ===========================================================================
# Validation
# ===========================================================================


class TestValidation:
    def test_empty_board_is_valid(self):
        assert SudokuBoard().is_valid()

    def test_easy_puzzle_is_valid(self):
        board = SudokuBoard.from_string(EASY_PUZZLE)
        assert board.is_valid()

    def test_solution_is_valid(self):
        board = SudokuBoard.from_string(EASY_SOLUTION)
        assert board.is_valid()

    def test_invalid_board_row_duplicate(self):
        board = SudokuBoard.from_string(INVALID_BOARD)
        assert not board.is_valid()

    def test_invalid_col_duplicate(self):
        board = SudokuBoard()
        board.set(0, 0, 5)
        board.set(1, 0, 5)
        assert not board.is_valid()

    def test_invalid_box_duplicate(self):
        board = SudokuBoard()
        board.set(0, 0, 5)
        board.set(2, 2, 5)
        assert not board.is_valid()

    def test_not_solved_when_incomplete(self):
        board = SudokuBoard.from_string(EASY_PUZZLE)
        assert not board.is_solved()

    def test_solved_complete_solution(self):
        board = SudokuBoard.from_string(EASY_SOLUTION)
        assert board.is_solved()


# ===========================================================================
# Candidates
# ===========================================================================


class TestCandidates:
    def test_candidates_empty_board_full_set(self):
        board = SudokuBoard()
        assert board.candidates(0, 0) == set(range(1, 10))

    def test_candidates_no_candidates_for_filled_cell(self):
        board = SudokuBoard()
        board.set(0, 0, 5)
        assert board.candidates(0, 0) == set()

    def test_candidates_eliminates_row(self):
        board = SudokuBoard()
        board.set(0, 1, 3)
        cands = board.candidates(0, 0)
        assert 3 not in cands

    def test_candidates_eliminates_col(self):
        board = SudokuBoard()
        board.set(1, 0, 7)
        cands = board.candidates(0, 0)
        assert 7 not in cands

    def test_candidates_eliminates_box(self):
        board = SudokuBoard()
        board.set(1, 1, 9)
        cands = board.candidates(0, 0)
        assert 9 not in cands


# ===========================================================================
# Solver
# ===========================================================================


class TestSolver:
    def test_solve_easy_puzzle(self):
        board = SudokuBoard.from_string(EASY_PUZZLE)
        assert board.solve()
        assert board.is_solved()
        expected = SudokuBoard.from_string(EASY_SOLUTION)
        assert board.grid == expected.grid

    def test_solve_does_not_modify_on_failure(self):
        # An already-invalid board should not be solvable
        board = SudokuBoard.from_string(INVALID_BOARD)
        original = [row[:] for row in board.grid]
        result = board.solve()
        assert not result
        assert board.grid == original

    def test_solve_already_solved(self):
        board = SudokuBoard.from_string(EASY_SOLUTION)
        assert board.solve()
        assert board.is_solved()

    def test_solve_empty_board(self):
        board = SudokuBoard()
        assert board.solve()
        assert board.is_solved()


# ===========================================================================
# Representation
# ===========================================================================


class TestRepresentation:
    def test_str_contains_separators(self):
        board = SudokuBoard.from_string(EASY_PUZZLE)
        s = str(board)
        assert "------+-------+------" in s

    def test_str_empty_shown_as_dot(self):
        board = SudokuBoard()
        s = str(board)
        assert "." in s
        assert "0" not in s

    def test_repr_round_trip(self):
        board = SudokuBoard.from_string(EASY_PUZZLE)
        reconstructed = eval(repr(board), {"SudokuBoard": SudokuBoard})
        assert board.grid == reconstructed.grid

    def test_copy_independence(self):
        board = SudokuBoard.from_string(EASY_PUZZLE)
        copy = board.copy()
        copy.set(0, 0, 1)
        assert board.get(0, 0) != 1
