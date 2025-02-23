from neo4j import GraphDatabase
from dotenv import load_dotenv
import pandas as pd
import os

# 載入 .env 檔案中的環境變數
load_dotenv()

# 連接到 Neo4j 資料庫，請確保 .env 中定義了 NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(uri, auth=(username, password))

# 函數：根據試算表中的資料建立節點與關係
def create_case_data(tx, case_type, sim_input, sim_output):
    # 建立或合併 案件類型 節點
    tx.run("MERGE (t:案件類型 {name: $case_type})", case_type=case_type)
    
    # 建立 案件 節點，並存入模擬輸入與模擬輸出作屬性
    tx.run("CREATE (c:案件 {模擬輸入: $sim_input, 模擬輸出: $sim_output})", 
           sim_input=sim_input, sim_output=sim_output)
    
    # 將 案件 節點連結到對應的 案件類型 節點
    tx.run(
        "MATCH (t:案件類型 {name: $case_type}), (c:案件 {模擬輸入: $sim_input, 模擬輸出: $sim_output}) "
        "MERGE (t)-[:所屬案件]->(c)",
        case_type=case_type, sim_input=sim_input, sim_output=sim_output
    )
    
    # 如果需要對模擬輸入和模擬輸出建立獨立節點，可使用下列範例：
    tx.run("MERGE (in:模擬輸入 {value: $sim_input})", sim_input=sim_input)
    tx.run("MERGE (out:模擬輸出 {value: $sim_output})", sim_output=sim_output)
    tx.run(
        "MATCH (c:案件 {模擬輸入: $sim_input, 模擬輸出: $sim_output}), "
        "(in:模擬輸入 {value: $sim_input}) "
        "MERGE (in)-[:屬於]->(c)",
        sim_input=sim_input, sim_output=sim_output
    )
    tx.run(
        "MATCH (c:案件 {模擬輸入: $sim_input, 模擬輸出: $sim_output}), "
        "(out:模擬輸出 {value: $sim_output}) "
        "MERGE (out)-[:屬於]->(c)",
        sim_input=sim_input, sim_output=sim_output
    )

if __name__ == "__main__":
    # 載入 Excel 檔案，假設檔案中有欄位名稱：案件類型、模擬輸入、模擬輸出
    df = pd.read_excel("DATA.xlsx")  # 請將 your_file.xlsx 換成你的檔案名稱

    # 使用 Neo4j session 逐筆將資料寫入資料庫
    with driver.session() as session:
        for index, row in df.iterrows():
            case_type = row["案件類型"]
            sim_input = row["模擬輸入"]
            sim_output = row["模擬輸出"]
            session.write_transaction(create_case_data, case_type, sim_input, sim_output)
            
    driver.close()
