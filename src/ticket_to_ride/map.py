"""
Map module
==========

This module defines the Ville (city) and Rail classes used to represent the game board.
- Ville: represents a city on the board.
- Rail: represents a rail link between two cities, with its graphical and logical properties.

Author: Evann MICHEL
"""

import numpy as np

class Ville:
    """
    A class representing a city on the game board.
    """
    def __init__(self, nom):
        """
        Initialises a city with its name.

        Args:
            nom (str): Name of the city.
        """
        self.nom = nom

          
class Rail:
    """
    A class representing a railway line connecting two cities on the game board.
    """
    def __init__(self, couleur, depart, arrivee, val, possession, point_a, point_b, point_c, point_d):
        """
        Initialises a rail with its properties and graphical coordinates.

        Args:
            couleur (str): Colour of the rail.
            depart (City): City of departure.
            arrivee (City): Destination city.
            val (int): Value (cost) of the rail.
            possession (Player|None): Player owning the rail, or None.
            point_a, point_b, point_c (tuple): Coordinates of the rail’s points for the button. 
            point_d (tuple): Coordinates of the point where the flag is to be placed.
        """
        self.couleur = couleur  # Colour of the rail
        self.depart = depart    # City of departure
        self.arrivee = arrivee  # Destination city
        self.val = val          # Cost of the rail
        self.possession = possession  # Player in possession of the rail
        self.xA, self.yA = point_a
        self.xB, self.yB = point_b
        self.xC, self.yC = point_c
        self.xD, self.yD = point_d

        # In order to create buttons on the game board that follows a railway's curve, we calculate the parabola on the gameboard itself
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
        Returns a textual description of the rail.

        Returns:
            str: Description of the rail.
        """
        return f"railway from {self.depart.nom} to {self.arrivee.nom}, colour: {self.couleur}, cost: {self.val}"

    def achat(self, joueur, cartes):
        """
        Allows a player to buy this track; updates the player’s ownership and cards.

        Args:
            joueur (Joueur): Player buying the rail.
            cartes (list): Cards used for the purchase.
        """
        if self.possession is not None:
            print("Already bought")
        self.possession = joueur
        joueur.rails.append(self)
        joueur.enlever_cartes(cartes)
        joueur.ajouter_points(self.val)