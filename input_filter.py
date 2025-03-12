from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

# 定義提示模板
prompt_template = PromptTemplate(
    input_variables=["reason"],
    template="""
請你幫我從以下車禍的事故發生緣由中提取所有原告和被告的數量，並判斷被告是否為未成年，是否為僱用人，以及車禍是否為動物造成，並只能以以下格式輸出:
原告:x位
被告:y位
被告是否為未成年:是or否
被告是否為僱用人:是or否
車禍是否為動物造成:是or否
### 事故發生緣由：
{reason}
備註:
如果未提及原告或被告的姓名或代稱需寫為"一名"
僱用人的定義是受雇於企業的人
如果有明確提及被告是未成年人才可以判斷為是，沒有提及則一律判斷為否
如果有明確提及被告是某公司的僱用人才可以判斷為是，沒有提及則一律判斷為否
有明確指出車禍為動物造成才可以判斷為是，沒有提及則一律為否
"""
)

def generate_filter(user_input):
    llm = OllamaLLM(model="kenneth85/llama-3-taiwan:8b-instruct-dpo",
                    temperature=0,
                    keep_alive=0,
                    num_predict=700
                    )
    # 創建 LLMChain
    llm_chain = LLMChain(llm=llm, prompt=prompt_template)
    # 傳入數據生成起訴書
    filtered_input = llm_chain.run({
        "reason" : user_input
    })
    print(filtered_input)
    return filtered_input
#print(generate_filter(user_input))