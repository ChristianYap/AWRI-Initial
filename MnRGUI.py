#! /usr/bin/env python3

from tkinter import *
from random import randint
from statistics import mean,stdev


# Sampling function
def lets_sample(population, sample_size, s_variation):
    '''
    Samples given population and returns sample size and number of marked individual in that sample.

    Parameters
    ----------
    population : 1D array
        List of all individuals in the population where marked individuals are denoted as 1s.
    sample_size: int
        Size of the individual sample
    s_variation: int
        Variation in sample size

    Returns
    ----------
    2-Tuple of form (size of sample,number of marked individuals)

    '''
    count = 0
    to_sample = [randint(0, len(population)) for i in range(sample_size + randint(0, s_variation))]
    sampled = []
    for individual in range(len(population)):
        if individual in to_sample:
            sampled.append(population[individual])
    return (len(sampled), sampled.count(1))

def marking(population_size, to_mark):
    marked = []
    while to_mark > 0:
        current = randint(0,population_size)
        if current not in marked:
            marked.append(current)
            to_mark = to_mark - 1

    population = []
    for individual in range(population_size):
        if individual in marked:
            population.append(1)
        else :
            population.append(0)
    return population

def aslikaam(event):
    population = marking(population_size.get(), to_mark.get())
    estimatedN = []
    for i in range(nSample.get()):
        sampleParam = lets_sample(population, sample_size.get(), s_variation.get())
        estimatedN.append(to_mark.get()*sampleParam[0]/sampleParam[1])
    resultmean.config(text="Result mean = " + str(mean(estimatedN)))
    resultSD.config(text="Result SD = " + str(stdev(estimatedN)))





#===============================GUI================================

box = Tk()
box.title("Mark-Recapture | Christian Yap")
# box.geometry("350x200")


# def checkkar(event):
#     print(population_size.get(), sample_size.get(), s_variation.get(), to_mark.get(), nSample.get())
#     resultmean.config(text="Result mean = "+str(population_size.get()))


#Layout

PS_label = Label(box, text="Original population size")
PS_label.grid(row=0, sticky=E)
population_size = IntVar()
PulmPS = Entry(box, width = 10, textvariable= population_size)
PulmPS.grid(row=0, column=1)

SS_label = Label(box, text="Size of each sample")
SS_label.grid(row=1, sticky=E)
sample_size = IntVar()
PulmSS = Entry(box, width = 10, textvariable= sample_size)
PulmSS.grid(row=1, column=1)

SV_label = Label(box, text="Variation in sampling")
SV_label.grid(row=2, sticky=E)
s_variation = IntVar()
PulmSV = Entry(box, width = 10, textvariable= s_variation)
PulmSV.grid(row=2, column=1)

TM_label = Label(box, text="Number of marked individuals")
TM_label.grid(row=3, sticky=E)
to_mark = IntVar()
PulmTM = Entry(box, width = 10, textvariable= to_mark)
PulmTM.grid(row=3, column=1)

nSample_label = Label(box, text="Number of samples")
nSample_label.grid(row=4, sticky=E)
nSample = IntVar()
PulmnSample = Entry(box, width = 10, textvariable= nSample)
PulmnSample.grid(row=4, column=1)

sampleNow = Button(box, text="Sample Now")
sampleNow.grid(row=5, columnspan=2)
sampleNow.bind("<Button-1>", aslikaam)

resultmean = Label(box, text="Result mean = ")
resultmean.grid(row=6, columnspan=2)
resultSD = Label(box, text="Result SD = ")
resultSD.grid(row=7, columnspan=2)




box.mainloop()
