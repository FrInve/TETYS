from bertopic import BERTopic
import pandas as pd

class BTM():

    def __init__(self,model_1,model_2,ids_1,texts_1,embeddings_1):

        self.model_1 = model_1
        self.model_2 = model_2
        self.ids_1 = ids_1
        self.texts_1 = texts_1
        self.embeddings_1 = embeddings_1

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

        # Cross topic
        topics, _ = self.model_2.transform(self.texts_1, embeddings=self.embeddings_1)
        model_2_topics = pd.DataFrame({'id': self.ids_1,
                                       'Topic': topics} )

        #model_2_topics = self.model_2.get_document_info(self.texts_2)[['Topic']]
        #model_2_topics['id'] = self.ids_2

        # Native Topic
        model_1_topics =  self.model_1.get_document_info(self.texts_1)[['Topic']]
        model_1_topics['id'] = self.ids_1

        model_1_topics = model_1_topics[ model_1_topics.Topic != -1 ].copy()
        
        self.cooccurence_matrix = model_1_topics.merge(model_2_topics,on='id',suffixes=('_model_1','_model_2'))

        topics_couple = self.cooccurence_matrix[['Topic_model_1','Topic_model_2']].value_counts().rename('Couple_counts').reset_index()

        self.topics_matrix = topics_couple.merge(self.model_1.get_topic_info()[['Count','Topic']].rename(columns={'Topic':'Topic_model_1'}),on='Topic_model_1')

        self.n_topics_model_1 = model_1_topics['Topic'].nunique()


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
        self.topic_alignment = topic_closeness_without_outlier.groupby(['Topic_model_1','Count']).agg(Alignment=('Closeness','max')).reset_index()
        
    def compute_corpus_closeness(self):
        if self.topic_closeness is None:
            self.compute_topic_closeness_and_uniqueness()
        
        topic_closeness_without_outlier = self.topic_closeness[ self.topic_closeness.Topic_model_2 != -1 ].reset_index()

        self.corpus_closeness = topic_closeness_without_outlier.Closeness.sum() / (self.n_topics_model_1)

        x = topic_closeness_without_outlier.groupby(by=['Topic_model_1','Count']).agg({'Closeness':'sum'}).reset_index()
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
        return self.topic_closeness[ self.topic_closeness.Topic_model_2 != -1 ].copy()
    
    def get_topic_uniqueness(self):
        if self.topic_closeness is None:
            self.compute_topic_closeness_and_uniqueness()
        return self.topic_closeness[ self.topic_closeness.Topic_model_2 == -1 ].copy()
    
    def get_topic_alignment(self):
        if self.topic_alignment is None:
            self.compute_topic_alignment()
        return self.topic_alignment.copy()
    
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
        print(f'Corpus Closeness: {self.corpus_closeness}')

        if self.corpus_uniqueness is None:
            self.compute_corpus_uniqueness()
        print(f'Corpus Uniqueness: {self.corpus_uniqueness}')

        if self.corpus_alignment is None:
            self.compute_corpus_alignment()
        print(f'Corpus Alignment: {self.corpus_alignment}')

    def print_weighted_corpus_metrics(self):

        if self.corpus_closeness is None:
            self.compute_corpus_closeness()
        print(f'Corpus Closeness: {self.corpus_weighted_closeness}')

        if self.corpus_uniqueness is None:
            self.compute_corpus_uniqueness()
        print(f'Corpus Uniqueness: {self.corpus_weighted_uniqueness}')

        if self.corpus_alignment is None:
            self.compute_corpus_alignment()
        print(f'Corpus Alignment: {self.corpus_weighted_alignment}')

        
        
        