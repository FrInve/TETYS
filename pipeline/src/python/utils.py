import datetime as dt
import re

def df_info(f):
    def wrapper(df, *args, **kwargs):
        tic = dt.datetime.now()
        result = f(df, *args, **kwargs)
        toc = dt.datetime.now()
        print("\n\n{} took {} time\n".format(f.__name__, toc - tic))
        print("After applying {}\n".format(f.__name__))
        print("Shape of df = {}\n".format(result.shape))
        print("Columns of df are {}\n".format(result.columns))
        print("Index of df is {}\n".format(result.index))
        for i in range(100): print("-", end='')
        return result
    return wrapper


def preprocess_text(text):
    # Virus nomenclature: A(H7N9) → AH7N9
    text = re.sub(r'[\(\)\[\]\{\}]', ' ', text)
    text = re.sub(r"[.,]", " ", text)

    
    # Removes percentage, symbols and number
    text = re.sub(r'\d+[\.,]?\d*\s*%', '', text)  
    text = re.sub(r'>\s*\d+', '', text)           
    text = re.sub(r'\d+\/\d+','',text)

    text = re.sub(r'(?<!\w)-|-(?!\w)', '', text)

    # Remove references such as [1,2] and (Smith et al., 2020)
    text = re.sub(r'\[\d+(?:,\d+)*\]', '', text)
    text = re.sub(r'\([A-Z][a-z]+\s+et\s+al\.,?\s+\d{4}\)', '', text)

    return text
