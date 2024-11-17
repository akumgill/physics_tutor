import json
import os
from openai import OpenAI
import csv

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Read the existing CSV file and update each row
csv_file_path = 'questions.csv'
rows = []

# Read the existing data
with open(csv_file_path, mode='r', newline='') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        problem_given = row['text']  # Extract the text field as the problem_given

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are an experienced physics teacher. Your task is to provide a similar physics problem with the same known and unknown variables as the problem given, but with different numbers and a different setting, as well as a solution in 4 steps: \nUnderstand Problem\nSplit into Components\nApply Relevant Equations\nPerform algebra and arithmetic\n\nPlease use LaTeX wrappers to wrap math expressions in the solutions. \nYou may use multiple lines separated by a line break \\n in your solution for clarity. \n\nPlease answer in the JSON format below, only provide a single JSON object, no markdown code fence:\n\n{\n  \"Problem\": \"problem\",\n  \"Step1\": {\n    \"Description\": \"Understand Problem\",\n    \"Solution\": \"solution\"\n  },\n  \"Step2\": {\n    \"Description\": \"Split into Components\",\n    \"Solution\": \"solution\"\n  },\n  \"Step3\": {\n    \"Description\": \"Apply Relevant Equations\",\n    \"Solution\": \"solution\"\n  },\n  \"Step4\": {\n    \"Description\": \"Perform algebra and arithmetic\",\n    \"Solution\": \"solution\"\n  }\n}"
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "text": f"<problem_given>\n{problem_given}\n<\\problem_given>",
                            "type": "text"
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "text"
            }
        )

        # Use the model's output as data
        try:
            print(f"Row {row['q_id']}")
            print(response.choices[0].message.content + "\n")
            data = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}, skipping row {row['q_id']}")
            continue  # Skip this row and move to the next one

        # Format the data into the desired text format
        formatted_text = f"Problem: {data['Problem']}\n\n"
        for step in range(1, 5):
            step_key = f"Step{step}"
            formatted_text += f"Step {step}: {data[step_key]['Description']}\n{data[step_key]['Solution']}\n\n"

        # Update the specific field
        row['example_problem'] = formatted_text
        rows.append(row)

# Write the updated data back to the CSV file
with open(csv_file_path, mode='w', newline='') as csv_file:
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("CSV file 'questions.csv' has been updated with new example_problems.")
