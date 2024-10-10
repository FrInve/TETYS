import pandas as pd
from graphdatascience import GraphDataScience

driver = GraphDataScience("bolt://localhost:47582", auth=("neo4j", "Ceri1900"))

def giveMeDataLaws():
    # Extract laws from 2015 to today, create dataframe ID-Title
    df = driver.run_cypher(""" MATCH (l:Article)<-[:HAS_ARTICLE]-(a:Law) WHERE a.publicationDate > datetime("2015") RETURN l.id AS ID, l.title AS Title""")

    return df