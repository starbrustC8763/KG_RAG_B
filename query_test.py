import pandas as pd
from get_closest_case import get_closest_case
df = pd.read_excel("data_50.xlsx")
for index, row in df.iterrows():
    sim_input = row.iloc[0]
    cases=get_closest_case(sim_input)
    ids=[]
    for case in cases:
        ids.append(case["id"])
    with open("test_result.txt", "a", encoding="utf-8") as f:
        f.write(f"{ids}\n")
