import pandas as pd
from KG_Faiss_Query import get_case_type
import re
df = pd.read_excel("data.xlsx")
case_id = 1
score = 0
for index, row in df.iterrows():
    sim_input = row[1]
    match = re.search(r'一、(.*?)二、(.*?)三、(.*)', sim_input, re.S)
    user_input = match.group(1).strip()
    case_type = get_case_type(user_input)
    if case_type == row[0]:
        score += 1
    with open("test_result.txt", "a", encoding="utf-8") as f:
        f.write(f"{case_type}\n")
    case_id += 1
print(f"正確率{score/49}")