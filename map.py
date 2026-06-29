"""
Module map
==========

Ce module définit les classes Ville et Rail utilisées pour représenter le plateau du jeu.
- Ville : représente une ville du plateau.
- Rail : représente un rail reliant deux villes, avec ses propriétés graphiques et logiques.

Auteur : Evann MICHEL
"""

import numpy as np

class Ville:
    """
    Classe représentant une ville du plateau.
    """
    def __init__(self, nom):
        """
        Initialise une ville avec son nom.

        Args:
            nom (str): Nom de la ville.
        """
        self.nom = nom

          
class Rail:
    """
    Classe représentant un rail reliant deux villes sur le plateau.
    """
    def __init__(self, couleur, depart, arrivee, val, possession, point_a, point_b, point_c, point_d):
        """
        Initialise un rail avec ses propriétés et ses coordonnées graphiques.

        Args:
            couleur (str): Couleur du rail.
            depart (Ville): Ville de départ.
            arrivee (Ville): Ville d'arrivée.
            val (int): Valeur (coût) du rail.
            possession (Joueur|None): Joueur possédant le rail, ou None.
            point_a, point_b, point_c (tuple): Coordonnées des points du rail pour le bouton.
            point_d (tuple): Coordonnées du point pour placer le drapeau.
        """
        self.couleur = couleur  # Couleur du rail
        self.depart = depart    # Ville de départ
        self.arrivee = arrivee  # Ville d'arrivée
        self.val = val          # Valeur du rail
        self.possession = possession  # Joueur possédant le rail
        self.xA, self.yA = point_a
        self.xB, self.yB = point_b
        self.xC, self.yC = point_c
        self.xD, self.yD = point_d

        A = np.array([[self.xA**2, self.xA, 1],
                      [self.xB**2, self.xB, 1],
                      [self.xC**2, self.xC, 1]])

        Y = np.array([self.yA, self.yB, self.yC])

        if np.linalg.det(A) == 0:
            self.a = self.b = self.c = 0
        else:
            self.a, self.b, self.c = np.linalg.solve(A, Y)

    def __str__(self):
        """
        Retourne une description textuelle du rail.

        Returns:
            str: Description du rail.
        """
        return f"Rail de {self.depart.nom} à {self.arrivee.nom}, couleur: {self.couleur}, coût: {self.val}"

    def achat(self, joueur, cartes):
        """
        Permet à un joueur d'acheter ce rail, met à jour la possession et les cartes du joueur.

        Args:
            joueur (Joueur): Joueur achetant le rail.
            cartes (list): Cartes utilisées pour l'achat.
        """
        if self.possession is not None:
            print("déjà acheté")
        self.possession = joueur
        joueur.rails.append(self)
        joueur.enlever_cartes(cartes)
        joueur.ajouter_points(self.val)