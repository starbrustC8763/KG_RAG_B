from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

# 定義提示模板
prompt_template = PromptTemplate(
    input_variables=["reason"],
    template="""
請你幫我從以下車禍的事故發生緣由中提取所有原告和被告的名字或代稱(例如:甲○○,乙○○)，並判斷被告是否為未成年，是否為僱用人，以及車禍是否為動物造成，並只能以以下格式輸出:
原告:
被告:
被告是否為未成年:
被告是否為僱用人:
車禍是否為動物造成:
### 事故發生緣由：
{reason}
備註:
如果未提及原告或被告的姓名或代稱需判斷為未知
僱用人的定義是受雇於企業的人，如果未提及被告是否為受僱人需判斷為否
如果未提及被告年齡需判斷為被告不是未成年人，即否
如果未提及被告是否為僱用人需判斷為否
"""
)

def generate_filter(user_input):
    llm = OllamaLLM(model="kenneth85/llama-3-taiwan:8b-instruct-dpo",
                    temperature=0.1,
                    keep_alive=0,
                    )
    # 創建 LLMChain
    llm_chain = LLMChain(llm=llm, prompt=prompt_template)
    # 傳入數據生成起訴書
    filtered_input = llm_chain.run({
        "reason" : user_input
    })
    return filtered_input
user_input="""
text: "事故發生緣由：
被告徐金坤受僱於被告尤彰寶即典坤企業行擔任大貨車司機職務。於民國109年4月7日8時16分許，被告徐金坤駕駛車牌號碼000-00號營業用大貨車，在屏東縣○○鎮○○路000號旁倒車欲駛入南灣路面，被告徐金坤應注意汽車倒車時，應顯示倒車燈光或手勢後，謹慎緩慢後倒，並應注意其他車輛及行人，且大型汽車須派人在車後指引，如無人在車後指引時，應先測明車後有足夠之地位，並促使行人及車輛讓避，以避免危險或交通事故之發生。而依當時天候良好、日間自然光線、柏油路面缺陷、無障礙物、視距良好、無號誌等情況，無不能注意之情形，竟疏未注意車後方往來人車之動向且無人在後指揮，即貿然倒車，致撞擊車後之機車道上，由原告所騎乘516-ENL普通重型機車，致原告人車倒地。"
"""
print(generate_filter(user_input))