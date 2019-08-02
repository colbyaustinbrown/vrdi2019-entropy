'''
Author: Colby Brown
26-July-2019
'''

import pandas as pds
import geopandas as gpd
import maup
import math
import matplotlib.pyplot as plt

def isnan(x):
    return x != x

chicago_2010_file = "res/chicago_metro_2010/Chicago-Naperville-Elgin_IL-IN_WI.shp"
chicago_2000_file = "res/chicago_metro_2000/Chicago-Naperville-Elgin_IL-IN-WI.shp"
chicago_1990_file = "res/chicago_metro_1990/Chicago-Naperville-Elgin_IL-IN-WI.shp"
chicago_blocks_file = "res/chicago_metro_blocks/Chicago_metro_blckgrps.shp"

columns = ["NH_WHITE", "NH_BLACK", "HIS_WHITE", "HIS_BLACK", "TOTPOP", "HIS_TOT"]
columns2000 = list(map(lambda x : x + "_2000", columns))
columns1990 = list(map(lambda x : x + "_1990", columns))

il2010 = gpd.read_file(chicago_2010_file)
il2000 = gpd.read_file(chicago_2000_file)
il1990 = gpd.read_file(chicago_1990_file)
blocks = gpd.read_file(chicago_blocks_file)
il2000.crs = il2010.crs
il1990.crs = il2010.crs
blocks.to_crs(il2010.crs, inplace=True)

for c in columns:
    il2010[c] = il2010[c].astype(int)
    il2000[c] = il2000[c].astype(int)
    il1990[c] = il1990[c].astype(int)

pieces2000 = maup.intersections(il2000, il2010, area_cutoff=0)
pieces1990 = maup.intersections(il1990, il2010, area_cutoff=0)
weights2000 = blocks["TOTPOP"].groupby(maup.assign(blocks, pieces2000)).sum()
weights1990 = blocks["TOTPOP"].groupby(maup.assign(blocks, pieces1990)).sum()
weights2000 = maup.normalize(weights2000, level=0)
weights1990 = maup.normalize(weights1990, level=0)

il2010[columns2000] = maup.prorate(pieces2000, il2000[columns], weights=weights2000)
il2010[columns1990] = maup.prorate(pieces1990, il1990[columns], weights=weights1990)

il2010.plot(column=il2010["TOTPOP_2000"].isna())
plt.show()

print(il2010["NH_BLACK_2000"])
print(il2010["TOTPOP_2000"])

def relentropy(df, races, totpop_col):
    totpop = sum(x for x in df[totpop_col] if not isnan(x))
    res = 0
    for j in range(0, df.shape[0]):
        jpop = df[totpop_col][j] 
        everyoneelse = jpop
        if jpop == 0 or isnan(jpop): continue
        qj = jpop / totpop
        entropy = 0
        for r in races:
            everyoneelse -= df[r][j]
            pij = df[r][j] / jpop
            if pij == 0 or isnan(pij): continue
            entropy -= pij * math.log(pij, 2)
        res += qj * entropy
        if everyoneelse == 0: continue
        pee = everyoneelse / jpop
        entropy -= pee * math.log(pee, 2)
    return res

def segregation(df, races, totpop_col):
     totpop = sum(x for x in df[totpop_col] if not isnan(x))
     pis = list(map(lambda r: sum([x / totpop for x in df[r] if not isnan(x)]), races))
     # Add one extra element for "everyone else"
     pis.append(1 - sum(pis))
     return relentropy(df, races, totpop_col) / sum(map(lambda pi: -pi * math.log(pi, 2), pis))

print("Black 1990: " + str(segregation(il2010, ["NH_BLACK_1990"], "TOTPOP_1990")))
print("Black 2000: " + str(segregation(il2010, ["NH_BLACK_2000"], "TOTPOP_2000")))
print("Black 2010: " + str(segregation(il2010, ["NH_BLACK"], "TOTPOP")))
print("His 1990: " + str(segregation(il2010, ["HIS_TOT_1990"], "TOTPOP_1990")))
print("His 2000: " + str(segregation(il2010, ["HIS_TOT_2000"], "TOTPOP_2000")))
print("His 2010: " + str(segregation(il2010, ["HIS_TOT"], "TOTPOP")))
print("White 1990: " + str(segregation(il2010, ["NH_WHITE_1990"], "TOTPOP_1990")))
print("White 2000: " + str(segregation(il2010, ["NH_WHITE_2000"], "TOTPOP_2000")))
print("White 2010: " + str(segregation(il2010, ["NH_WHITE"], "TOTPOP")))

