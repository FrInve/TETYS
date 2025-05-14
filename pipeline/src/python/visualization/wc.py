import logging

import matplotlib.pyplot as plt
from bertopic import BERTopic
from wordcloud import WordCloud


def create_wordcloud(topic_model, topic):
    text = {word: value for word, value in topic_model.get_topic(topic)}
    wc = WordCloud(background_color="black", max_words=1000)
    wc.generate_from_frequencies(text)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()

def create_and_save_wordcloud(topic_model, topic,save_path):
    text = {word: value for word, value in topic_model.get_topic(topic)}
    wc = WordCloud(background_color="black", max_words=1000, width=1600, height=800)
    wc.generate_from_frequencies(text)
    plt.figure(figsize=(20,10))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(save_path)


if __name__ == '__main__':
    #logging.basicConfig(format='%(asctime)s | %(levelname)s:%(message)s',filename='./logs/plots.log', encoding='utf-8', level=logging.INFO)
    #logging.info('Started...')
    topic_model = BERTopic.load('/home/telese/TETYS/pipeline/src/python/models/tuning/30_marzo_fulltext/model_0.403241194641185.safetensors', embedding_model="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)
    #logging.info('Model loaded')
    root_path = 'plots/'
    for topic_i in range(2,12):
        create_and_save_wordcloud(topic_model, topic_i, root_path+'wc_'+str(topic_i)+'.png')
        logging.info(f'Generated wordcloud for topic {topic_i}')
