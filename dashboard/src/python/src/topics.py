class Topics:
    def __init__(self, query, similar_topics):
        self.query = query
        self.similar_topics = TopicFactory.create_topic_dict(similar_topics)
    
    def update(self, query, similar_topics):
        if query == self.query:
            return False
        else:
            self.query = query
            self.similar_topics = TopicFactory.create_topic_dict(similar_topics)
        
    def any_solo(self):
        if any(t.solo for t in self.similar_topics.values()):
            return True
        else:
            False
    
    def get_solo(self):
        return [str(t) for t in self.similar_topics.values() if t.solo]

    def toggle_solo(self, topic_id):
        topics = self.get_solo()
        for t in topics:
            try:
                t.toggle_solo()
            except:
                pass
        self.similar_topics[str(topic_id)].toggle_solo()
    
    def remove_solo(self):
        for t in self.similar_topics.items():
            if t[1].solo:
                t[1].solo = False
        

    def get_selected_topics(self):
        if self.any_solo():
            return self.get_solo()
        return [t.topic_id for t in self.similar_topics.values() if t.selected]
    

    def select_topic(self, topic_id, choice):
        self.similar_topics[str(topic_id)].select(choice)

    #def convert_rank_to_id(self, rank):
    #    return [t.topic_id for t in self.similar_topics if t.rank == rank][0]
    
    def map_ids_to_rank(self):
        return {id:str(self.similar_topics[id].rank) for id in self.get_selected_topics()}
    
    def get_topic_by_rank(self,rank):
        return [t for t in self.similar_topics.values() if t.rank == rank][0]


class TopicFactory:
    @staticmethod
    def create_topic(topic_id):
        return Topic(topic_id)
    
    @staticmethod
    def create_topic_dict(topic_ids):
        res = {str(topic_id):TopicFactory.create_topic(topic_id) for topic_id in topic_ids}
        for i, topic in enumerate(topic_ids):
            res[str(topic)].rank = i+1
        return res

class Topic:
    def __init__(self, topic):
        self.topic_id = str(topic)
        self.selected = True
        self.solo = False
        self.rank = -1
    
    def __str__(self):
        return self.topic_id
    
    def select(self, choice):
        self.selected = choice

    def toggle_solo(self):
        self.solo = not self.solo
    
