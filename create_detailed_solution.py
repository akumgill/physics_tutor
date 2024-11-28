import json
import os
from openai import OpenAI
import csv

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Read the existing CSV file and update each row
csv_file_path = 'questions.csv'
rows = []

SYSTEM_PROMPT = """You are an experienced physics teacher. Your task is to provide the detailed solution to a physics problem in 4 steps: 
Understand Problem
Split into Components
Apply Relevant Equations
Perform algebra and arithmetic

Please use LaTeX wrappers to wrap math expressions in the solutions. 
You may use multiple lines separated by a line break \n in your solution for clarity. 

Please answer in the JSON format below, only provide a single JSON object, no markdown code fence:

{
  "Step1": {
    "Description": "Understand Problem",
    "Solution": "solution"
  },
  "Step2": {
    "Description": "Split into Components",
    "Solution": "solution"
  },
  "Step3": {
    "Description": "Apply Relevant Equations",
    "Solution": "solution"
  },
  "Step4": {
    "Description": "Perform algebra and arithmetic",
    "Solution": "solution"
  }
}
"""

# Read the existing data
with open(csv_file_path, mode='r', newline='') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        # Add a condition to check if the row should be updated
        if int(row['q_id'][1:]) >= 1:  # Process rows starting from q1
            problem_given = row['text']  # Extract the text field as the problem_given
            response = client.chat.completions.create(
                model="gpt-4o", 
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"<problem_given>\n{problem_given}\n</problem_given>"}
                ],
                temperature=0.1,
                max_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            # Use the model's output as data
            try:
                print(f"Processing Row {row['q_id']}")
                print(response.choices[0].message.content + "\n")
                data = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}, skipping row {row['q_id']}")
                continue  # Skip this row and move to the next one

            # Format the data into the desired text format
            formatted_text = ""
            for step in range(1, 5):
                step_key = f"Step{step}"
                formatted_text += f"Step {step}: {data[step_key]['Description']}\n{data[step_key]['Solution']}\n\n"

            # Update the solution field instead of example_problem
            row['solution'] = formatted_text
        rows.append(row)

# Write the updated data back to the CSV file
with open(csv_file_path, mode='w', newline='') as csv_file:
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("CSV file 'questions.csv' has been updated with new solutions.")
