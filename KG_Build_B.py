from neo4j import GraphDatabase
from dotenv import load_dotenv
import pandas as pd
import os

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
def create_case_node(tx, sim_input, sim_output):
    tx.run("CREATE (c:案件 {模擬輸入: $sim_input, 模擬輸出: $sim_output})",
           sim_input=sim_input, sim_output=sim_output)
    print(f"建立案件節點，屬性 - 模擬輸入: {sim_input}，模擬輸出: {sim_output}")

# 將 案件 節點連結到對應的 案件類型 節點
def link_case_to_case_type(tx, case_type, sim_input, sim_output):
    tx.run(
        "MATCH (t:案件類型 {name: $case_type}), (c:案件 {模擬輸入: $sim_input, 模擬輸出: $sim_output}) "
        "MERGE (t)-[:所屬案件]->(c)",
        case_type=case_type, sim_input=sim_input, sim_output=sim_output
    )
    print(f"連結案件節點到案件類型節點：{case_type}")

# 建立或合併 模擬輸入 節點
def merge_sim_input(tx, sim_input):
    tx.run("MERGE (in:模擬輸入 {value: $sim_input})", sim_input=sim_input)
    print(f"建立或合併模擬輸入節點：{sim_input}")

# 建立或合併 模擬輸出 節點
def merge_sim_output(tx, sim_output):
    tx.run("MERGE (out:模擬輸出 {value: $sim_output})", sim_output=sim_output)
    print(f"建立或合併模擬輸出節點：{sim_output}")

# 將 模擬輸入 節點連結到 案件 節點
def link_sim_input_to_case(tx, sim_input, sim_output):
    tx.run(
        "MATCH (c:案件 {模擬輸入: $sim_input, 模擬輸出: $sim_output}), "
        "(in:模擬輸入 {value: $sim_input}) "
        "MERGE (in)-[:屬於]->(c)",
        sim_input=sim_input, sim_output=sim_output
    )
    print("連結模擬輸入節點到案件節點")

# 將 模擬輸出 節點連結到 案件 節點
def link_sim_output_to_case(tx, sim_input, sim_output):
    tx.run(
        "MATCH (c:案件 {模擬輸入: $sim_input, 模擬輸出: $sim_output}), "
        "(out:模擬輸出 {value: $sim_output}) "
        "MERGE (out)-[:屬於]->(c)",
        sim_input=sim_input, sim_output=sim_output
    )
    print("連結模擬輸出節點到案件節點")


# 函數：根據試算表中的資料建立節點與關係
def create_case_data(tx, case_type, sim_input, sim_output):
    merge_case_type(tx, case_type)
    create_case_node(tx, sim_input, sim_output)
    link_case_to_case_type(tx, case_type, sim_input, sim_output)
    merge_sim_input(tx, sim_input)
    merge_sim_output(tx, sim_output)
    link_sim_input_to_case(tx, sim_input, sim_output)
    link_sim_output_to_case(tx, sim_input, sim_output)

def delete_all_nodes(tx):
    tx.run("MATCH (n) DETACH DELETE n")
    print("Delete All Node")

if __name__ == "__main__":
    # 載入 Excel 檔案，假設檔案中有欄位名稱：案件類型、模擬輸入、模擬輸出
    df = pd.read_excel("data.xlsx")  # 請將 your_file.xlsx 換成你的檔案名稱
    with driver.session() as session:
        session.execute_write(delete_all_nodes)
    # 使用 Neo4j session 逐筆將資料寫入資料庫
    with driver.session() as session:
        for index, row in df.iterrows():
            case_type = row[0]
            sim_input = row[1]
            sim_output = row[2]
            session.execute_write(create_case_data, case_type, sim_input, sim_output)
            
    driver.close()
