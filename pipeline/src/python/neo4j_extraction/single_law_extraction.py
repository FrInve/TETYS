import pandas as pd
from graphdatascience import GraphDataScience

driver = GraphDataScience("bolt://localhost:47582", auth=("xx", "xx"))

    # Extract laws from 2016 to today
df = driver.run_cypher(""" match (l:Law) - [:HAS_ARTICLE] ->(a:Article) where l.id = ('2016|191') return l.id, l.title, a.id, a.number, a.title """)
df.to_csv('law_text.csv')