"""Command-line interface for sudoku-support."""

import argparse
import sys

from sudoku import SudokuBoard


def cmd_solve(args: argparse.Namespace) -> int:
    raw = args.puzzle
    try:
        board = SudokuBoard.from_string(raw)
    except ValueError as exc:
        print(f"Error parsing puzzle: {exc}", file=sys.stderr)
        return 1

    if not board.is_valid():
        print("The provided puzzle is not valid (duplicate digits).", file=sys.stderr)
        return 1

    print("Puzzle:")
    print(board)
    print()

    if board.solve():
        print("Solution:")
        print(board)
    else:
        print("No solution exists for this puzzle.", file=sys.stderr)
        return 1

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    raw = args.puzzle
    try:
        board = SudokuBoard.from_string(raw)
    except ValueError as exc:
        print(f"Error parsing puzzle: {exc}", file=sys.stderr)
        return 1

    if board.is_solved():
        print("The puzzle is a valid, complete solution.")
    elif board.is_valid():
        print("The puzzle state is valid (no duplicates) but not yet complete.")
    else:
        print("The puzzle state is INVALID (duplicate digits detected).")
        return 1

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sudoku",
        description="Sudoku support tool: solve or validate Sudoku puzzles.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    solve_p = sub.add_parser("solve", help="Solve a Sudoku puzzle")
    solve_p.add_argument(
        "puzzle",
        help=(
            "81-character puzzle string. Use 0 or . for empty cells. "
            "Example: "
            "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
        ),
    )

    validate_p = sub.add_parser("validate", help="Validate a Sudoku puzzle or solution")
    validate_p.add_argument(
        "puzzle",
        help="81-character puzzle or solution string.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "solve":
        sys.exit(cmd_solve(args))
    elif args.command == "validate":
        sys.exit(cmd_validate(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
