#!/usr/bin/python3
# coding: utf-8

#python3 PLNE.py test/tournament_x.txt

import sys
from pyscipopt import Model

if len(sys.argv) != 2:
    print("Usage: python3 PLNE.py test/tournament_x.txt")

# Les paramètres :

f = open(sys.argv[1], 'r')

C = 0 # nombre C de combattants
H = 0 # nombre H d'hôtes
B = 0 # budget énergétique B
P = 0 # pénalité P déduite des gains des combattants pour chaque hôte qui n'est pas combattu

combattant = [] # combattant i -> niveau de compétence, estCapitaine
hotes = [] # hotes j -> niveau de compétence, win_point, loss_point, energy_cost

for ligne in f :
    toks = ligne.split()
    print(toks)
    if len(toks) == 0:
        continue
    elif toks[0] == '#':
        continue
    else:
        if len(toks) == 1:
            if C == 0:
                C = (int(toks[0]))
            elif H == 0:
                H = (int(toks[0]))
            elif B == 0:
                B = (int(toks[0]))
            elif P == 0:
                P = (int(toks[0]))
        if len(toks) == 2:
            combattant.append((int(toks[1])))      
        if len(toks) == 5:
            hotes.append([int(toks[1]),int(toks[2]),int(toks[3]),int(toks[4])])
            
 
f.close()

print("nbCombattant = ",C)
print("nb hotes = ", H)
print("Budget energetique = ", B)
print("Pénalité = ",P)
for i in range(C):
    print("combattant ", i, " niveau de compétence = ",combattant[i])
for i in range(H):
    print("hote ", i)
    print("niveau de competence = ",hotes[i][0])
    print("win_point = ", hotes[i][1])
    print("loss_point = ", hotes[i][2])
    print("energy_cost = ", hotes[i][3])

def gain_combattant(i,j):
    if combattant[i] < hotes[j][0]:
        return - hotes[j][2]
    elif combattant[i] > hotes[j][0]:
        return hotes[j][1]
    else:
        return 0
    
def gain_capitaine(i,j):
    if combattant[i] + 5 < hotes[j][0]:
        return - hotes[j][2]
    elif combattant[i] + 5 > hotes[j][0]:
        return hotes[j][1]
    else:
        return 0

def PLNE_SansCapitaine_SansJoker():
    M = Model()   # Le "modèle" est initialisé, et affecté à la variable M

    x = {}

    I = range(C)
    J = range(H)

    # combattant i affronte hote j
    for i in I:
        for j in J:
            x[i,j] = M.addVar(f"x{i}{j}",vtype="B")

    # gain du combat entre combattant i et hote j
    y = []
    for i in I:
        tmp = []
        for j in J:
            tmp.append(gain_combattant(i,j))
        y.append(tmp)

    # hote j n'a pas été affronté
    z = {}
    for j in J:
        z[j] = M.addVar(f"z{j}", vtype="B")

    # Création de l'obectif : max gains
    M.setObjective(sum(x[i,j]*y[i][j] for i in I for j in J) - sum(P * z[j] for j in J),"maximize")

    # Contraintes:

    # chaque combattant peut engager deux combats (ou moins) - sauf le capitaine des combattants, s'il y en a un, qui ne peut engager qu'un combat (ou aucun)
    for i in I:
        M.addCons(sum(x[i,j] for j in J) <= 2)

    # chaque hôte peut être engagé dans un combat au maximum
    for j in J:
        M.addCons(sum(x[i,j] for i in I) <= 1)
    
    # l'hote j n'a pas été affronté
    for j in J:
        M.addCons(z[j] >= 1 - sum(x[i,j] for i in I))
        M.addCons(z[j] <= 1)

    # équipe des combattants a un budget en énergie B qui ne peut être dépassé
    M.addCons(sum(x[i,j] * hotes[j][3] for i in I for j in J) <= B)

    # Lancement du solveur
    print("-----------Exécution du solveur--------")
    M.optimize()
    print("-----------Exécution terminée--------")

    # Si pas de solution optimale trouvée : on quitte l'interpréteur Python avec quit()
    if M.getStatus() != 'optimal': print('Pas de solution ?!',quit())

    # Lorsqu'il y a une solution optimale : on affiche les valeurs des x[i] et la valeur de l'objectif
    print("\nSolution optimale trouvée :")
    for i in I : 
        for j in J:
            if M.getVal(x[i,j]) != 0:
                print('x', i+1, j+1)

    print("\nValeur =", M.getObjVal())

def PLNE_AvecCapitaine_SansJoker():
    M = Model()   # Le "modèle" est initialisé, et affecté à la variable M

    x = {}

    I = range(C)
    J = range(H)

    # combattant i affronte hote j
    for i in I:
        for j in J:
            x[i,j] = M.addVar(f"x{i}{j}",vtype="B")

    # gain du combat entre combattant i et hote j
    y = []
    for i in I:
        tmp = []
        for j in J:
            tmp.append(gain_combattant(i,j))
        y.append(tmp)
    
    # gain du combat entre combattant i et hote j si i est capitaine
    y_c = []
    for i in I:
        tmp = []
        for j in J:
            tmp.append(gain_capitaine(i,j))
        y.append(tmp)

    # hote j n'a pas été affronté
    z = {}
    for j in J:
        z[j] = M.addVar(f"z{j}", vtype="B")
    
    # combattant i est le capitaine
    c = {}
    for i in I:
        c[i] = M.addVar(f"c{i}", vtype="B")

    # Création de l'obectif : max gains
    M.setObjective(sum(x[i,j]*y[i][j] for i in I for j in J) - sum(P * z[j] for j in J),"maximize")

    # Contraintes:

    # chaque combattant peut engager deux combats (ou moins) - sauf le capitaine des combattants, s'il y en a un, qui ne peut engager qu'un combat (ou aucun)
    for i in I:
        M.addCons(sum(x[i,j] for j in J) <= 2)

    # chaque hôte peut être engagé dans un combat au maximum
    for j in J:
        M.addCons(sum(x[i,j] for i in I) <= 1)
    
    # l'hote j n'a pas été affronté
    for j in J:
        M.addCons(z[j] >= 1 - sum(x[i,j] for i in I))
        M.addCons(z[j] <= 1)

    # équipe des combattants a un budget en énergie B qui ne peut être dépassé
    M.addCons(sum(x[i,j] * hotes[j][3] for i in I for j in J) <= B)

    # Lancement du solveur
    print("-----------Exécution du solveur--------")
    M.optimize()
    print("-----------Exécution terminée--------")

    # Si pas de solution optimale trouvée : on quitte l'interpréteur Python avec quit()
    if M.getStatus() != 'optimal': print('Pas de solution ?!',quit())

    # Lorsqu'il y a une solution optimale : on affiche les valeurs des x[i] et la valeur de l'objectif
    print("\nSolution optimale trouvée :")
    for i in I : 
        for j in J:
            if M.getVal(x[i,j]) != 0:
                print('x', i+1, j+1)

    print("\nValeur =", M.getObjVal())

PLNE_SansCapitaine_SansJoker()