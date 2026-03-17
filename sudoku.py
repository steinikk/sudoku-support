"""
Sudoku support library.

Provides board representation, validation, candidate computation, and solving.
"""

from __future__ import annotations

from copy import deepcopy
from typing import List, Optional


EMPTY = 0
SIZE = 9
BOX_SIZE = 3
DIGITS = set(range(1, SIZE + 1))


class SudokuBoard:
    """Represents a 9x9 Sudoku board."""

    def __init__(self, grid: Optional[List[List[int]]] = None) -> None:
        if grid is None:
            self.grid = [[EMPTY] * SIZE for _ in range(SIZE)]
        else:
            if len(grid) != SIZE or any(len(row) != SIZE for row in grid):
                raise ValueError("Grid must be 9x9")
            for row in grid:
                for val in row:
                    if val not in range(0, SIZE + 1):
                        raise ValueError(
                            f"Cell values must be 0–9, got {val!r}"
                        )
            self.grid = [list(row) for row in grid]

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_string(cls, s: str) -> "SudokuBoard":
        """
        Parse a board from an 81-character string.

        Digits 1-9 are filled cells; '0', '.' or '_' represent empty cells.
        All other characters (spaces, newlines, pipes, dashes) are ignored.
        """
        digits = []
        for ch in s:
            if ch.isdigit():
                digits.append(int(ch))
            elif ch in "._":
                digits.append(EMPTY)
            # spaces, pipes, dashes, newlines, and other separators are silently skipped
        if len(digits) != SIZE * SIZE:
            raise ValueError(
                f"Expected 81 cells, got {len(digits)}"
            )
        grid = [digits[r * SIZE : (r + 1) * SIZE] for r in range(SIZE)]
        return cls(grid)

    # ------------------------------------------------------------------
    # Basic accessors
    # ------------------------------------------------------------------

    def get(self, row: int, col: int) -> int:
        return self.grid[row][col]

    def set(self, row: int, col: int, value: int) -> None:
        if value not in range(0, SIZE + 1):
            raise ValueError(f"Value must be 0–9, got {value!r}")
        self.grid[row][col] = value

    # ------------------------------------------------------------------
    # Candidate logic
    # ------------------------------------------------------------------

    def _row_values(self, row: int) -> set:
        return {v for v in self.grid[row] if v != EMPTY}

    def _col_values(self, col: int) -> set:
        return {self.grid[r][col] for r in range(SIZE) if self.grid[r][col] != EMPTY}

    def _box_values(self, row: int, col: int) -> set:
        br, bc = (row // BOX_SIZE) * BOX_SIZE, (col // BOX_SIZE) * BOX_SIZE
        return {
            self.grid[r][c]
            for r in range(br, br + BOX_SIZE)
            for c in range(bc, bc + BOX_SIZE)
            if self.grid[r][c] != EMPTY
        }

    def candidates(self, row: int, col: int) -> set:
        """Return the set of valid digits for the given empty cell."""
        if self.grid[row][col] != EMPTY:
            return set()
        used = self._row_values(row) | self._col_values(col) | self._box_values(row, col)
        return DIGITS - used

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _group_is_valid(self, values: List[int]) -> bool:
        filled = [v for v in values if v != EMPTY]
        return len(filled) == len(set(filled))

    def is_valid(self) -> bool:
        """
        Return True if the board contains no repeated digits in any row,
        column, or 3×3 box (empty cells are allowed).
        """
        for i in range(SIZE):
            if not self._group_is_valid(self.grid[i]):
                return False
            col = [self.grid[r][i] for r in range(SIZE)]
            if not self._group_is_valid(col):
                return False
        for br in range(0, SIZE, BOX_SIZE):
            for bc in range(0, SIZE, BOX_SIZE):
                box = [
                    self.grid[r][c]
                    for r in range(br, br + BOX_SIZE)
                    for c in range(bc, bc + BOX_SIZE)
                ]
                if not self._group_is_valid(box):
                    return False
        return True

    def is_solved(self) -> bool:
        """Return True if every cell is filled and the board is valid."""
        all_filled = all(
            self.grid[r][c] != EMPTY
            for r in range(SIZE)
            for c in range(SIZE)
        )
        return all_filled and self.is_valid()

    # ------------------------------------------------------------------
    # Solver
    # ------------------------------------------------------------------

    def solve(self) -> bool:
        """
        Solve the board in-place using backtracking with MRV heuristic.

        Returns True if a solution was found and the board is updated,
        False if no solution exists (the board is left unchanged in that case).
        """
        if not self.is_valid():
            return False

        # Find the unfilled cell with the fewest candidates (MRV heuristic)
        best = None
        best_cands: set = set()
        for r in range(SIZE):
            for c in range(SIZE):
                if self.grid[r][c] == EMPTY:
                    cands = self.candidates(r, c)
                    if not cands:
                        return False  # dead end
                    if best is None or len(cands) < len(best_cands):
                        best = (r, c)
                        best_cands = cands

        if best is None:
            return True  # all cells filled

        row, col = best
        for digit in sorted(best_cands):
            self.grid[row][col] = digit
            if self.solve():
                return True
            self.grid[row][col] = EMPTY

        return False

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        lines = []
        for r in range(SIZE):
            if r > 0 and r % BOX_SIZE == 0:
                lines.append("------+-------+------")
            row_parts = []
            for c in range(SIZE):
                if c > 0 and c % BOX_SIZE == 0:
                    row_parts.append("|")
                val = self.grid[r][c]
                row_parts.append("." if val == EMPTY else str(val))
            lines.append(" ".join(row_parts))
        return "\n".join(lines)

    def __repr__(self) -> str:
        flat = "".join(
            str(self.grid[r][c]) for r in range(SIZE) for c in range(SIZE)
        )
        return f"SudokuBoard.from_string({flat!r})"

    def copy(self) -> "SudokuBoard":
        return SudokuBoard(deepcopy(self.grid))
