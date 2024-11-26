PROMPT_QA = """
Suppose you are a professor teaching intro-undergrad-level physics. 
The student is struggling with a question. 
The picture (if there is) shows how he is currently solving the question. He asks "{std_msg}". 
We designed several hints for this question. Which one is most related to student's confusion? 
{hints}
Response in the following json format: 
{{"hint_idx": #, "response": answer the student's question in a simple and direct way}}
"""