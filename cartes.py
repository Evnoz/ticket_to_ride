"""
Module cartes
=============

Ce module definit les classes Carte et Destination utilisees dans le jeu.
- Carte : represente une carte wagon avec sa couleur et son image.
- Destination : represente une carte objectif reliant deux villes avec un nombre de points associe.

Auteur : Evann MICHEL
"""

import pygame

class Carte:
    """
    Classe repr�sentant une carte wagon.
    """
    def __init__(self, couleur, chemin):
        """
        Initialise une carte wagon avec sa couleur et le chemin de son image.

        Args:
            couleur (str): Couleur de la carte.
            chemin (str): Chemin vers l'image de la carte.
        """
        self.couleur = couleur  # Couleur de la carte
        self.chemin = chemin    # Chemin de l'image de la carte
        self.image = pygame.image.load(self.chemin)  # Charge l'image de la carte

        
class Destination:
    """
    Classe representant une carte de destination (objectif).
    """
    def __init__(self, id_depart, id_arrivee, points, dico_id_villes):
        """
        Initialise une carte de destination.

        Args:
            id_depart (str|int): Identifiant de la ville de depart.
            id_arrivee (str|int): Identifiant de la ville d'arrivee.
            points (int): Points de la destination.
            dico_id_villes (dict): Dictionnaire associant id de ville a nom.
        """
        self.id_depart = id_depart  # Ville de depart
        self.id_arrivee = id_arrivee  # Ville d'arrivee
        self.points = points  # Points de la destination
        self.dico_id_villes = dico_id_villes  # Dictionnaire id->nom
        self.depart = self.dico_id_villes[self.id_depart]
        self.arrivee = self.dico_id_villes[self.id_arrivee]
        
    def __str__(self):
        """
        Renvoie une chaine de caracteres decrivant la destination et le nombre de points.

        Returns:
            str: Description de la destination.
        """
        depart = self.dico_id_villes[self.id_depart]
        arrivee = self.dico_id_villes[self.id_arrivee]
        return f"Destination : {depart} - {arrivee} pour {self.points} points"


