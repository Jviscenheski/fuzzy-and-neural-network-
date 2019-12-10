# -*- coding: utf-8 -*-

from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd

def redeNeural():

    # Coleta os dados de um arquivo .csv
    dados  = pd.read_csv("dataset.csv")

    # Separa em entrada e saída
    entrada = dados[["s1", "s2", "s3", "s4", "s5"]].values
    saida = dados[["m1", "m2"]].values

    xscaler = StandardScaler()
    xscaler.fit(entrada)
    entrada = xscaler.transform(entrada)

    # Cria uma rede com multiple layer perceptron regression
    clf = MLPRegressor(activation='relu', hidden_layer_sizes=(10), max_iter = 10000, random_state=9)
    clf.fit(entrada,saida)
    
    return clf, xscaler
