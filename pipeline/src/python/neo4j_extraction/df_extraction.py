import pandas as pd
from graphdatascience import GraphDataScience

driver = GraphDataScience("bolt://localhost:47582", auth=("neo4j", "Ceri1900"))

def giveMeDataLawsFull():
    # Extract laws from 2002 to today
    df = driver.run_cypher(""" match (l:Law) - [:HAS_ARTICLE] ->(a:Article) where l.publicationDate >= datetime("2016") return l.id, l.title, a.id, a.number, a.title, a.text """)
    return df

def giveMeDataLawsTitles():
    # Extract laws from 2016 to today, create dataframe ID-Title
    df = driver.run_cypher("""  MATCH (l:Article)<-[:HAS_ARTICLE]-(a:Law) WHERE a.publicationDate > datetime("2015") RETURN l.id AS law_id, l.title AS text """)
    return df







