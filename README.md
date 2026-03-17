# sudoku-support

A Python library and command-line tool for working with Sudoku puzzles.

## Features

- **Board representation** – create a 9×9 board from a grid, an 81-character string, or a
  formatted string with visual separators.
- **Validation** – check that no row, column, or 3×3 box contains repeated digits.
- **Candidate computation** – find the set of valid digits for any empty cell.
- **Solver** – solve any valid puzzle using backtracking with the MRV (minimum remaining
  values) heuristic.
- **CLI** – `solve` and `validate` commands for quick interactive use.

## Requirements

- Python 3.8+
- `pytest` (for running tests only)

## Usage

### Library

```python
from sudoku import SudokuBoard

# Parse an 81-character string (0 or . for empty cells)
board = SudokuBoard.from_string(
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

print(board.is_valid())   # True
print(board.is_solved())  # False

board.solve()

print(board.is_solved())  # True
print(board)
```

Output:

```
5 3 4 | 6 7 8 | 9 1 2
6 7 2 | 1 9 5 | 3 4 8
1 9 8 | 3 4 2 | 5 6 7
------+-------+------
8 5 9 | 7 6 1 | 4 2 3
4 2 6 | 8 5 3 | 7 9 1
7 1 3 | 9 2 4 | 8 5 6
------+-------+------
9 6 1 | 5 3 7 | 2 8 4
2 8 7 | 4 1 9 | 6 3 5
3 4 5 | 2 8 6 | 1 7 9
```

### Command-line interface

**Solve a puzzle**

```
python cli.py solve 530070000600195000098000060800060003400803001700020006060000280000419005000080079
```

**Validate a puzzle or solution**

```
python cli.py validate 534678912672195348198342567859761423426853791713924856961537284287419635345286179
# The puzzle is a valid, complete solution.
```

## Running tests

```
pip install pytest
pytest tests/ -v
```
