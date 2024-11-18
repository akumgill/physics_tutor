import json
import os
import csv
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Union

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define file paths
questions_file = 'questions.csv'
hints_file = 'hints.csv'
options_file = 'options.csv'

# Define the system prompt
SYSTEM_PROMPT = """You are an experienced physics teacher tasked with creating Hints and corresponding 5 answer options for each hint in a physics problem. Each problem requires a sequence of 4 Hints as follows:
1. Understand the Problem
2. Split into Components
3. Apply Relevant Equations
4. Perform Algebra and Arithmetic

Guidelines:
1. Use LaTeX wrappers to format math expressions. Remember to use valid escape sequences for special characters.
2. Use the line break symbol when applicable for clarity. Remember to use valid escape sequences for special characters.
3. For the 5 options, only Hint 3 may have more than one TRUE option. Hint 1, Hint 2, and each version of Hint 4 must have exactly 1 TRUE option. All other options for these hints should be FALSE.
4. Hint 4 can have multiple variations depending on the equations chosen in Hint 3. Specifically, there is exactly 1 hint for Hint 1, Hint 2, and Hint 3, but there can be multiple hints for Hint 4, tailored to different equation choices made in Hint 3.

Please answer in the JSON format below, only provide a single JSON object, no markdown code fence:

{
  "hint1": {
    "description": "Understand Problem",
    "text": "hint question 1",
    "option": ["option1", "option2", "option3", "option4", "option5"],
    "correctness": ["TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE"]
  },
  "hint2": {
    "description": "Split into Components",
    "text": "hint question 2",
    "option": ["option1", "option2", "option3", "option4", "option5"],
    "correctness": ["TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE"]
  },
  "hint3": {
    "description": "Apply Relevant Equations",
    "text": "hint question 3",
    "option": ["option1", "option2", "option3", "option4", "option5"],
    "correctness": ["TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE"]
  },
  "hint4": [
    {
      "description": "Perform algebra and arithmetic",
      "text": "hint question 4, variation 1",
      "option": ["option1", "option2", "option3", "option4", "option5"],
      "correctness": ["TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE"]
    },
    {
      "description": "Perform algebra and arithmetic",
      "text": "hint question 4, variation 2",
      "option": ["option1", "option2", "option3", "option4", "option5"],
      "correctness": ["TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE"]
    },
    {
      "description": "Perform algebra and arithmetic",
      "text": "hint question 4, variation 3",
      "option": ["option1", "option2", "option3", "option4", "option5"],
      "correctness": ["TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE", "TRUE or FALSE"]
    }
  ]
}

Here is an example of the JSON object you are to generate:
The given problem is: A dolphin jumps with an initial velocity of 25 m/s at an angle of 30° above the horizontal. The dolphin passes through the center of a hoop before returning to the water. If the dolphin is moving horizontally at the instant it goes through the hoop, how high, H, above the water is the center of the hoop?
{
  "hint1": {
    "description": "Understand Problem",
    "text": "What kind of information can we get from the description? What are we solving for?",
    "option": ["Known Information: \\(v_{0,x} = 25 \\cos(30^\\circ) \\, \\text{m/s}\\) \\n We are solving for the height of the hoop", "Known Information: \\(v_{0,y} = 25 \\sin(30^\\circ) \\, \\text{m/s}\\) \\n We are solving for the height of the hoop", "Known Information: \\(v_{0,x} = 25 \\sin(30^\\circ) \\, \\text{m/s}\\) \\n We are solving for the horizontal distance", "Known Information: \\(v_{0,y} = 25 \\cos(30^\\circ) \\, \\text{m/s}\\) \\n We are solving for the horizontal distance", "Known Information: \\(v_{0,x} = 25 \\, \\text{m/s}\\) \\n We are solving for the time of flight"],
    "correctness": ["TRUE", "FALSE", "FALSE", "FALSE", "FALSE"]
  },
  "hint2": {
    "description": "Split into Components",
    "text": "The initial velocity is 25 m/s at an angle of 30° above the horizontal. What are the x and y components of the initial velocity?",
    "option": ["\\(v_{0,x} = 25 \\sin(30^\\circ) \\, \\text{m/s}\\) \\n \\(v_{0,y} = 25 \\cos(30^\\circ) \\, \\text{m/s}\\)", "\\(v_{0,x} = 25 \\cos(30^\\circ) \\, \\text{m/s}\\) \\n \\(v_{0,y} = 25 \\sin(30^\\circ) \\, \\text{m/s}\\)", "\\(v_{0,x} = 25 \\tan(30^\\circ) \\, \\text{m/s}\\) \\n \\(v_{0,y} = 25 \\sin(30^\\circ) \\, \\text{m/s}\\)", "\\(v_{0,x} = 0 \\, \\text{m/s}\\) \\n \\(v_{0,y} = 25 \\, \\text{m/s}\\)", "\\(v_{0,x} = 25 \\, \\text{m/s}\\) \\n \\(v_{0,y} = 0 \\, \\text{m/s}\\)"],
    "correctness": ["FALSE", "TRUE", "FALSE", "FALSE", "FALSE"]
  },
  "hint3": {
    "description": "Apply Relevant Equations",
    "text": "Focusing our attention in the vertical direction, we know the initial velocity, \\(v_{0,y}\\), and the final velocity, \\(v_{f,y}\\), when the dolphin is passing through the hoop at the maximum height. You also know that the acceleration is due to gravity, i.e. \\(a_y = -g\\). Which equation of motion would you like to use to solve the problem? Note that there is more than one acceptable answer.",
    "option": ["\\(v_f = v_0 + at\\) \\n \\(h = v_0 t + \\frac{1}{2} at^2\\)", "\\(v_f^2 = v_0^2 + 2ah\\)", "\\(v_f^2 - v_0^2 = 2ah\\)", "\\(\\frac{1}{2} (mv_f^2 - mv_0^2) = mgh\\)", "\\(h = \\frac{v_0^2 \\sin^2(\\theta)}{2g}\\)"],
    "correctness": ["FALSE", "TRUE", "TRUE", "TRUE", "FALSE"]
  },
  "hint4": [
    {
      "description": "Perform algebra and arithmetic",
      "text": "You have selected the following equation: \\(v_f^2 = v_0^2 + 2ah\\). Which of the following options correctly applies this equation?",
      "option": ["\\(0 = (25 \\sin(30^\\circ))^2 + 2(-9.8)h\\)", "\\(0 = (25 \\cos(30^\\circ))^2 + 2(-9.8)h\\)", "\\(0 = (25 \\sin(30^\\circ))^2 - 2(9.8)h\\)", "\\(0 = (25 \\cos(30^\\circ))^2 - 2(9.8)h\\)", "\\(0 = (25)^2 + 2(-9.8)h\\)"],
      "correctness": ["TRUE", "FALSE", "FALSE", "FALSE", "FALSE"]
    },
    {
      "description": "Perform algebra and arithmetic",
      "text": "You have selected the following equation: \\(v_f^2 - v_0^2 = 2ah\\). Which of the following options correctly applies this equation?",
      "option": ["\\(0 - (25 \\sin(30^\\circ))^2 = 2(-9.8)h\\)", "\\(0 - (25 \\cos(30^\\circ))^2 = 2(-9.8)h\\)", "\\(0 - (25 \\sin(30^\\circ))^2 = -2(9.8)h\\)", "\\(0 - (25 \\cos(30^\\circ))^2 = -2(9.8)h\\)", "\\(0 - (25)^2 = 2(-9.8)h\\)"],
      "correctness": ["TRUE", "FALSE", "FALSE", "FALSE", "FALSE"]
    },
    {
      "description": "Perform algebra and arithmetic",
      "text": "You have selected the following equation: \\(\\frac{1}{2} (mv_f^2 - mv_0^2) = mgh\\). Which of the following options correctly applies this equation?",
      "option": ["\\(\\frac{1}{2} (0 - (25 \\sin(30^\\circ))^2) = 9.8h\\)", "\\(\\frac{1}{2} (0 - (25 \\cos(30^\\circ))^2) = 9.8h\\)", "\\(\\frac{1}{2} (0 - (25 \\sin(30^\\circ))^2) = -9.8h\\)", "\\(\\frac{1}{2} (0 - (25 \\cos(30^\\circ))^2) = -9.8h\\)", "\\(\\frac{1}{2} (0 - (25)^2) = 9.8h\\)"],
      "correctness": ["TRUE", "FALSE", "FALSE", "FALSE", "FALSE"]
    }
  ]
}

Now I will give you a problem, please provide me with Hint questions and Options in a JSON object without markdown code fence.
"""

