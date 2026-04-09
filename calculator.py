#!/usr/bin/env python3
"""Simple command-line calculator."""


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


def main():
    print("Simple Calculator")
    print("Operations: +, -, *, /")

    while True:
        op = input("Choose operation (+, -, *, /) or q to quit: ").strip()

        if op.lower() == "q":
            print("Goodbye!")
            break

        if op not in {"+", "-", "*", "/"}:
            print("Invalid operation. Try again.")
            continue

        try:
            a = float(input("Enter first number: ").strip())
            b = float(input("Enter second number: ").strip())

            if op == "+":
                result = add(a, b)
            elif op == "-":
                result = subtract(a, b)
            elif op == "*":
                result = multiply(a, b)
            else:
                result = divide(a, b)

            print(f"Result: {result}")
        except ValueError as err:
            print(f"Error: {err}")


if __name__ == "__main__":
    main()
