from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from input_filter import generate_filter
import re

llm = OllamaLLM(model="kenneth85/llama-3-taiwan:8b-instruct-dpo-q8_0",
                    temperature=0,
                    keep_alive=0,
                    )

def generate_case_type(user_input):
    prompt_template = PromptTemplate(
        input_variables=["info"],
        template="""
        請你幫我從以下的車禍案件中的原告和被告人數判斷這筆案件是屬於:"單純原被告各一","數名原告","數名被告","原被告皆數名"
        輸出格式:
        依照你判斷的結果輸出
        單純原被告各一,數名原告,數名被告,原被告皆數名 其中之一
        以下是本起車禍的事故訊息：
        {info}
        備註:
        "單純原被告各一"定義為:原告被告各只有一位
        "數名原告"定義為:原告大於一位，被告只有一位
        "數名被告"定義為:原告只有一位，被告大於一位
        "原被告皆數名"定義為:原告和被告皆為數名
        如果原告或被告欄位只寫了一個未提及則判斷為只有一位
        你只需要輸出這筆案件是屬於什麼類型，請不要輸出其他多餘的內容
        """
    )
    llm_chain = LLMChain(llm=llm, prompt=prompt_template)
    # 傳入數據生成起訴書
    case_info = generate_filter(user_input)
    match = re.search(r'被告是否為未成年人(.*?)被告是否為受僱人(.*?)車禍是否由動物造成(.*)', case_info, re.S)

    if match.group(1).strip()[1] =="是":
        case_type = "§187未成年案型"
        return case_type
    if match.group(2).strip()[1] =="是":
        case_type = "§188僱用人案型"
        return case_type
    if match.group(3).strip()[1] =="是":
        case_type = "§190動物案型"
        return case_type

    case_type = llm_chain.run({
        "info" : case_info
    })
    
    #print(filtered_input)
    return case_type