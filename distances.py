'''
Author: Colby Brown
22-July-2019
'''

from gerrychain import (
        Graph,
        Partition,
)
from gerrychain.updaters import Tally
import numpy as np
import math
import matplotlib.pyplot as plt
from sklearn import manifold

map_json_file = "res/PA_VTD.json"
vtd_column = "VTDST10"
population_column = "TOT_POP"
popper_column = "pop_percent"
plans = dict(   [ ("2011 Enacted", "2011_PLA_1")
                , ("Governor's counter-proposal", "GOV")
                , ("Turzai-Scarnati", "TS")
                , ("2018 Enacted Remedial", "REMEDIAL_P")
                , ("538 Compact", "538CPCT__1")
                , ("538 Democratic", "538DEM_PL")
                , ("538 Republican", "538GOP_PL")
                , ("8th Grade", "8THGRADE_1")
                ])
weight_by_population = False

myupdaters = {
        "population": Tally(population_column, alias="population")
}

def rel_entropy(graph, X, Y):
    tot_pop = sum([graph.nodes[n][population_column] for n in graph.nodes()]) if weight_by_population else len(graph.nodes())
    res = 0
    for j,Yj in Y.parts.items():
        qj_pop = sum([graph.nodes[n][population_column] for n in Yj]) if weight_by_population else len(Yj)
        entropy = 0
        for i,Xi in X.parts.items():
            p = sum([graph.nodes[n][population_column] for n in Yj & Xi]) / qj_pop if weight_by_population else len(Yj & Xi) / qj_pop
            if p == 0: continue
            entropy -= p * math.log(p, 2)
        res += (qj_pop / tot_pop) * entropy
    return res

graph = Graph.from_json(map_json_file)
partitions = dict([(k, Partition(graph, v, myupdaters)) for k,v in plans.items()])

keys = list(plans.keys())
distMat = np.zeros((len(keys), len(keys)))
for j in range(len(keys)):
    for k in range(j+1, len(keys)):
        distMat[j,k] = rel_entropy(graph, partitions[keys[j]], partitions[keys[k]])
        distMat[k,j] = distMat[j,k]

fig,ax = plt.subplots(figsize=(8,8))
fig.suptitle("PA Entropy MDS, weighted")

'''
ax.imshow(distMat);
ax.xaxis.tick_top()
plt.show()

'''

mds = manifold.MDS(n_components=2, dissimilarity='precomputed')
results = mds.fit(distMat)
coords = results.embedding_
z = coords[:,0]
y = coords[:,1]
ax.scatter(z, y)
for k in range(len(keys)):
    ax.annotate(keys[k], (z[k], y[k]))

plt.show()


