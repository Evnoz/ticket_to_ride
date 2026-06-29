"""
Module joueurs
==============

Ce module définit la classe Joueur, qui gère l'ensemble des fonctionnalités liées à un joueur
dans le jeu.

Fonctionnalités principales :
- Gestion des cartes, des rails, des objectifs/destinations et du score du joueur.
- Méthodes pour ajouter/retirer des cartes, mettre à jour le score et les wagons restants.
- Algorithmes de graphe (BFS, DFS) pour valider les objectifs et calculer le plus long chemin construit.

Classe :
    Joueur : Représente un joueur du jeu avec ses propriétés et méthodes associées.

Auteurs : Alice DEBELS et Evann MICHEL
"""

class Joueur:
    """
    Classe représentant un joueur du jeu.

    Gère les cartes, les rails, les destinations, le score, et fournit des méthodes
    pour manipuler l'état du joueur ainsi que des algorithmes de graphe pour valider
    les objectifs et calculer le plus long chemin.
    """

    def __init__(self, couleur, pseudo, villes):
        """
        Initialise un joueur avec sa couleur, son pseudo et la liste des villes du plateau.

        Args:
            couleur (str): Couleur du joueur.
            pseudo (str): Nom ou pseudo du joueur.
            villes (list): Liste des villes du plateau.
        """
        self.rails = []  # rails du joueur
        self.score = 0  # score du joueur
        self.cartes = []  # cartes du joueur
        self.couleurs = {}  # nombre de chaque carte couleur du joueur
        self.destination = []  # destinations du joueur
        self.couleur_joueur = couleur  # couleur du joueur
        self.pseudo = pseudo  # nom du joueur
        self.max_longueur = 0
        self.villes = villes  # liste des villes de la carte

        # Points à distribuer selon la longueur du rail
        self.dico_points = {
            1: 1,
            2: 2,
            3: 4,
            4: 7,
            5: 10,
            6: 15,
        }

        # Nombre de wagons restants pour le joueur
        self.wagons_restants = 45

    def enlever_cartes(self, cartes):
        """
        Enlève les cartes utilisées du joueur et met à jour les wagons restants.
        Valide les objectifs atteints et met à jour le score.

        Args:
            cartes (list): Liste de tuples (carte, x, y) à enlever.

        Auteur : Evann MICHEL
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
        Ajoute au score les points correspondant à la longueur d'un rail construit.

        Args:
            nb_case (int): Nombre de cases du rail.

        Auteur : Evann MICHEL
        """
        self.score += self.dico_points[nb_case]

    def dfs_plus_long(self, g, sommet, visites, longueur_courante, chemin_courant, meilleur_resultat):
        """
        Recherche récursive du plus long chemin dans le graphe du joueur (DFS).

        Args:
            g (dict): Graphe des rails possédés.
            sommet (str): Sommet de départ.
            visites (list): Sommets déjà visités.
            longueur_courante (int): Longueur actuelle du chemin.
            chemin_courant (list): Chemin courant.
            meilleur_resultat (dict): Dictionnaire stockant la meilleure longueur et le chemin associé.

        Auteur : Evann MICHEL
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
        Calcule la longueur du plus long chemin continu construit par le joueur.

        Returns:
            int: Longueur du plus long chemin.

        Auteur : Evann MICHEL
        """
        g = self.conversion_graphe(self.rails, self.villes)
        meilleur_resultat = {"longueur": 0, "chemin": []}
        for sommet in g:
            self.dfs_plus_long(g, sommet, [], 0, [], meilleur_resultat)
        return meilleur_resultat["longueur"]

    def conversion_graphe(self, rails_possedes, villes):
        """
        Génère un graphe sous forme de dictionnaire à partir de la liste des rails.

        Args:
            rails_possedes (list): Rails possédés par le joueur.
            villes (list): Liste des villes du plateau.

        Returns:
            dict: Graphe des rails possédés (clé = nom de ville, valeur = voisins et poids).

        Auteur : Alice DEBELS
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
        Parcours en largeur du graphe à partir d'un sommet donné.

        Args:
            G (dict): Graphe sous forme de dictionnaire.
            s (str|int): Sommet de départ.

        Returns:
            list: Sommets atteints depuis le sommet de départ.

        Auteur : Alice DEBELS
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
        Vérifie si un objectif (relier deux villes) est atteint par le joueur.

        Args:
            rails (list): Rails possédés.
            villes (list): Liste des villes du plateau.
            depart (str|int): Nom ou id de la ville de départ.
            arrivee (str|int): Nom ou id de la ville d'arrivée.

        Returns:
            bool: True si la ville d'arrivée est accessible depuis la ville de départ, False sinon.

        Auteur : Alice DEBELS
        """
        exploration = self.BFS(self.conversion_graphe(rails, villes), depart)
        test = arrivee in exploration
        return test