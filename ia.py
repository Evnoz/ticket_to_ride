"""
Module ia
=========

Ce module définit différentes classes d'IA pour le jeu.
Chaque IA hérite de la classe Joueur et propose une stratégie différente pour jouer automatiquement :
- IA_aleatoire : choisit ses actions de façon aléatoire.
- IA_capitaliste : privilégie l'achat du rail le plus cher possible.
- IA_objectif : cherche à remplir ses objectifs de destination en priorité, en utilisant des algorithmes de plus court chemin.

Fonctions principales :
- Gestion des actions automatiques d'un joueur IA (piocher, acheter, planifier).
- Algorithmes de graphe pour la planification des objectifs (Dijkstra).
- Méthodes utilitaires pour l'achat de rails et la gestion des cartes.

Classes :
    IA : Classe de base pour une IA.
    IA_aleatoire : IA qui joue aléatoirement.
    IA_capitaliste : IA qui maximise la valeur de ses achats.
    IA_objectif : IA qui optimise la réalisation de ses objectifs.

Auteurs : Alice DEBELS et Evann MICHEL
"""

import random
from map import Ville, Rail
from cartes import Carte, Destination
from joueurs import Joueur
import time
import numpy as np

class IA(Joueur):
    """
    Classe de base pour une IA héritant de Joueur.
    Fournit des méthodes génériques pour piocher des cartes, piocher des destinations
    et acheter des rails.

    Auteur : Evann MICHEL
    """

    def __init__(self, couleur, pseudo, villes, cartes_complet):
        """
        Initialise une IA avec ses paramètres de base.

        Args:
            couleur (str): Couleur du joueur.
            pseudo (str): Pseudo du joueur.
            villes (list): Liste des villes du plateau.
            cartes_complet (list): Jeu complet de cartes pour la pioche.
        """
        super().__init__(couleur, pseudo, villes)
        self.rails_restants = []
        self.peut_acheter = []
        self.cartes_complet = cartes_complet

    def jouer(self):
        """
        Méthode à surcharger par les classes filles pour définir le comportement de l'IA à chaque tour.
        """
        pass

    def piocher(self, pile_pioche):
        """
        Pioche une carte depuis la pile de pioche et l'ajoute à la main du joueur.

        Args:
            pile_pioche (list): Pile de cartes à piocher.

        Returns:
            list: Nouvelle pile de pioche (mélangée et réinitialisée si vide).
        """
        pioche = pile_pioche.pop()
        self.cartes.append(pioche)
        self.couleurs[pioche.couleur] += 1
        if len(pile_pioche) == 0:
            pile_pioche = self.cartes_complet.copy()
            random.shuffle(pile_pioche)
        return pile_pioche

    def piocher_dest(self, pile_dest):
        """
        Pioche une carte destination et l'ajoute à la liste des objectifs du joueur.

        Args:
            pile_dest (list): Pile de cartes destination.

        Returns:
            list: Nouvelle pile de destinations.
        """
        choix = pile_dest.pop()
        self.destination.append(choix)
        return pile_dest

    def acheter_rail(self, rail):
        """
        Achete un rail si le joueur possède les cartes nécessaires.
        Prend en compte si le rail est gris ou non pour les cartes à défausser

        Args:
            rail (Rail): Rail à acheter.
        """
        if rail.couleur == "gris":
            couleur_max = max(self.couleurs, key=self.couleurs.get)
            cartes_achat = []
            cartes_arc = []
            for carte in self.cartes:
                if len(cartes_achat) < rail.val and carte.couleur == couleur_max:
                    cartes_achat.append((carte,0,0))
                elif carte.couleur == "arc-en-ciel":
                    cartes_arc.append(carte)
            for i in range(min(len(cartes_arc),rail.val-len(cartes_achat))):
                cartes_achat.append((cartes_arc[i],0,0))
            rail.achat(self,cartes_achat)
            cartes_achat.clear()
            cartes_arc.clear()
            self.rails_restants.remove(rail)
            
        elif self.couleurs[rail.couleur] + self.couleurs["arc-en-ciel"] >= rail.val:
            cartes_achat = []
            cartes_arc = []
            for carte in self.cartes:
                if carte.couleur == rail.couleur and len(cartes_achat) < rail.val:
                    cartes_achat.append((carte,0,0))
                elif carte.couleur == "arc-en-ciel":
                    cartes_arc.append(carte)
            for i in range(min(len(cartes_arc),rail.val-len(cartes_achat))):
                cartes_achat.append((cartes_arc[i],0,0))
            rail.achat(self,cartes_achat)
            cartes_achat.clear()
            cartes_arc.clear()
            self.rails_restants.remove(rail)


