import pandas as pd
from gensim.models import Word2Vec
import nltk
import tempfile
#nltk.download('punkt_tab')
#from helpers import preprocess_text

MODEL_PATH = '/home/telese/TETYS/pipeline/src/python/models/word2vec'


if __name__ == "__main__":
    #data = pd.read_csv('/home/telese/TETYS/pipeline/src/python/data/processed/16_dicembre/metadata_full_text.csv')
    # tokenize dataset
    #data['text'] = data['text'].apply(lambda x: nltk.word_tokenize(x))

    #texts = data.text.tolist()
    # fit model
    #model = Word2Vec(texts)
    # save model

    #model.save('/home/telese/TETYS/pipeline/src/python/models/fasttext/word2vec')

    ## prova word2vec
    model = Word2Vec.load("/home/telese/TETYS/pipeline/src/python/models/fasttext/word2vec")
    print(list(w for w in model.wv.index_to_key))
    print(model.wv.most_similar('trattato', topn=10))


