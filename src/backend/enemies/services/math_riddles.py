import random

def generate_math_riddle():
    """
    Generate a random simple math riddle.

    The riddle can use one of the four basic operations:
    - Addition (+)
    - Subtraction (-)
    - Multiplication (*)
    - Division (/), restricted so that the result is always an integer.

    Returns:
        tuple[str, int]: A tuple containing:
            - question (str): The math riddle in plain English
            - answer (int): The correct integer answer to the riddle

    Example:
        q, a = generate_math_riddle()
        print(q)
        "What is 42 / 6?"
        print(a)
        7
    """
    answer = -1
    while not 0 < answer < 100:
        operations = ["+", "-", "*", "/"]
        op = random.choice(operations)

        a = random.randint(1, 100)
        b = random.randint(1, 100)

        if op == "/":
            # ensure integer division by constructing a divisible pair
            b = random.randint(1, 10)
            a = b * random.randint(1, 10)

        question = f"What is {a} {op} {b}?"
        answer = eval(f"{a}{op}{b}")
        answer = int(answer)
    return {"riddle": question, "answer": answer}