class IA_aleatoire(IA):
    """
    IA qui effectue des actions de manière aléatoire.
    Elle achète un rail possible au hasard ou pioche si aucun achat n'est possible.

    Auteur : Evann MICHEL
    """

    def __init__(self, couleur, pseudo, villes, cartes_complet):
        """
        Initialise l'IA aléatoire.

        Args:
            couleur (str): Couleur du joueur.
            pseudo (str): Pseudo du joueur.
            villes (list): Liste des villes du plateau.
            cartes_complet (list): Jeu complet de cartes pour la pioche.
        """
        super().__init__(couleur, pseudo, villes, cartes_complet)

    def jouer(self, couleurs_carte, rails_restants, pile_pioche, pile_dest):
        """
        Joue un tour en choisissant aléatoirement un rail à acheter ou en piochant.

        Args:
            couleurs_carte (dict): Couleurs de cartes disponibles.
            rails_restants (list): Rails encore disponibles.
            pile_pioche (list): Pile de cartes à piocher.
            pile_dest (list): Pile de cartes destination.

        Returns:
            tuple: (pile_pioche, pile_dest) après le tour.
        """
        self.rails_restants = rails_restants
        self.peut_acheter = []
        for rail in self.rails_restants:
            if rail.possession == None and rail.couleur == "gris" and self.couleurs[max(self.couleurs, key=self.couleurs.get)] + self.couleurs["arc-en-ciel"] >= rail.val:
                self.peut_acheter.append(rail)
            elif rail.possession == None and rail.couleur != "gris" and self.couleurs[rail.couleur] + self.couleurs["arc-en-ciel"] >= rail.val:
                self.peut_acheter.append(rail)
        if self.peut_acheter != []:
            rail = random.choice(self.peut_acheter)
            self.acheter_rail(rail)
        else:
            pile_pioche = self.piocher(pile_pioche)
            pile_pioche = self.piocher(pile_pioche)
        return pile_pioche, pile_dest


class IA_capitaliste(IA):
    """
    IA qui privilégie l'achat du rail le plus cher possible à chaque tour.

    Auteur : Evann MICHEL
    """

    def __init__(self, couleur, pseudo, villes, cartes_complet):
        """
        Initialise l'IA capitaliste.

        Args:
            couleur (str): Couleur du joueur.
            pseudo (str): Pseudo du joueur.
            villes (list): Liste des villes du plateau.
            cartes_complet (list): Jeu complet de cartes pour la pioche.
        """
        super().__init__(couleur, pseudo, villes, cartes_complet)

    def jouer(self, couleurs_carte, rails_restants, pile_pioche, pile_dest):
        """
        Joue un tour en achetant le rail le plus cher possible ou en piochant.

        Args:
            couleurs_carte (dict): Couleurs de cartes disponibles.
            rails_restants (list): Rails encore disponibles.
            pile_pioche (list): Pile de cartes à piocher.
            pile_dest (list): Pile de cartes destination.

        Returns:
            tuple: (pile_pioche, pile_dest) après le tour.
        """
        self.rails_restants = rails_restants
        self.peut_acheter = []
        for rail in self.rails_restants:
            if rail.possession == None and rail.couleur == "gris" and self.couleurs[max(self.couleurs, key=self.couleurs.get)] + self.couleurs["arc-en-ciel"] >= rail.val:
                self.peut_acheter.append(rail)
            elif rail.possession == None and rail.couleur != "gris" and self.couleurs[rail.couleur] + self.couleurs["arc-en-ciel"] >= rail.val:
                self.peut_acheter.append(rail)
        if self.peut_acheter != []:
            rail = max(self.peut_acheter, key=lambda r: r.val)
            self.acheter_rail(rail)
        else:
            pile_pioche = self.piocher(pile_pioche)
            pile_pioche = self.piocher(pile_pioche)
        return pile_pioche, pile_dest


