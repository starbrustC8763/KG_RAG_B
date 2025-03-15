import re

def get_case_type(case_info):
    # 分割姓名列表
    # 正則表達式提取原告和被告姓名
    pattern = r"原告:([\u4e00-\u9fa5A-Za-z0-9○·．,、]+)"
    plaintiff_match = re.search(pattern, case_info)
    pattern = r"被告:([\u4e00-\u9fa5A-Za-z0-9○·．,、]+)"
    defendant_match = re.search(pattern, case_info)

    plaintiffs = re.split(r"[,、]", plaintiff_match.group(1)) if plaintiff_match else []
    defendants = re.split(r"[,、]", defendant_match.group(1)) if defendant_match else []

    # 去除空格
    plaintiffs = [name.strip() for name in plaintiffs]
    defendants = [name.strip() for name in defendants]

    print("原告:", plaintiffs)
    print("被告:", defendants)

    case_type=""
    p=len(plaintiffs)
    d=len(defendants)
    if p<=1 and d<=1:
        case_type="單純原被告各一"
    elif p>1 and d<=1:
        case_type="數名原告"
    elif p<=1 and d>1:
        case_type="數名被告"
    elif p>1 and d>1:
        case_type="原被告皆數名"

    match = re.search(r'被告是否為未成年人(.*?)被告是否為受僱人(.*?)車禍是否由動物造成(.*)', case_info, re.S)

    if match.group(1).strip()[1] =="是":
        case_type += "+§187未成年案型"
        return case_type
    if match.group(2).strip()[1] =="是":
        case_type += "+§188僱用人案型"
        return case_type
    if match.group(3).strip()[1] =="是":
        case_type += "+§190動物案型"
        return case_type
    
    return case_type
