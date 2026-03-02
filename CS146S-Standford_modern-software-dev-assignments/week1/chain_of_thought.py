import os
import re
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 5

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """
Let's calculate 3^{5} (mod 7) by working through it step by step.

First, let's understand what modular exponentiation means:
- We want to calculate base^{exponent} (mod modulus)
- In this case: base = 3, exponent = 5, modulus = 7
- So we need 3^5 mod 7

Step 1: Write the exponent (13) in binary
13 in binary = 1101 (working right to left: 13 = 8 + 4 + 0 + 1)

Step 2: Track two things:
   - result (starts at 1)
   - base power (starts at base = 3)
   Process each binary digit from right to left

Step 3: Process each bit:
   Binary:   1    1    0    1
   Power:    2^3  2^2  2^1  2^0 (reading right to left)

Let's work through it:

Initialize:
result = 1
current_base = 3 mod 7 = 3

Process from rightmost bit (least significant) to leftmost:

Bit 0 (rightmost, 2^0 place = 1):
- Bit = 1 → result = result × current_base = 1 × 3 = 3
- Square current_base: current_base = 3^2 = 9 mod 7 = 2

Bit 1 (2^1 place = 2):
- Bit = 0 → no multiplication needed
- Square current_base: current_base = 2^2 = 4 mod 7 = 4

Bit 2 (2^2 place = 4):
- Bit = 1 → result = result × current_base = 3 × 4 = 12 mod 7 = 5
- Square current_base: current_base = 4^2 = 16 mod 7 = 2

Bit 3 (2^3 place = 8):
- Bit = 1 → result = result × current_base = 5 × 2 = 10 mod 7 = 3
- Square current_base: current_base = 2^2 = 4 mod 7 = 4 (not needed after last bit)

Final result = 3

Answer: 3
"""


USER_PROMPT = """
Solve this problem, then give the final answer on the last line as "Answer: <number>".

what is 3^{12345} (mod 100)?
"""


# For this simple example, we expect the final numeric answer only
EXPECTED_OUTPUT = "Answer: 43"


def extract_final_answer(text: str) -> str:
    """Extract the final 'Answer: ...' line from a verbose reasoning trace.

    - Finds the LAST line that starts with 'Answer:' (case-insensitive)
    - Normalizes to 'Answer: <number>' when a number is present
    - Falls back to returning the matched content if no number is detected
    """
    matches = re.findall(r"(?mi)^\s*answer\s*:\s*(.+)\s*$", text)
    if matches:
        value = matches[-1].strip()
        # Prefer a numeric normalization when possible (supports integers/decimals)
        num_match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        if num_match:
            return f"Answer: {num_match.group(0)}"
        return f"Answer: {value}"
    return text.strip()


def test_your_prompt(system_prompt: str) -> bool:
    """Run up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="llama3.1:8b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.3},
        )
        output_text = response.message.content
        final_answer = extract_final_answer(output_text)
        if final_answer.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {final_answer}")
    return False


if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)


