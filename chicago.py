'''
Author: Colby Brown
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
populations = {"NH_BLACK": "black", "HISP": "hispanic", "NH_WHITE": "white"}
number_of_wards = 50

myupdaters = {
    "population": Tally(population_column, alias="population")
}
myupdaters.update([(v, Tally(k, alias=v)) for k,v in populations.items()])

def segregation(graph, part, R):
    numerator = 0
    for i in range(0,number_of_wards):
        p = part['population'][i]
        if p == 0: continue
        r_pop = part[R][i] / p
        if r_pop == 0 or r_pop == 1: continue
        numerator -= (r_pop) * math.log(r_pop)
        numerator -= (1 - r_pop) * math.log(1 - r_pop)
    tot_pop = sum([part['population'][i] for i in range(0,number_of_wards)])
    r_pop = sum([part[R][i] for i in range(0,number_of_wards)]) / tot_pop
    denominator = -r_pop * math.log(r_pop) - (1 - r_pop) * math.log(1 - r_pop)
    return numerator / denominator

graph = Graph.from_json(map_json_file)

data = []
for i in range(10000,15000):
    with open("./res/chicago_assignments/assignment%05d.json" % i) as f:
        assignments = json.load(f)
        for n in graph.nodes():
            graph.nodes[n]['assignment'] = assignments[graph.nodes[n]['JOINID']]

        part = Partition(graph, 'assignment', myupdaters)

        data.append(dict([(l, segregation(graph, part, l)) for _,l in populations.items()]))

actual = Partition(graph, 'ward', myupdaters)

x = [d['black'] for d in data]
plt.hist(x, 100)
plt.axvline(x=segregation(graph, actual, 'black'), color='r')
plt.show()

