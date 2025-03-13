from bertopic import BERTopic
import pandas as pd
import numpy as np

matrices = np.load('matrices_compressed_0_500.npz', allow_pickle=True)
print(matrices['arr_0'][207])
