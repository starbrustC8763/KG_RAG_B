from neo4j import GraphDatabase
from dotenv import load_dotenv
import pandas as pd
import os
import re
# 載入 .env 檔案中的環境變數
load_dotenv()

# 連接到 Neo4j 資料庫，請確保 .env 中定義了 NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
uri = os.getenv("NEO4J_URI_B")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(uri, auth=(username, password))

# 建立或合併 案件類型 節點
def merge_case_type(tx, case_type):
    tx.run("MERGE (t:案件類型 {name: $case_type})", case_type=case_type)
    print(f"建立或合併案件類型節點：{case_type}")

# 建立 案件 節點，並存入模擬輸入與模擬輸出作屬性
def create_case_node(tx, case_id):
    tx.run("CREATE (c:案件 {case_id: $case_id})",
           case_id = case_id)
    print(f"建立案件節點，ID:{case_id}")

# 將 案件 節點連結到對應的 案件類型 節點
def link_case_to_case_type(tx, case_type, case_id):
    tx.run(
        "MATCH (t:案件類型 {name: $case_type}), (c:案件 {case_id: $case_id}) "
        "MERGE (t)-[:所屬案件]->(c)",
        case_type=case_type, case_id = case_id
    )
    print(f"連結案件{case_id}節點到案件類型節點：{case_type}")

# 建立或合併 模擬輸入 節點
def merge_sim_input(tx, sim_input, case_id):
    tx.run("MERGE (in:模擬輸入 {text: $sim_input,case_id: $case_id})", sim_input=sim_input, case_id = case_id)
    print(f"建立或合併模擬輸入節點：{sim_input}")

# 建立或合併 模擬輸出 節點
def merge_sim_output(tx, sim_output, case_id):
    tx.run("MERGE (out:模擬輸出 {text: $sim_output,case_id: $case_id})", sim_output=sim_output, case_id = case_id)
    print(f"建立或合併模擬輸出節點：{sim_output}")

# 將 模擬輸入 節點連結到 案件 節點
def link_sim_input_to_case(tx, sim_input, case_id):
    tx.run(
        "MATCH (c:案件 {case_id: $case_id}), "
        "(in:模擬輸入 {text: $sim_input,case_id: $case_id}) "
        "MERGE (in)-[:屬於]->(c)",
        sim_input=sim_input, case_id = case_id
    )
    print("連結模擬輸入節點到案件節點")

# 將 模擬輸出 節點連結到 案件 節點
def link_sim_output_to_case(tx, sim_output, case_id):
    tx.run(
        "MATCH (c:案件 {case_id: $case_id}), "
        "(out:模擬輸出 {text: $sim_output,case_id: $case_id}) "
        "MERGE (out)-[:屬於]->(c)",
        sim_output=sim_output, case_id = case_id
    )
    print("連結模擬輸出節點到案件節點")

#將解析後的模擬輸入部分建立成子節點，並與原模擬輸入節點連結
def create_sim_input_parts(tx, sim_input_value, parts_list, case_id):
    # 依序建立每個子節點，並用「包含」關係連接到模擬輸入節點
    for idx, part in enumerate(parts_list, start=1):
        tx.run(
            "CREATE (p:模擬輸入子 {text: $part, part_index: $idx, case_id: $case_id})",
            part=part, idx=idx, case_id = case_id
        )
        print(f"建立模擬輸入子節點：value={part}, part_index={idx}")
        tx.run(
            "MATCH (m:模擬輸入 {text: $sim_input_value,case_id: $case_id}), (p:模擬輸入子 {text: $part, part_index: $idx,case_id: $case_id}) "
            "MERGE (m)-[:包含]->(p)",
            sim_input_value=sim_input_value, part=part, idx=idx, case_id = case_id
        )
        print(f"連接模擬輸入節點 {sim_input_value} 與子節點 (value={part}, part_index={idx})")

def create_sim_output_parts(tx, sim_output_value, parts_list, case_id):
    # 建立每個模擬輸出子節點並連接到原節點
    for idx, part in enumerate(parts_list, start=1):
        tx.run(
            "CREATE (p:模擬輸出子 {text: $part, part_index: $idx, case_id: $case_id})",
            part=part, idx=idx, case_id = case_id
        )
        print(f"建立模擬輸出子節點：value={part}, part_index={idx}")
        tx.run(
            "MATCH (m:模擬輸出 {text: $sim_output_value, case_id: $case_id}), (p:模擬輸出子 {text: $part, part_index: $idx, case_id: $case_id}) "
            "MERGE (m)-[:包含]->(p)",
            sim_output_value=sim_output_value, part=part, idx=idx, case_id = case_id
        )
        print(f"連接模擬輸出節點 {sim_output_value} 與子節點 (value={part}, part_index={idx})")

# 函數：根據試算表中的資料建立節點與關係
def create_case_data(tx, case_type, sim_input, sim_output, case_id):
    merge_case_type(tx, case_type)
    create_case_node(tx, case_id)
    link_case_to_case_type(tx, case_type, case_id)
    merge_sim_input(tx, sim_input, case_id)
    merge_sim_output(tx, sim_output, case_id)
    link_sim_input_to_case(tx, sim_input, case_id)
    link_sim_output_to_case(tx, sim_output, case_id)
    # 解析模擬輸入並建立子節點
    input_parts = parse_sim_input(sim_input)
    create_sim_input_parts(tx, sim_input, input_parts, case_id)
    output_parts = parse_sim_output(sim_output)
    create_sim_output_parts(tx, sim_output, output_parts, case_id)

def delete_all_nodes(tx):
    tx.run("MATCH (n) DETACH DELETE n")
    print("Delete All Node")

def parse_sim_input(sim_input):
    match = re.search(r'一、(.*?)二、(.*?)三、(.*)', sim_input, re.S)
    parsed_input=[match.group(1).strip(),match.group(2).strip(),match.group(3).strip()]
    return parsed_input

def parse_sim_output(sim_output):
    match = re.search(r'一、(.*?)二、(.*?)（一）(.*)', sim_output, re.S)
    comp_match = match.group(3).strip()
    comp_match="（一）"+comp_match
    parsed_input=[match.group(1).strip(),match.group(2).strip(),comp_match]
    return parsed_input

if __name__ == "__main__":
    # 載入 Excel 檔案，假設檔案中有欄位名稱：案件類型、模擬輸入、模擬輸出
    df = pd.read_excel("data.xlsx")  # 請將 your_file.xlsx 換成你的檔案名稱
    # 使用 Neo4j session 逐筆將資料寫入資料庫
    with driver.session() as session:
        session.execute_write(delete_all_nodes)
        case_id = 1
        for index, row in df.iterrows():
            case_type = row[0]
            sim_input = row[1]
            sim_output = row[2]
            session.execute_write(create_case_data, case_type, sim_input, sim_output, case_id)
            case_id += 1
            
    driver.close()
