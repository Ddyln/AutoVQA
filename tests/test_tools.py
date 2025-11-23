import os
import sys
import typing
from math import ceil, sqrt


def add_numbers(a: int, b: int) -> int:
    return a + b


def main():
    print("Hello, world!")
    x = add_numbers(1, 2)
    print(f"Result: {x}")
    # type error for mypy
    y = add_numbers("3", 4)
    print(y)


if __name__ == "__main__":
    main()
