import pandas as pd
import os

def read_counters():

    path = '../model/starting_file_trial/new_counter.txt'
    df = pd.read_csv(path, sep=' ', header=None)

    counter = df[1].sum()

    print(counter)

    os.remove(path)

    return counter

if __name__ == '__main__':
    read_counters()

