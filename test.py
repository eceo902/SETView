import random

l = [5, 4, 7, 6, 10, 15]

rtn = []

for i in range(3):
    temp = random.choice(l)
    rtn += temp
    l.remove(temp)

print(rtn)

