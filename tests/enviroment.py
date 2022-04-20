import os

for el in os.environ:
    print(el, os.environ[el], sep=" ---> ")
