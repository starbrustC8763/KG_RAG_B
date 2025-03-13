from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

def generate_filter(user_input):
    filted=get_people(user_input)+"\n"+get_187(user_input)+"\n"+get_188(user_input)+"\n"+get_190(user_input)+"\n"
    return filted

def get_187(user_input):
    llm = OllamaLLM(model="kenneth85/llama-3-taiwan:8b-instruct-dpo",
                    temperature=0,
                    keep_alive=0,
                    )
    # 創建 LLMChain
    # 定義提示模板
    prompt_template = PromptTemplate(
        input_variables=["reason"],
        template="""
    請你幫我從以下車禍案件的事故詳情中判斷被告是否為未成年人，並只能用以下格式輸出:
    被告是否為未成年人:(是/否)

    以下是本起車禍的事故詳情：
    {reason}
    備註:
    如果未提及被告的年齡就判斷為否
    你只需要告訴我被告是不是未成年人，請依照格式輸出，不要輸出其他多餘的內容
    """
    )
    llm_chain = LLMChain(llm=llm, prompt=prompt_template)
    # 傳入數據生成起訴書
    filtered_input = llm_chain.run({
        "reason" : user_input
    })
    #print(filtered_input)
    return filtered_input

def get_188(user_input):
    llm = OllamaLLM(model="kenneth85/llama-3-taiwan:8b-instruct-dpo",
                    temperature=0,
                    keep_alive=0,
                    )
    # 創建 LLMChain
    # 定義提示模板
    prompt_template = PromptTemplate(
        input_variables=["reason"],
        template="""
    請你幫我從以下車禍案件的事故詳情中判斷被告在車禍發生時是否為正在執行職務的受僱人，並只能用以下格式輸出:
    被告是否為受僱人:(是/否)

    以下是本起車禍的事故詳情：
    {reason}
    備註:
    如果未提及被告是否為正在執行職務的受僱人就判斷為否
    你只需要告訴我被告是不是受僱人，請依照格式輸出，不要輸出其他多餘的內容
    輸出時記得按照格式在是或否前加上:"被告是否為受僱人:"
    """
    )
    llm_chain = LLMChain(llm=llm, prompt=prompt_template)
    # 傳入數據生成起訴書
    filtered_input = llm_chain.run({
        "reason" : user_input
    })
    #print(filtered_input)
    return filtered_input

def get_190(user_input):
    llm = OllamaLLM(model="kenneth85/llama-3-taiwan:8b-instruct-dpo",
                    temperature=0,
                    keep_alive=0,
                    )
    # 創建 LLMChain
    # 定義提示模板
    prompt_template = PromptTemplate(
        input_variables=["reason"],
        template="""
    請你幫我從以下車禍案件的事故詳情中判斷車禍是否由動物造成，並只能用以下格式輸出:
    車禍是否由動物造成:(是/否)

    以下是本起車禍的事故詳情：
    {reason}
    備註:
    如果未提及車禍是否由動物造成就判斷為否
    你只需要告訴我車禍是否由動物造成，請依照格式輸出，不要輸出其他多餘的內容
    """
    )
    llm_chain = LLMChain(llm=llm, prompt=prompt_template)
    # 傳入數據生成起訴書
    filtered_input = llm_chain.run({
        "reason" : user_input
    })
    #print(filtered_input)
    return filtered_input

def get_people(user_input):
    llm = OllamaLLM(model="kenneth85/llama-3-taiwan:8b-instruct-dpo",
                    temperature=0,
                    keep_alive=0,
                    )
    # 創建 LLMChain
    # 定義提示模板
    prompt_template = PromptTemplate(
        input_variables=["reason"],
        template="""
    請你幫我從以下車禍案件的事故詳情中提取並列出所有原告和被告的姓名，並只能用以下格式輸出:
    原告:
    被告:

    以下是本起車禍的事故詳情：
    {reason}
    備註:
    如果未提及原告或被告的姓名或代稱需寫為"未提及"
    你只需要列出原告和被告的姓名，請不要輸出其他多餘的內容
    """
    )
    llm_chain = LLMChain(llm=llm, prompt=prompt_template)
    # 傳入數據生成起訴書
    filtered_input = llm_chain.run({
        "reason" : user_input
    })
    #print(filtered_input)
    return filtered_input
#print(generate_filter(user_input))