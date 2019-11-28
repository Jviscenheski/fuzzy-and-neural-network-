from scipy.interpolate import interp1d

distanceList = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
pertinenciaNear = [0, 0, 0, 0, 0, 0.5, 1.0, 1.0, 1.0, 1.0, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
pertinenciaFar = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 1.0, 1.0, 1.0, 0.5, 0, 0, 0, 0, 0]
pertVeryNear = [1.0, 1.0, 1.0, 1.0, 0.5, 0, 0, 0, 0, 0, 0, 0.5, 1.0, 1.0, 1.0, 0.5, 0, 0, 0, 0, 0]
pertVeryFar = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.5, 1.0, 1.0, 1.0, 1.0]


# Calcula as funções de interpolação por pertinência
pertFunctionNear = interp1d(distanceList, pertinenciaNear, kind='cubic')
pertFunctionFar = interp1d(distanceList, pertinenciaFar, kind='cubic')
pertFunctionVeryNear = interp1d(distanceList, pertVeryNear, kind='cubic')
pertFunctionVeryFar = interp1d(distanceList, pertVeryFar, kind='cubic')
#print(str(pertFunctionVeryFar(0.33)))

# eu coloquei os pontos discretos, mas o sensor pode me dar um valor tipo 0.87 m, certo?
# Ele naõ ta mapeado, por isso eu uso interpolação. interpolação pega um conjunto e aproxima a função que deu origem ao conjunto
# essas são as nossas funções de pertinencia
# Entrada: vetor com 8 sensores
# digamos que eu receba um vetor de sensores assim:
sensores = [0.1, 0.5, 1.24, 1.97, 1.15, 0.68, 0.17, 0.13]

# preciso calcular a pertinência de cada variável linguística para cada sensor
dicSensors = {}
index = 0           # esse index vai me dizer sobre qual sensor estamos falando

for mesure in sensores:
    pertNear = float(pertFunctionNear(mesure))
    pertFar = float(pertFunctionFar(mesure))
    pertVeryNear = float(pertFunctionVeryNear(mesure))
    pertVeryFar = float(pertFunctionVeryFar(mesure))

    dicSensors[index] = [pertVeryNear, pertNear, pertFar, pertVeryFar]
    index += 1

print(dicSensors)

#[MP,P,L,ML]

# Agora eu preciso sujeitar todos os sensores a todas as regras
# ----- 90+ rules
rule1 = min(dicSensors[0][0], dicSensors[1][1], dicSensors[2][2], dicSensors[3][3], dicSensors[4][2], dicSensors[5][1],
            dicSensors[6][0], dicSensors[7][0])
rule2 = min(dicSensors[0][0], dicSensors[1][0], dicSensors[2][1], dicSensors[3][2], dicSensors[4][3], dicSensors[5][2],
            dicSensors[6][1], dicSensors[7][0])
rule3 = min(dicSensors[0][0], dicSensors[1][1], dicSensors[2][2], dicSensors[3][3], dicSensors[4][3], dicSensors[5][3],
            dicSensors[6][2], dicSensors[7][1])
# ----- 45+ rules
rule4 = min(dicSensors[0][1], dicSensors[1][2], dicSensors[2][3], dicSensors[3][3], dicSensors[4][3], dicSensors[5][2],
            dicSensors[6][1], dicSensors[7][0])
rule5 = min(dicSensors[0][1], dicSensors[1][2], dicSensors[2][3], dicSensors[3][3], dicSensors[4][2], dicSensors[5][1],
            dicSensors[6][0], dicSensors[7][0])
# ----- 0 rules
rule6 = min(dicSensors[0][3], dicSensors[1][3], dicSensors[2][3], dicSensors[3][3], dicSensors[4][3], dicSensors[5][3],
            dicSensors[6][3], dicSensors[7][3])
rule7 = min(dicSensors[0][2], dicSensors[1][2], dicSensors[2][2], dicSensors[3][2], dicSensors[4][2], dicSensors[5][2],
            dicSensors[6][2], dicSensors[7][2])
rule8 = min(dicSensors[0][3], dicSensors[1][1], dicSensors[2][0], dicSensors[3][1], dicSensors[4][3], dicSensors[5][1],
            dicSensors[6][0], dicSensors[7][1])
rule9 = min(dicSensors[0][3], dicSensors[1][2], dicSensors[2][1], dicSensors[3][2], dicSensors[4][3], dicSensors[5][3],
            dicSensors[6][3], dicSensors[7][3])
rule10 = min(dicSensors[0][3], dicSensors[1][3], dicSensors[2][3], dicSensors[3][3], dicSensors[4][3], dicSensors[5][2],
            dicSensors[6][1], dicSensors[7][2])
# ----- 45- rules
rule11 = min(dicSensors[0][1], dicSensors[1][0], dicSensors[2][1], dicSensors[3][2], dicSensors[4][3], dicSensors[5][3],
            dicSensors[6][3], dicSensors[7][2])
rule12 = min(dicSensors[0][1], dicSensors[1][0], dicSensors[2][0], dicSensors[3][0], dicSensors[4][1], dicSensors[5][2],
            dicSensors[6][2], dicSensors[7][2])
# ----- 90- rules
rule13 = min(dicSensors[0][0], dicSensors[1][0], dicSensors[2][0], dicSensors[3][1], dicSensors[4][2], dicSensors[5][3],
            dicSensors[6][2], dicSensors[7][1])
rule14 = min(dicSensors[0][1], dicSensors[1][0], dicSensors[2][0], dicSensors[3][0], dicSensors[4][1], dicSensors[5][2],
            dicSensors[6][3], dicSensors[7][3])

max90p = max(rule1, rule2, rule3)
max45p = max(rule4, rule5)
max0 = max(rule6, rule7, rule8, rule9, rule10)
max45n = max(rule11, rule12)
max90n = max(rule13, rule14)


finalAngle = (-90*max90n + -45*max45n + 0*max0 + 45*max45p + 90*max90p)/(max90n + max45n + max0 + max45p + max90p)
print(str(finalAngle))









