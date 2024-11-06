from itertools import cycle
import matplotlib.pyplot as plt
import numpy as np
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import AgglomerativeClustering

def plot_dendrogram(model,**kwargs):
    children=model.children_
    distance=np.arange(children.shape[0])
    no_of_observations=np.arange(2,children.shape[0]+2)
    linkage_matrix=np.column_stack([children,distance,no_of_observations]).astype(float)
    dendrogram(linkage_matrix,**kwargs)

x=np.array([(89, 151), (114, 120), (156, 110), (163, 153), (148, 215), (170, 229), (319, 166), (290, 178), (282, 222)])
NC=3

clustering=AgglomerativeClustering(n_clusters=NC,linkage='ward')
x_pr=clustering.fit_predict(x)

f,ax=plt.subplots(1,2)
for c,n in zip(cycle('bgrcmykgrcmykgrcmykgrcmykgrcmykgrcmyk'),range(NC)):
    clst=x[x_pr==n].T
    ax[0].scatter(clst[0],clst[1],s=10,color=c)

plot_dendrogram(clustering,ax=ax[1])
plt.show()