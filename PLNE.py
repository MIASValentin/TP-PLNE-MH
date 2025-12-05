#!/usr/bin/python3
# coding: utf-8

#python3 PLNE.py test/fichier_test.txt

import itertools
import sys
from pyscipopt import Model

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
    if toks[0] == '#':
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
            combattant.append([(int(toks[1])), 0])      
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

M = Model()   # Le "modèle" est initialisé, et affecté à la variable M

def gain_combat(i,j):
    if combattant[i] < hotes[j][0]:
        return - hotes[j][2]
    elif combattant[i] > hotes[j][0]:
        return hotes[j][1]
    else:
        return 0

# Création d'une liste de variables booléennes : combattant i affronte hote j
x = {}

I = range(C)
J = range(H)
for i in I:
  for j in J:
    x[i,j] = M.addVar(f"x{i}{j}",vtype="B")

y = []
for i in I:
    tmp = []
    for j in J:
        tmp.append(gain_combat(i,j))
    y.append(tmp)

print(y)

# Création de l'obectif : max gains
M.setObjective(sum(x[i,j]*y[i][j] for i in I for j in J),"maximize")

# Contraintes:

# l'équipe des combattants peut désigner un capitaine, mais ça n'est pas obligatoire
for i in I:
    

# chaque combattant peut engager deux combats (ou moins) - sauf le capitaine des combattants, s'il y en a un, qui ne peut engager qu'un combat (ou aucun)
for i in I:
    M.addCons(sum(x[i,j] for j in J) <= 2)

# chaque hôte peut être engagé dans un combat au maximum
for j in J:
    M.addCons(sum(x[i,j] for i in I) <= 1)

# équipe des combattants a un budget en énergie B qui ne peut être dépassé
for i in I:
    M.addCons(sum(x[i,j]*hotes[j][3] for j in J) <= B)

# Lancement du solveur
print("-----------Exécution du solveur--------")
M.optimize()
print("-----------Exécution terminée--------")

# Si pas de solution optimale trouvée : on quitte l'interpréteur Python avec quit()
if M.getStatus() != 'optimal': print('Pas de solution ?!',quit())

# Lorsqu'il y a une solution optimale : on affiche les valeurs des x[i] et la valeur de l'objectif
print("\nSolution optimale trouvée :")
valeur = 0
for i in I : 
    for j in J:
        if M.getVal(x[i,j]) != 0:
            print('x', i, j)
            valeur += y[i][j]

print("\nValeur =", valeur)
