'''
Author: Colby Brown
22-July-2019
'''

from gerrychain import (
    Graph,
    Partition,
)
from gerrychain.updaters import Tally
import math

map_json_file = "res/NC_VTD.json"
vtd_column = "VTD"
population_column = "TOTPOP"
minority_columns = ["NH_BLACK", "NH_WHITE"]
plans = dict(   [ ("Judge's Plan", "judge")
                , ("2016 Plan","newplan")
                , ("2011 Plan", "oldplan")
                ])
num_partitions = 100
baseline_plans = ["districtMap%05d" % i for i in range(num_partitions)]


#####################################

vtd_to_fis = dict()
with open("arcgis_FIDtovtdkeymap.txt") as f:
    f.readline()
    for line in f:
        vtd_to_fis[line.split()[1]] = int(line.split()[0])
for m in baseline_plans:
    assignments = dict()
    for line in open("")

#####################################

myupdaters = {
    "population": Tally(population_column, alias="population")
}
myupdaters.update([(k, Tally(k)) for k in minority_columns])

def rel_entropy(graph, C):
    tot_pop = sum([graph.nodes()[n][population_column] for n in graph.nodes()]) 
    res = 0
    for j,Cj in C.parts.items():
        qj_pop = sum([graph.nodes[n][population_column] for n in Cj])
        entropy = 0
        everyone_else = tot_pop
        for minority in minority_columns:
            p = sum([graph.nodes[n][minority] for n in Cj]) / qj_pop
            if p == 0: continue
            entropy -= p * math.log(p, 2)
            everyone_else -= p
        # entropy -= everyone_else * math.log(everyone_else, 2)
        res += (qj_pop / tot_pop) * entropy
    return res

graph = Graph.from_json(map_json_file)
partitions = dict([(k, Partition(graph, v, myupdaters)) for k,v in plans.items()])

keys = list(plans.keys())
for j in range(len(keys)):
    print("%s: %0.3f" % (keys[j], rel_entropy(graph, partitions[keys[j]])))

