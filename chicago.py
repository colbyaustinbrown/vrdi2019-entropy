'''
Author: Colby Brown
24-July-2019
'''

from gerrychain import (
    Graph,
    Partition,
)
from gerrychain.updaters import Tally
import math
import json
import matplotlib.pyplot as plt

map_json_file = "res/Chicago_Precincts.json"
ward_column = "ward"
population_column = "TOTPOP"
populations = {"NH_BLACK": "black", "HIS_TOT": "hispanic", "NH_WHITE": "white"}
number_of_wards = 50

myupdaters = {
    "population": Tally(population_column, alias="population")
}
myupdaters.update([(v, Tally(k, alias=v)) for k,v in populations.items()])

def segregation(graph, part, R):
    numerator = 0
    tot_pop = sum([part['population'][i] for i in range(1,number_of_wards + 1)])
    for i in range(1,number_of_wards + 1):
        p = part['population'][i]
        if p == 0: continue
        r_pop = part[R][i] / p
        if r_pop == 0 or r_pop == 1: continue
        entropy = -(r_pop) * math.log(r_pop)
        entropy -= (1 - r_pop) * math.log(1 - r_pop)
        numerator += (p / tot_pop) * entropy
    r_pop = sum([part[R][i] for i in range(1,number_of_wards + 1)]) / tot_pop
    denominator = -r_pop * math.log(r_pop) - (1 - r_pop) * math.log(1 - r_pop)
    return numerator / denominator

graph = Graph.from_json(map_json_file)

data = []
for i in range(10000,15000):
    if i % 100 == 0:
        print(i)
    with open("./res/chicago_assignments/assignment%05d.json" % i) as f:
        assignments = json.load(f)
        for n in graph.nodes():
            graph.nodes[n]['assignment'] = assignments[graph.nodes[n]['JOINID']] + 1

        part = Partition(graph, 'assignment', myupdaters)

        data.append(dict([(l, segregation(graph, part, l)) for _,l in populations.items()]))

actual = Partition(graph, 'ward', myupdaters)

x = [d['hispanic'] for d in data]
plt.hist(x, 100)
plt.axvline(x=segregation(graph, actual, 'hispanic'), color='r')
plt.show()

x = [d['white'] for d in data]
plt.hist(x, 100)
plt.axvline(x=segregation(graph, actual, 'white'), color='r')
plt.show()

