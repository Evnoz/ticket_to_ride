"""
Player Module
==============

This module defines the Joueur (player) class, which manages all features related to a player
in the game.

Main features:
- Management of cards, railways, objectives/destinations, and the player’s score.
- Methods for adding/removing cards, updating the score, and tracking remaining train cards.
- Graph algorithms (BFS, DFS) to validate objectives and calculate the longest constructed path.

Class:
    Joueur: Represents a player in the game, along with their associated properties and methods.

Authors: Alice DEBELS and Evann MICHEL
"""

class Joueur:
    """
    A class representing a player in the game.

    Manages cards, railways, destinations, and score. Provides methods
    for manipulating the player's state, as well as graph algorithms to validate
    objectives and calculate the longest path.
    """

    def __init__(self, couleur, pseudo, villes):
        """
        Initializes a player with their colour, username, and the list of cities on the board.

        Args:
            couleur (str): Player's colour.
            pseudo (str): Player's username.
            villes (list): List of the cities in the game.
        """
        self.rails = []  # railways owned by the player
        self.score = 0  # player's score
        self.cartes = []  # player's cards
        self.couleurs = {}  # number of cards in each colours
        self.destination = []  # player's destinations
        self.couleur_joueur = couleur  # player's colour
        self.pseudo = pseudo  # player's username
        self.max_longueur = 0
        self.villes = villes  # cities

        # Points to be allocated according to the length of the rail
        self.dico_points = {
            1: 1,
            2: 2,
            3: 4,
            4: 7,
            5: 10,
            6: 15,
        }

        # Number of train cards remaining for the player
        self.wagons_restants = 45

    def enlever_cartes(self, cartes):
        """
        Remove the player’s used cards and update the remaining train cards.
        Confirm the objectives achieved and update the score.

        Args:
            cartes (list): List of tuples (card, x, y) to be removed.

        Author : Evann MICHEL
        """
        for carte, x, y in cartes:
            self.couleurs[carte.couleur] -= 1
            self.cartes.remove(carte)
            self.wagons_restants -= 1

        for dest in self.destination:
            if self.verifObjectif(self.rails, self.villes, dest.depart, dest.arrivee):
                self.score += dest.points
                print("Objectif validé : ", dest)
                self.destination.remove(dest)

    def ajouter_points(self, nb_case):
        """
        Adds the points corresponding to the length of a railway built to the score.

        Args:
            nb_case (int): length of the railway.

        Author: Evann MICHEL
        """
        self.score += self.dico_points[nb_case]

    def dfs_plus_long(self, g, sommet, visites, longueur_courante, chemin_courant, meilleur_resultat):
        """
        Recursive search for the longest path in the player’s graph (DFS).

        Args:
            g (dict): Graph of owned railways.
            sommet  (str): Starting vertex.
            visites (list): Vertices already visited.
            longueur_courante (int): Current length of the path.
            chemin_courant (list): Current path.
            meilleur_resultat (dict): Dictionary storing the best length and the associated path.

        Author: Evann MICHEL
        """
        visites.append(sommet)
        chemin_courant.append(sommet)

        if longueur_courante > meilleur_resultat["longueur"]:
            meilleur_resultat["longueur"] = longueur_courante
            meilleur_resultat["chemin"] = chemin_courant.copy()

        for voisin, poids in g[sommet]:
            if voisin not in visites:
                self.dfs_plus_long(g, voisin, visites, longueur_courante + poids, chemin_courant, meilleur_resultat)

        visites.remove(sommet)
        chemin_courant.pop()

    def plus_long_chemin(self):
        """
        Calculates the length of the longest continuous path constructed by the player.

        Returns:
            int: Length of the longest path.

        Author: Evann MICHEL
        """
        g = self.conversion_graphe(self.rails, self.villes)
        meilleur_resultat = {"longueur": 0, "chemin": []}
        for sommet in g:
            self.dfs_plus_long(g, sommet, [], 0, [], meilleur_resultat)
        return meilleur_resultat["longueur"]

    def conversion_graphe(self, rails_possedes, villes):
        """
        Generates a graph in dictionary form from the list of railways.

        Args:
            rails_possedes (list): Rails owned by the player.
            villes (list): List of cities on the board.

        Returns:
            dict: Graph of owned rails (key = city name, value = neighbours and weight).

        Author: Alice DEBELS
        """
        g = {}
        for ville in villes:
            g[ville.nom] = []
        for rail in rails_possedes:
            g[rail.depart.nom].append((rail.arrivee.nom, rail.val))
            g[rail.arrivee.nom].append((rail.depart.nom, rail.val))
        return g

    def BFS(self, G, s):
        """
        Breadth-first traversal of the graph starting from a given vertex.

        Args:
            G (dict): Graph represented as a dictionary.
            s (str|int): Starting vertex.

        Returns:
            list: Vertices reached from the starting vertex.

        Author: Alice DEBELS
        """
        F = [s]
        c = []
        m = {}
        for sommet in G.keys():
            m[sommet] = False

        while F != []:
            sa = F.pop(0)
            if not m[sa]:
                m[sa] = True
                v = G[sa]
                v.sort()
                for v, _ in G[sa]:
                    if not m[v]:
                        F.append(v)
        for i in G.keys():
            if m[i] == True:
                c.append(i)
        return c

    def verifObjectif(self, rails, villes, depart, arrivee):
        """
        Checks whether the player has achieved an objective (connecting two cities).

        Args:
            rails (list): Rails owned.
            villes (list): List of towns on the board.
            depart (str|int): Name or ID of the starting town.
            arrivee (str|int): Name or ID of the destination town.

        Returns:
            bool: True if the destination city is accessible from the starting city, False otherwise.

        Author: Alice DEBELS
        """
        exploration = self.BFS(self.conversion_graphe(rails, villes), depart)
        test = arrivee in exploration
        return test