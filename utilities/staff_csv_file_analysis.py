import os
from collections import Counter

import pandas as pd

os.chdir("/home/david/dev/fastapi-sqlalchemy/tests")
# print(os.getcwd())
df = pd.read_csv("./Utilisation report - 20230227.xlsx - Staff List.csv", usecols=[0, 1, 2], header=7)
# df = df.dropna()

# print(df)
#
# print(f"{df['Name'].nunique()} unique names")
# print(f"{df['GM'].nunique()} unique GMs")
# print(f"{df['Perm/Contract'].nunique()} unique Emp Types")

names = list(df["Name"].loc[:180])
print(names[0], names[-1])

name_counter = Counter(names)
print(f"{len(list(name_counter))} unique names")
# print(name_counter.most_common(3))

gms = list(df["GM"].loc[:180])
gm_counter = Counter(gms)
print(f"{len(list(gm_counter))} unique GMs")
# print(gm_counter.most_common())

all_names = set(name_counter).union(set(gm_counter))
print(f"{len(all_names)} overall unique names")

emp_types = list(df["Perm/Contract"].loc[:180])
emp_type_counter = Counter(emp_types)
# print(emp_type_counter.most_common())
# print(list(emp_type_counter))
print(f"{len(list(emp_type_counter))} unique employment types")

print(f"There we expect {len(all_names) + len(set(emp_type_counter))} nodes")
#
# data_rows = df.loc[7:]
#
# data_rows.columns = ["Name","GM","Employment"]

everything = all_names.union(set(emp_type_counter))

nodes = set()
with open("./nodes.txt", "r") as file:
    while True:
        line = file.readline().strip()
        if line:
            nodes.add(line)
        else:
            break

print(f"read {len(nodes)} as a set")

# diff = nodes.difference(everything)
diff = everything.difference(nodes)
print(diff)

pass
