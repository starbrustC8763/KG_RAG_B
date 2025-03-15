import pandas as pd
from define_case_type import generate_case_type
import re
df = pd.read_excel("data.xlsx")
case_id = 1
score = 0
for index, row in df.iterrows():
    sim_input = row.iloc[1]
    match = re.search(r'一、(.*?)二、(.*?)三、(.*)', sim_input, re.S)
    user_input = match.group(1).strip()
    case_type = generate_case_type(user_input)
    with open("test_result.txt", "a", encoding="utf-8") as f:
        f.write(f"{case_type}\n")
    if case_type == row.iloc[0]:
        score += 1
    case_id += 1
print(f"正確率:{score/49}")