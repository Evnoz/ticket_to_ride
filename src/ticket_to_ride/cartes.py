"""
Carte (card) Module
=============

This module defines the Carte and Destination classes used in the game.
- Carte: represents a train card, including its colour and image.
- Destination: represents an objective card linking two cities, with an associated number of points.

Author: Evann MICHEL
"""

import pygame

class Carte:
    """
    Class representing a train card.
    """
    def __init__(self, couleur, chemin):
        """
        Initialises a train card with its colour and the path to its image.

        Args:
            couleur (str): The colour of the card.
            chemin (str): The path to the card’s image.
        """
        self.couleur = couleur  # card's colour
        self.chemin = chemin    # path to the card’s image.
        self.image = pygame.image.load(self.chemin)  # load card's image

        
class Destination:
    """
    Class representing a destination (objective).
    """
    def __init__(self, id_depart, id_arrivee, points, dico_id_villes):
        """
        Initialises a destination card.

        Args:
            id_depart (str|int): ID of the departure city.
            id_arrivee (str|int): ID of the arrival city.
            points (int): Points for the destination.
            dico_id_villes (dict): Dictionary mapping city IDs to names.
        """
        self.id_depart = id_depart  # departure city
        self.id_arrivee = id_arrivee  # arrival city
        self.points = points  # points for the destination
        self.dico_id_villes = dico_id_villes  # dict mapping city IDs to names
        self.depart = self.dico_id_villes[self.id_depart]
        self.arrivee = self.dico_id_villes[self.id_arrivee]
        
    def __str__(self):
        """
        Returns a string describing the destination and the number of points.

        Returns:
            str: Description of the destination.
        """
        depart = self.dico_id_villes[self.id_depart]
        arrivee = self.dico_id_villes[self.id_arrivee]
        return f"Destination : {depart} - {arrivee} for {self.points} points"


