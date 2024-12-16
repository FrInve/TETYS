import pandas as pd
import fasttext
import nltk
import tempfile
#nltk.download('punkt_tab')
#from helpers import preprocess_text

MODEL_PATH = '/home/telese/TETYS/pipeline/src/python/models/word2vec'


if __name__ == "__main__":
    data = pd.read_csv('/home/telese/TETYS/pipeline/src/python/data/processed/16_dicembre/metadata_full_text.csv')
    # tokenize dataset
    data['text'] = data['text'].apply(lambda x: nltk.word_tokenize(x))

    texts = data.text.tolist()
    # fit model
    model = fasttext.train_unsupervised(texts)
    # save model

    with tempfile.NamedTemporaryFile(prefix='saved_model_gensim-', delete=False) as tmp:
        model.save(tmp.name, separately=[])


