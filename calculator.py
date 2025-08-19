# Simple Calculator Program

def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        return "Error: Division by zero"
    return x / y

def calculator():
    print("Simple Calculator")
    print("Enter 'quit' to exit.")

    while True:
        try:
            num1_str = input("Enter first number: ")
            if num1_str.lower() == 'quit':
                break
            num1 = float(num1_str)

            operator = input("Enter operator (+, -, *, /): ")
            if operator.lower() == 'quit':
                break

            num2_str = input("Enter second number: ")
            if num2_str.lower() == 'quit':
                break
            num2 = float(num2_str)

            if operator == '+':
                result = add(num1, num2)
            elif operator == '-':
                result = subtract(num1, num2)
            elif operator == '*':
                result = multiply(num1, num2)
            elif operator == '/':
                result = divide(num1, num2)
            else:
                result = "Invalid operator"

            print(f"Result: {result}")

        except ValueError:
            print("Invalid input. Please enter numbers only.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    calculator()