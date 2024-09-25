import logging

import matplotlib.pyplot as plt
from bertopic import BERTopic
from wordcloud import WordCloud

GROUP=1

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
    logging.basicConfig(format='%(asctime)s | %(levelname)s:%(message)s',filename=f'./logs/group_{GROUP}/plots_02_08.log', encoding='utf-8', level=logging.INFO)
    logging.info('Started...')
    topic_model = BERTopic.load(f'./models/group_{GROUP}/model_group_1_dbcv_0_44', embedding_model="sentence-transformers/allenai-specter"
)
    logging.info('Model loaded')
    root_path = f'./reports/group_{GROUP}/2024-08-02/'
    print(len(topic_model.topics_))
    for topic_i in range(-1,29):
        create_and_save_wordcloud(topic_model, topic_i, root_path+'wc_'+str(topic_i)+'.png')
        logging.info(f'Generated wordcloud for topic {topic_i}')