# Define Pydantic models for structured output
class HintOption(BaseModel):
    option: str
    correctness: str
    feedback: str

class Hint(BaseModel):
    description: str
    text: str
    option: List[HintOption]

class StructuredHints(BaseModel):
    hint1: Hint
    hint2: Hint
    hint3: Hint
    hint4: List[Hint]

def generate_hints(problem):
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"<problem_given>\n{problem}\n<\\problem_given>"
            }
        ],
        response_format=StructuredHints,
    )
    try:
        hints_json = StructuredHints.model_validate_json(response.choices[0].message.content)
        return hints_json
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Response: {response.choices[0].message.content}")
        return None

# Read existing hints and options
with open(hints_file, mode='a', newline='') as hf, open(options_file, mode='a', newline='') as of:
    hints_writer = csv.writer(hf)
    options_writer = csv.writer(of)

    # Read questions
    with open(questions_file, mode='r', newline='') as qf:
        reader = csv.DictReader(qf)
        for row in reader:
            q_id = row['q_id']
            problem = row['text']
            print(f"Generating hints for {q_id}")
            hints = generate_hints(problem)
            if hints:
                # Generate hints.csv entries
                for i in range(1, 5):
                    hint_key = f"hint{i}"
                    hint = getattr(hints, hint_key, None)
                    if hint:
                        if hint_key != "hint4":
                            h_id = f"{q_id}.h{i}"
                            text = hint.text
                            # Assuming kc_id is same as hint number
                            kc_id = f"kc{i}"
                            img_name = "no_img"
                            hints_writer.writerow([h_id, kc_id, text, img_name])
                            
                            # Generate options.csv entries
                            for opt_num, option in enumerate(hint.option, start=1):
                                o_id = f"{q_id}.h{i}.o{opt_num}"
                                feedback = "Good try, but that's not correct. Maybe try a hint?" if option.correctness == "FALSE" else "That's the correct answer. Congratulations on completing the problem!"
                                options_writer.writerow([o_id, option.option, option.correctness, feedback])
                        else:
                            # hint4 is a list of variations
                            for var_num, var in enumerate(hint, start=1):
                                h_id = f"{q_id}.h4_{var_num}"
                                text = var.text
                                kc_id = f"kc4"
                                img_name = "no_img"
                                hints_writer.writerow([h_id, kc_id, text, img_name])
                                
                                # Generate options.csv entries
                                for opt_num, option in enumerate(var.option, start=1):
                                    o_id = f"{q_id}.h4_{var_num}.o{opt_num}"
                                    feedback = "Good try, but that's not correct. Maybe try a hint?" if option.correctness == "FALSE" else "That's the correct answer. Congratulations on completing the problem!"
                                    options_writer.writerow([o_id, option.option, option.correctness, feedback])

print("Hints and options have been generated and appended to hints.csv and options.csv.") 
