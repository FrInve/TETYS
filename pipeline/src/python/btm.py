from bertopic import BERTopic
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt

class BTM():

    def __init__(self,model_1,model_2,ids_1,texts_1,embeddings_1,texts_2,embeddings_2,model_1_name="Model_1",model_2_name="Model_2",percentile_threshold=0.05):

        self.model_1_name = model_1_name
        self.model_2_name = model_2_name
        self.model_1 = model_1
        self.model_2 = model_2
        self.ids_1 = ids_1
        self.texts_1 = texts_1
        self.embeddings_1 = embeddings_1
        self.embeddings_2 = embeddings_2
        self.texts_2 = texts_2
        self.percentile_threshold = percentile_threshold

        self.n_topics_model_1 = None
        self.topics_matrix = None
        self.topic_closeness = None
        self.topic_alignment = None
        self.corpus_closeness = None
        self.corpus_weighted_closeness = None
        self.corpus_uniqueness = None
        self.corpus_weighted_uniqueness = None
        self.corpus_alignment = None
        self.corpus_weighted_alignment = None
        self.cooccurence_matrix = None
        self.TH = None

        self.sanity_check()
        self.init()

    def sanity_check(self):
        if len(self.texts_1) != len(self.ids_1):
            raise ValueError("texts_1 and ids_1 must have the same length")

        if not isinstance(self.model_1, BERTopic):
            raise TypeError("model_1 must be an instance of BERTopic")

        if not isinstance(self.model_2, BERTopic):
            raise TypeError("model_2 must be an instance of BERTopic")

        for i, model in enumerate([self.model_1, self.model_2], start=1):
            if not hasattr(model, "topics_"):
                raise ValueError(f"model_{i} must be a fitted BERTopic model")

    def init(self):

        # Select the threshold to decide when consider documnets as outlier (5% confidence)
        topics_2 = np.array(self.model_2.topics_)
        
        _, sims_in = self.model_2.transform(self.texts_2, embeddings=self.embeddings_2)
        mask_incluster = (topics_2 != -1)
        sims_in_clean = sims_in[mask_incluster]
        self.TH = np.quantile(sims_in_clean, self.percentile_threshold) 

        print(f"Threshold:{self.TH}")
        # Cross topic
        topics, probabilty = self.model_2.transform(self.texts_1, embeddings=self.embeddings_1)

        
        topics_accepted = np.where(probabilty >= self.TH, topics, -1)

        if self.model_2.custom_labels_ == None:
            model_2_topic_dict = self.model_2.topic_labels_
        else:
            model_2_topic_dict = { idx:topic for idx, topic in enumerate(self.model_2.custom_labels_,start=-1) }

        model_2_topic_labels = [ model_2_topic_dict[topic] for topic in topics_accepted ]

        model_2_topics = pd.DataFrame({'id': self.ids_1,
                                       'Topic': topics_accepted,
                                       'Topic_label': model_2_topic_labels} )

        #model_2_topics = self.model_2.get_document_info(self.texts_2)[['Topic']]
        #model_2_topics['id'] = self.ids_2

        # Native Topic

        if self.model_1.custom_labels_ is None:
            columns_to_extract = ['Topic','Name']
        else:
            columns_to_extract = ['Topic','CustomName']


        model_1_topics =  self.model_1.get_document_info(self.texts_1)[columns_to_extract]
        model_1_topics['id'] = self.ids_1

        if self.model_1.custom_labels_ is None:
            model_1_topics = model_1_topics.rename(columns={'Name':'Topic_label'})
        else:
           model_1_topics = model_1_topics.rename(columns={'CustomName':'Topic_label'})

        
        #to remove
        no_out_index = model_1_topics[model_1_topics['Topic'] != -1 ].index 

        model_1_topics = model_1_topics[ model_1_topics.Topic != -1 ].copy()
        
        self.cooccurence_matrix = model_1_topics.merge(model_2_topics,on='id',suffixes=('_model_1','_model_2'))

        topics_couple = self.cooccurence_matrix[['Topic_model_1','Topic_model_2','Topic_label_model_1','Topic_label_model_2']].value_counts().rename('Couple_counts').reset_index()

        self.topics_matrix = topics_couple.merge(self.model_1.get_topic_info()[['Count','Topic']].rename(columns={'Topic':'Topic_model_1'}),on='Topic_model_1')

        self.n_topics_model_1 = model_1_topics['Topic'].nunique()

        
        probabilty = probabilty[ no_out_index ]
        print(f"{len(probabilty[probabilty < self.TH])}/{len(probabilty)} are classified as outlier due to their threshold values")

        pd.DataFrame({'topic_assigned_pre_filter': [ model_2_topic_dict[topic] for topic in topics[no_out_index] ],
                      'probability' : probabilty,
                      'text' : self.texts_1[no_out_index],
                      'id' : self.ids_1[no_out_index],
                      }).to_parquet(f'test_{self.model_1_name}_{self.model_2_name}.parquet')


    def evaluate_metrics(self):
        self.compute_topic_closeness_and_uniqueness()
        self.compute_topic_alignment()
        self.compute_corpus_closeness()
        self.compute_corpus_uniqueness()
        self.compute_corpus_alignment()

    def compute_topic_closeness_and_uniqueness(self):
        if self.topic_closeness is not None:
            return
        
        self.topic_closeness = self.topics_matrix.copy()
        self.topic_closeness['Closeness'] = self.topic_closeness['Couple_counts'] / self.topic_closeness['Count']

    def compute_topic_alignment(self):

        if self.topic_closeness is None:
            self.compute_topic_closeness_and_uniqueness()

        topic_closeness_without_outlier = self.topic_closeness[ self.topic_closeness.Topic_model_2 != -1 ].reset_index()
        self.topic_alignment = topic_closeness_without_outlier.groupby(['Topic_model_1','Topic_label_model_1','Count']).agg(Alignment=('Closeness','max')).reset_index()
        
    def compute_corpus_closeness(self):
        if self.topic_closeness is None:
            self.compute_topic_closeness_and_uniqueness()
        
        topic_closeness_without_outlier = self.topic_closeness[ self.topic_closeness.Topic_model_2 != -1 ].reset_index()

        self.corpus_closeness = topic_closeness_without_outlier.Closeness.sum() / (self.n_topics_model_1)

        x = topic_closeness_without_outlier.groupby(by=['Topic_model_1','Topic_label_model_1','Count']).agg({'Closeness':'sum'}).reset_index()
        x['Weigted'] = x['Count'] * x['Closeness']

        den = self.model_1.get_topic_info().query("Topic != -1")["Count"].sum()

        self.corpus_weighted_closeness = x['Weigted'].sum() / (den)
    
    def compute_corpus_uniqueness(self):
        if self.topic_closeness is None:
            self.compute_topic_closeness_and_uniqueness()

        only_outliers = self.topic_closeness[ (self.topic_closeness.Topic_model_2 == -1) ].reset_index()
        self.corpus_uniqueness = only_outliers.Closeness.sum() / self.n_topics_model_1

        only_outliers['Weighted'] = only_outliers['Closeness'] * only_outliers['Count']

        den = self.model_1.get_topic_info().query("Topic != -1")["Count"].sum()

        self.corpus_weighted_uniqueness = only_outliers['Weighted'].sum() / (den)

    def compute_corpus_alignment(self):
        if self.topic_alignment is None:
            self.compute_topic_alignment()

        # Questo lo fa su solo quelli che in realtà hanno almeno una corrisponza con un topic cross
        #self.corpus_alignment = self.topic_alignment.Alignment.mean()
        # Da paper dovrebbe essere rispetto al numero di topic
        self.corpus_alignment = self.topic_alignment.Alignment.sum() / self.n_topics_model_1

        self.topic_alignment['Weigth'] = self.topic_alignment['Count'] * self.topic_alignment['Alignment']
        
        den = self.model_1.get_topic_info().query("Topic != -1")["Count"].sum()

        self.corpus_weighted_alignment = self.topic_alignment['Weigth'].sum() / (den)

    def get_topic_closeness(self):
        if self.topic_closeness is None:
            self.compute_topic_closeness_and_uniqueness()
        return self.topic_closeness[ self.topic_closeness.Topic_model_2 != -1 ].rename(columns={"Topic_label_model_1":f"{self.model_1_name} Topic Label",
            "Topic_label_model_2":f"{self.model_2_name} Topic Label",
            "Topic_model_1":f"{self.model_1_name} Topic Id",
            "Topic_model_2":f"{self.model_2_name} Topic Id",
            "Closeness":f"Topic Closeness",
            "Couple_counts": "Total Couple matches",
            "Count":"Topic Corpus Occurrences"}
            ).copy()
    
    def get_topic_uniqueness(self):
        if self.topic_closeness is None:
            self.compute_topic_closeness_and_uniqueness()
        return self.topic_closeness[ self.topic_closeness.Topic_model_2 == -1 ][['Topic_label_model_1','Topic_model_1','Closeness']].rename(columns={"Topic_label_model_1":f"{self.model_1_name} Topic Label",
            "Topic_model_1":f"{self.model_1_name} Topic Id",
            "Closeness":f"Topic Uniqueness"},
            ).copy()
    
    def get_topic_alignment(self):
        if self.topic_alignment is None:
            self.compute_topic_alignment()
        return self.topic_alignment[['Topic_label_model_1','Topic_model_1','Alignment']].rename(columns={"Topic_label_model_1":f"{self.model_1_name} Topic Label",
            "Topic_model_1":f"{self.model_1_name} Topic Id",
            "Closeness":f"Topic Alignment"},
            ).copy()
    
    def get_corpus_closeness(self):
        if self.corpus_closeness is None:
            self.compute_corpus_closeness()
        return self.corpus_closeness
    
    def get_corpus_uniqueness(self):
        if self.corpus_uniqueness is None:
            self.compute_corpus_uniqueness()
        return self.corpus_uniqueness
    
    def get_corpus_alignment(self):
        if self.corpus_alignment is None:
            self.compute_corpus_alignment()
        return self.corpus_alignment
    
    def print_corpus_metrics(self):

        if self.corpus_closeness is None:
            self.compute_corpus_closeness()
        print(f'Evaluation: {self.model_1_name} -> {self.model_2_name}')
        print(f'Corpus Closeness: {self.corpus_closeness}')

        if self.corpus_uniqueness is None:
            self.compute_corpus_uniqueness()
        print(f'Evaluation: {self.model_1_name} -> {self.model_2_name}')
        print(f'Corpus Uniqueness: {self.corpus_uniqueness}')

        if self.corpus_alignment is None:
            self.compute_corpus_alignment()
        print(f'Evaluation: {self.model_1_name} -> {self.model_2_name}')
        print(f'Corpus Alignment: {self.corpus_alignment}')

    def print_weighted_corpus_metrics(self):

        if self.corpus_closeness is None:
            self.compute_corpus_closeness()
        print(f'Evaluation: {self.model_1_name} -> {self.model_2_name}')
        print(f'Corpus Closeness: {self.corpus_weighted_closeness}')

        if self.corpus_uniqueness is None:
            self.compute_corpus_uniqueness()
        print(f'Evaluation: {self.model_1_name} -> {self.model_2_name}')
        print(f'Corpus Uniqueness: {self.corpus_weighted_uniqueness}')

        if self.corpus_alignment is None:
            self.compute_corpus_alignment()
        print(f'Evaluation: {self.model_1_name} -> {self.model_2_name}')
        print(f'Corpus Alignment: {self.corpus_weighted_alignment}')


    def create_wordcloud(self, model, topic, ax, title=None):
        text = {word: value for word, value in model.get_topic(topic)}

        wc = WordCloud(
            background_color="white",
            max_words=1000,
            colormap='viridis', 
            relative_scaling=0.5,
            min_font_size=10
        ).generate_from_frequencies(text)

        wc_image = np.array(wc.to_image())

        ax.imshow(wc_image, interpolation="bilinear")
        ax.axis("off")

        if title:
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

    def compare_wordcloud_topics(self, topic_1, topic_2):

        if self.model_1.custom_labels_ == None:
            model_1_topic_dict = self.model_1.topic_labels_
        else:
            model_1_topic_dict = {idx: topic for idx, topic in enumerate(self.model_1.custom_labels_, start=-1)}

        if self.model_2.custom_labels_ == None:
            model_2_topic_dict = self.model_2.topic_labels_
        else:
            model_2_topic_dict = {idx: topic for idx, topic in enumerate(self.model_2.custom_labels_, start=-1)}

        assert (topic_2 in model_2_topic_dict.keys()), f"{topic_2} doesn't exist in model 2"
        assert (topic_1 in model_1_topic_dict.keys()), f"{topic_1} doesn't exist in model 1"

        
        fig = plt.figure(figsize=(16, 7))
        fig.patch.set_facecolor('#f8f9fa')  
        
        
        gs = fig.add_gridspec(1, 3, width_ratios=[1, 0.05, 1], wspace=0.05)
        
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 2])

        
        self.create_wordcloud(self.model_1, topic_1, ax1, title=model_1_topic_dict[topic_1])
        self.create_wordcloud(self.model_2, topic_2, ax2, title=model_2_topic_dict[topic_2])

        
        line_ax = fig.add_subplot(gs[0, 1])
        line_ax.axvline(x=0.5, color='#dee2e6', linewidth=3, linestyle='-')
        line_ax.set_xlim(0, 1)
        line_ax.set_ylim(0, 1)
        line_ax.axis('off')

        
        fig.suptitle(f'{self.model_1_name} ({topic_1}) vs {self.model_2_name} ({topic_2})', fontsize=20, fontweight='bold', y=0.98)

        plt.tight_layout()
        plt.show()


            
