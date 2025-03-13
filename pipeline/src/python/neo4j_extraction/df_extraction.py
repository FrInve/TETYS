import pandas as pd
from graphdatascience import GraphDataScience

driver = GraphDataScience("bolt://localhost:47582", auth=("neo4j", "Ceri1900"))

### FAI ATTENZIONE, QUESTA E' LA PRIMA VERSIONE CHE HAI UTILIZZATO CHE ESTRAE TUTTE LE LEGGI DAL 2016 AD OGGI
# ADESSO SCRIVO UNA NUOVA QUERY PER FARE FINE-TUNING CON UN CAMPIONE PIU' GRANDE
# PERO' NON TI DIMENTICARE QUESTA C
# def giveMeDataLawsFull():
    # Extract laws from 2016 to today
    # df = driver.run_cypher(""" match (l:Law) - [:HAS_ARTICLE] ->(a:Article) where l.publicationDate >= datetime("2016") return l.id, l.title, a.id, a.number, a.title, a.text """)
    # return df

def giveMeDataLawsFull():
    # Extract laws from 2016 to today
    df = driver.run_cypher(""" match (l:Law) - [:HAS_ARTICLE] ->(a:Article) where l.publicationDate >= datetime("2016") return l.id, l.title, a.id, a.number, a.title, a.text """)
    return df


def giveMeDataLawsTitles():
    # Extract laws from 2016 to today, create dataframe ID-Title
    df = driver.run_cypher("""  MATCH (l:Article)<-[:HAS_ARTICLE]-(a:Law) WHERE a.publicationDate > datetime("2015") RETURN l.id AS article_id, l.title AS text, a.id as law_id, a.title as law_title """)
    return df







