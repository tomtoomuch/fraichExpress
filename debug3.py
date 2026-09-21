
# erreur trouvée : ZeroDivisionError: division by zero
# Solution : tester si le parametre commandes n'est pas vide  avant de le parcourir 

# erreur trouvee :  total += c["montant"] 
# convertir en float avant de faire la somme
def moyenne_panier(commandes):
    if len(commandes) == 0:
        return "Commandes vide"
    else:
        total = 0
        for c in commandes:
            total += float(c["montant"])
        return total / len(commandes)
        



print(moyenne_panier([]))
print(moyenne_panier([{"montant": "12.5"}, {"montant": "8"}]))


