from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from input_filter import generate_filter
import numpy as np
import faiss
import os
from typing import List, Dict, Tuple, Any
from dotenv import load_dotenv

# 加載 .env 配置
load_dotenv()

# Neo4j 配置
uri = os.getenv("NEO4J_URI_B")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")
driver = GraphDatabase.driver(uri, auth=(username, password))

# 索引保存路徑
INDEX_PATH = "case_index_hnsw.faiss"

# 初始化嵌入模型
model = SentenceTransformer("shibing624/text2vec-base-chinese")

def build_faiss_index() -> Tuple[faiss.IndexHNSWFlat, List[str], List[str]]:
    """
    從 Neo4j 數據庫中構建 FAISS 索引並保存到磁盤。

    Returns:
        Tuple[faiss.IndexHNSWFlat, List[str], List[str]]: FAISS 索引，事實節點 ID 列表，事實文本列表。
    """
    with driver.session() as session:
        # 查詢所有 Fact 節點的 ID、文本和嵌入
        results = session.run("MATCH (f:案件屬性) RETURN f.case_id AS id, f.text AS text, f.embedding AS embedding")
        embeddings = []
        case_ids = []
        reason_texts = []
        
        for record in results:
            case_ids.append(record["id"])
            reason_texts.append(record["text"])
            embeddings.append(np.array(record["embedding"], dtype="float32"))

    # 構建 FAISS HNSW 索引
    dimension = len(embeddings[0])
    M = 32  # HNSW 的參數，決定連接數量
    index = faiss.IndexHNSWFlat(dimension, M)
    index.hnsw.efConstruction = 200  # 構建時的 ef 值
    index.hnsw.efSearch = 100  # 查詢時的 ef 值
    index.add(np.array(embeddings))  # 添加嵌入向量

    # 保存索引到磁盤
    faiss.write_index(index, INDEX_PATH)
    with open("case_metadata_hnsw.npy", "wb") as f:
        np.save(f, {"case_ids": case_ids, "reason_texts": reason_texts})
    
    return index, case_ids, reason_texts

def load_faiss_index() -> Tuple[faiss.IndexHNSWFlat, List[str], List[str]]:
    """
    加載 FAISS 索引和對應的元數據。如果索引不存在，則構建索引。

    Returns:
        Tuple[faiss.IndexHNSWFlat, List[str], List[str]]: FAISS 索引，事實節點 ID 列表，事實文本列表。
    """
    if os.path.exists(INDEX_PATH) and os.path.exists("case_metadata_hnsw.npy"):
        # 從磁盤加載索引
        index = faiss.read_index(INDEX_PATH)
        metadata = np.load("case_metadata_hnsw.npy", allow_pickle=True).item()
        return index, metadata["case_ids"], metadata["reason_texts"]
    else:
        # 索引不存在時構建索引
        return build_faiss_index()

def query_faiss(input_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    在 FAISS 索引中查詢最相似的案件。

    Args:
        input_text (str): 用戶輸入的文本。
        top_k (int): 返回的最相似事實數量。

    Returns:
        List[Dict[str, Any]]: 包含最相似事實的 ID、文本和距離的列表。
    """
    query_embedding = np.array([model.encode(input_text)], dtype="float32")
    index, fact_ids, fact_texts = load_faiss_index()
    distances, indices = index.search(query_embedding, top_k)
    results = []

    for dist, idx in zip(distances[0], indices[0]):
        results.append({
            "id": fact_ids[idx],
            "text": fact_texts[idx],
            "distance": dist
        })
    return results

def find_case_type_by_case_id(tx, case_id):
    query = (
        "MATCH (t:案件類型)-[:所屬案件]->(c:案件 {case_id: $case_id}) "
        "RETURN t.name AS case_type"
    )
    result = tx.run(query, case_id=case_id)
    record = result.single()
    if record:
        return record["case_type"]
    else:
        return None


def get_type_for_case(case_id):
    with driver.session() as session:
        case_type = session.execute_read(find_case_type_by_case_id, case_id)
        return case_type

def fetch_statutes_and_explanations(statutes: List[str]) -> List[Dict[str, str]]:
    """
    查詢指定法條的條文內容及其口語化解釋。

    Args:
        statutes (List[str]): 要查詢的法條 ID 列表。

    Returns:
        List[Dict[str, str]]: 包含法條 ID、條文和口語化解釋的字典列表。
    """
    query = """
    MATCH (s:Statute)-[:口語化解釋]->(e:Explanation)
    WHERE s.id IN $statutes
    RETURN s.id AS statute_id, s.text AS statute_text, e.text AS explanation_text
    """
    with driver.session() as session:
        results = session.run(query, statutes=statutes)
        return [
            {
                "statute_id": record["statute_id"],
                "statute_text": record["statute_text"],
                "explanation_text": record["explanation_text"]
            }
            for record in results
        ]

user_input="""
text: "事故發生緣由:
 原告於106年8月5日凌晨騎乘車牌號碼000-000號普通重型機車（下稱A車），沿臺北市松山區南京東路5段由西往東方向之第4車道行駛，因訴外人康家誠將車牌號碼000-0000號自用小客車（下稱C車）違規停放於同路段116號前紅線處，遮蔽原告視線，致無法看見斜停於C車前方王俊傑所駕駛且正在執行拖吊機車業務之車牌號碼000-0000號拖吊車（下稱B車）將車尾拖板起落架放下，且王俊傑亦未於車後適當位置設置警告標誌，導致原告行經C車後，始發現B車之起落架放置於原告行進路線上，不及閃避而發生擦撞（下稱系爭事故）。
 又王俊傑受僱於王俊楠即楠德車業工作室，而B車車身上漆有「TMS」字樣（即全鋒公司之英文名稱縮寫），且係因執行拖吊業務而發生系爭事故，王俊楠、全鋒公司均應分別就王俊傑之侵權行為負僱用人責任。"
"""
def get_case_type(user_input):
    score={"單純原被告各一":0,"數名原告":0,"數名被告":0,"原被告皆數名":0,"§187未成年案型":0,"§188僱用人案型":0,"§190動物案型":0}
    filtered_input = generate_filter(user_input)
    top_k=3
    l = query_faiss(filtered_input,top_k=top_k)
    for i in range(top_k):
        #print(f"id:{l[i]["id"]}")
        #print(f"text:{l[i]["text"]}")
        dist=l[i]["distance"]
        #print(f"dist:{dist}")
        case_type=get_type_for_case(l[i]["id"])
        print(f"type:{case_type}")
        score[case_type] += 300 - dist
    max_key = max(score, key=score.get)
    return max_key
#print(get_case_type(user_input))