class IA_objectif(IA):
    """
    IA qui cherche à remplir ses objectifs de destination en priorité
    en utilisant des algorithmes de plus court chemin pour planifier ses achats de rails.

    Auteurs : Alice DEBELS et Evann MICHEL
    """

    def __init__(self, couleur, pseudo, villes, cartes_complet):
        """
        Initialise l'IA objectif.

        Args:
            couleur (str): Couleur du joueur.
            pseudo (str): Pseudo du joueur.
            villes (list): Liste des villes du plateau.
            cartes_complet (list): Jeu complet de cartes pour la pioche.
        """
        super().__init__(couleur, pseudo, villes, cartes_complet)

    def cle_de_valeur_mini(self, etat, dist, e):
        """
        Retourne la liste des clés de valeur e dans etat ayant la valeur minimale dans dist.

        Args:
            etat (dict): Dictionnaire d'états des sommets.
            dist (dict): Dictionnaire des distances.
            e (string): Valeur recherchée dans etat (blanc, gris ou noir).

        Returns:
            list: Clés correspondant à la valeur minimale.

        Auteur : Alice DEBELS
        """
        cle_etat = etat.keys()
        cle_etat_e = [cle for cle in cle_etat if etat[cle] == e]
        liste_cle_mini = []
        valeur_mini = float('+inf')

        for cle in cle_etat_e:
            if dist[cle] < valeur_mini:
                liste_cle_mini = [cle]
                valeur_mini = dist[cle]
            elif dist[cle] == valeur_mini:
                liste_cle_mini.append(cle)

        liste_cle_mini.sort()
        return liste_cle_mini

    def dijkstra_pcc(self, g, s, a):
        """
        Calcule le plus court chemin entre deux sommets d'un graphe pondéré.

        Args:
            g (dict): Graphe valué (dictionnaire d'adjacence).
            s (Ville): Sommet de départ.
            a (Ville): Sommet d'arrivée.

        Returns:
            tuple: (chemin, sommets_traites, sommets_decouverts, distance)

        Auteur : Alice DEBELS
        """
        dist = {}
        pcc = {}
        etat = {}
        for sommet in g.keys():
            etat[sommet] = 'blanc'
            dist[sommet] = float('inf')
        etat[s] = 'gris'
        dist[s] = 0
        while etat[a] != 'noir':
            s_liste = self.cle_de_valeur_mini(etat, dist, 'gris')
            if not s_liste:
                return ([], [], [], float('inf'))
            s_proche = s_liste[0]
            for (v, c) in g[s_proche]:
                if etat[v] == 'blanc':
                    etat[v] = 'gris'
                    dist[v] = dist[s_proche] + c
                    pcc[v] = s_proche
                elif etat[v] == 'gris':
                    if dist[s_proche] + c < dist[v]:
                        dist[v] = dist[s_proche] + c
                        pcc[v] = s_proche
            etat[s_proche] = 'noir'
        chemin = [a]
        p = a
        while p != s:
            p = pcc[p]
            chemin.append(p)
        chemin.reverse()
        sommets_traites = [s for s in etat.keys() if etat[s] == 'noir']
        sommets_decouverts = [s for s in etat.keys() if etat[s] == 'gris']
        d = dist[a]
        return (chemin, sommets_traites, sommets_decouverts, d)

    def chemins_objectifs(self, rails_possedes, rails_restants, destinations):
        """
        Génère la liste des chemins optimaux pour remplir les objectifs de destination.

        Args:
            rails_possedes (list): Rails déjà possédés par le joueur.
            rails_restants (list): Rails encore disponibles.
            destinations (list): Liste des cartes destination du joueur.

        Returns:
            list: Liste de chemins (list de Ville) pour chaque objectif.

        Auteur : Alice DEBELS
        """
        rails_non_adverses = rails_possedes + rails_restants
        sorted(destinations, key=lambda destination: destination.points, reverse=True)
        chemins = []
        g = self.conversion_graphe(rails_non_adverses, self.villes)
        for dest in destinations:
            depart = dest.depart
            arrivee = dest.arrivee
            chemins.append(self.dijkstra_pcc(g, depart, arrivee)[0])
        return chemins

    def conversion_chemin_rails(self, chemin):
        """
        Convertit un chemin de villes en une liste de rails correspondants.

        Args:
            chemin (list): Liste ordonnée de noms de villes.

        Returns:
            list: Liste de Rail correspondant au chemin.

        Auteur : Alice DEBELS
        """
        chemin_rails = []
        for i in range (len(chemin) - 1):
            for rail in self.rails_restants:
                if (rail.depart.nom == chemin[i] and rail.arrivee.nom == chemin[i+1]) or (rail.arrivee.nom == chemin[i] and rail.depart.nom == chemin[i+1]):
                    chemin_rails.append(rail)
        return chemin_rails

    def jouer(self, couleurs_carte, rails_restants, pile_pioche, pile_dest):
        """
        Joue un tour en essayant de remplir les objectifs de destination en priorité.
        Achète les rails nécessaires, pioche des destinations ou des cartes si besoin.
        Si aucune carte destination n'est disponible, acheter les rails les plus chers.

        Args:
            couleurs_carte (dict): Couleurs de cartes disponibles.
            rails_restants (list): Rails encore disponibles.
            pile_pioche (list): Pile de cartes à piocher.
            pile_dest (list): Pile de cartes destination.

        Returns:
            tuple: (pile_pioche, pile_dest) après le tour.

        Auteur : Evann MICHEL
        """
        self.rails_restants = rails_restants
        chemins = self.chemins_objectifs(self.rails, self.rails_restants, self.destination)
        chemin_souhaite = []
        val_dest = [dest.points for dest in self.destination]
        val_dest.sort(reverse=True)

        # Ordonne les destinations par points décroissants
        for i in range(len(self.destination)):
            for val in val_dest:
                if self.destination[i].points == val:
                    chemin_souhaite.append(self.conversion_chemin_rails(chemins[i]))
                    break
        self.peut_acheter = [[]]*len(self.destination)

        # Recherche les rails pouvant être achetés pour accomplir chaque destination
        for i in range(len(self.destination)):
            for rail in chemin_souhaite[i]:
                if rail.possession == None and rail.couleur == "gris" and self.couleurs[max(self.couleurs, key=self.couleurs.get)] + self.couleurs["arc-en-ciel"] >= rail.val:
                    self.peut_acheter[i].append(rail)
                elif rail.possession == None and rail.couleur != "gris" and self.couleurs[rail.couleur] + self.couleurs["arc-en-ciel"] >= rail.val:
                    self.peut_acheter[i].append(rail)

        # Achète le premier rail le plus cher possible
        if self.peut_acheter != [[]]*len(self.destination):
            for i in range(len(self.peut_acheter)):
                if self.peut_acheter[i] != []:
                    rail = max(self.peut_acheter[i], key=lambda r: r.val)
                    self.acheter_rail(rail)
                    break

        # Si aucune destination n'est faisable et qu'il possède moins de 3 cartes destination, en repiocher une
        elif chemins == [[]]*len(self.destination) and pile_dest != [] and len(self.destination) < 3:
            pile_dest = self.piocher_dest(pile_dest)

        # Sinon acheter le rail le plus cher possible
        elif chemins == [[]]*len(self.destination) and (pile_dest == [] or len(self.destination) >= 3):
            self.peut_acheter = []
            for rail in self.rails_restants:
                if rail.possession == None and rail.couleur == "gris" and self.couleurs[max(self.couleurs, key=self.couleurs.get)] + self.couleurs["arc-en-ciel"] >= rail.val:
                    self.peut_acheter.append(rail)
                elif rail.possession == None and rail.couleur != "gris" and self.couleurs[rail.couleur] + self.couleurs["arc-en-ciel"] >= rail.val:
                    self.peut_acheter.append(rail)
            if self.peut_acheter != []:
                rail = max(self.peut_acheter, key=lambda r: r.val)
                self.acheter_rail(rail)
            else:
                pile_pioche = self.piocher(pile_pioche)
                pile_pioche = self.piocher(pile_pioche)
            return pile_pioche, pile_dest
        
        # Sinon piocher
        else:
            pile_pioche = self.piocher(pile_pioche)
            pile_pioche = self.piocher(pile_pioche)
        return pile_pioche, pile_dest