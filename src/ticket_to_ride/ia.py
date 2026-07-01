"""
IA (AI) module
=========

This module defines various AI classes for the game.
Each AI inherits from the Player class and offers a different strategy for playing automatically:
- IA_aleatoire: chooses its actions at random.
- IA_capitaliste: prioritises buying the most expensive track possible.
- IA_objectif: seeks to fulfil its destination objectives as a priority, using shortest-path algorithms.

Main features:
- Management of an AI player’s automatic actions (draw, buy, plan).
- Graph algorithms for objective planning (Dijkstra).
- Utility methods for buying tracks and managing cards.

Classes :
    AI: Base class for an AI.
    IA_aleatoire: An AI that plays randomly.
    IA_capitaliste: An AI that maximises the value of its purchases.
    IA_objectif: An AI that optimises the achievement of its objectives.

Auteurs : Alice DEBELS et Evann MICHEL
"""

import random
from map import Ville, Rail
from cartes import Carte, Destination
from joueurs import Joueur
import numpy as np

class IA(Joueur):
    """
    Base class for an AI that inherits from Joueur (player class).
    Provides generic methods for drawing cards, drawing destinations
    and purchasing railway.

    Author: Evann MICHEL
    """

    def __init__(self, couleur, pseudo, villes, cartes_complet):
        """
        Initialises an AI with its basic settings.

        Args:
            couleur (str): The player’s colour.
            pseudo (str): The player’s username.
            villes (list): List of cities on the board.
            cartes_complet (list): Full deck of cards for the draw pile.
        """
        super().__init__(couleur, pseudo, villes)
        self.rails_restants = []
        self.peut_acheter = []
        self.cartes_complet = cartes_complet

    def jouer(self):
        """
        A method to be overridden by subclasses to define the AI’s behaviour on each turn.
        """
        pass

    def piocher(self, pile_pioche):
        """
        Draws a card from the draw pile and adds it to the player’s hand.

        Args:
            pile_pioche (list): The pile of cards to draw from.

        Returns:
            list: New draw pile (shuffled and reset if empty).
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
        Draws a destination card and adds it to the player’s list of objectives.

        Args:
            pile_dest (list): Stack of destination cards.

        Returns:
            list: New stack of destinations.
        """
        choix = pile_dest.pop()
        self.destination.append(choix)
        return pile_dest

    def acheter_rail(self, rail):
        """
        Buy a rail if the player has the necessary cards.
        Take into account whether the rail is grey or not when discarding cards

        Args:
            rail (Rail): The rail to buy.
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
    AI that performs actions at random.
    It buys a possible railway at random or draws a card if no purchase is possible.

    Author: Evann MICHEL
    """

    def __init__(self, couleur, pseudo, villes, cartes_complet):
        """
        Initialises the random AI.

        Args:
            couleur (str): Player’s colour.
            pseudo (str): Player’s username.
            villes (list): List of cities on the board.
            cartes_complet (list): Full deck of cards for the draw pile.
        """
        super().__init__(couleur, pseudo, villes, cartes_complet)

    def jouer(self, couleurs_carte, rails_restants, pile_pioche, pile_dest):
        """
        Play a turn by randomly selecting a track to buy or by drawing a card.

        Args:
            couleurs_carte (dict): Available card colours.
            rails_restants (list): Tracks still available.
            pile_pioche (list): Stack of cards to draw from.
            pile_dest (list): Destination card stack.

        Returns:
            tuple: (draw_stack, destination_stack) after the turn.
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
    AI that prioritises purchasing the most expensive rail possible in each turn.

    Author: Evann MICHEL
    """

    def __init__(self, couleur, pseudo, villes, cartes_complet):
        """
        Initialises the capitalist AI.

        Args:
            couleur (str): Player’s colour.
            pseudo (str): Player’s username.
            villes (list): List of cities on the board.
            cartes_complet (list): Full deck of cards for the draw pile.
        """
        super().__init__(couleur, pseudo, villes, cartes_complet)

    def jouer(self, couleurs_carte, rails_restants, pile_pioche, pile_dest):
        """
        Play a turn by buying the most expensive track possible or by drawing a card.

        Args:
            couleurs_carte (dict): Available card colours.
            rails_restants (list): Tracks still available.
            pile_pioche (list): Stack of cards to draw from.
            pile_dest (list): Destination card stack.

        Returns:
            tuple: (draw_stack, destination_stack) after the turn.
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
    AI that prioritises meeting its destination targets
    by using shortest-path algorithms to plan its rail purchases.

    Authors: Alice DEBELS and Evann MICHEL
    """

    def __init__(self, couleur, pseudo, villes, cartes_complet):
        """
        Initialises the objective AI.

        Args:
            couleur (str): Player’s colour.
            pseudo (str): Player’s username.
            villes (list): List of cities on the board.
            cartes_complet (list): Full deck of cards for the draw pile.
        """
        super().__init__(couleur, pseudo, villes, cartes_complet)

    def cle_de_valeur_mini(self, etat, dist, e):
        """
        Returns the list of keys of value e in etat with the minimal value in dist.

        Args:
            etat (dict): Dictionary of vertex states.
            dist (dict): Dictionary of distances.
            e (string): Value to search for in state (blanc, gris, noir) (=white, grey, black).

        Returns:
            list: Keys corresponding to the minimum value.

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
        Calculates the shortest path between two vertices in a weighted graph.

        Args:
            g (dict): Weighted graph (adjacency dictionary).
            s (City): Starting vertex.
            a (City): Destination vertex.

        Returns:
            tuple: (path, visited_vertices, unvisited_vertices, distance)

        Author: Alice DEBELS
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
        Generates a list of optimal routes to fulfil the destination objectives.

        Args:
            rails_possedes (list): railway already owned by the player.
            rails_restants (list): railway still available.
            destinations (list): List of the player’s destination cards.

        Returns:
            list: List of routes (list of Ville (cities)) for each objective.

        Author: Alice DEBELS
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
        Converts a path of cities into a list of corresponding railway.

        Args:
            chemin (list): An ordered list of town names.

        Returns:
            list: A list of railway corresponding to the path.

        Author: Alice DEBELS
        """
        chemin_rails = []
        for i in range (len(chemin) - 1):
            for rail in self.rails_restants:
                if (rail.depart.nom == chemin[i] and rail.arrivee.nom == chemin[i+1]) or (rail.arrivee.nom == chemin[i] and rail.depart.nom == chemin[i+1]):
                    chemin_rails.append(rail)
        return chemin_rails

    def jouer(self, couleurs_carte, rails_restants, pile_pioche, pile_dest):
        """
        Play a round by trying to fulfil the destination objectives as a priority.
        Buy the necessary railways, and draw destinations or cards if needed.
        If no destination cards are available, buy the most expensive tracks.

        Args:
            couleurs_carte (dict): Available card colours.
            rails_restants (list): Tracks still available.
            pile_pioche (list): Stack of cards to be drawn from.
            pile_dest (list): Stack of destination cards.

        Returns:
            tuple: (draw_stack, destination_stack) after the turn.

        Author : Evann MICHEL
        """
        self.rails_restants = rails_restants
        chemins = self.chemins_objectifs(self.rails, self.rails_restants, self.destination)
        chemin_souhaite = []
        val_dest = [dest.points for dest in self.destination]
        val_dest.sort(reverse=True)

        # Sort the destinations in descending order by points
        for i in range(len(self.destination)):
            for val in val_dest:
                if self.destination[i].points == val:
                    chemin_souhaite.append(self.conversion_chemin_rails(chemins[i]))
                    break
        self.peut_acheter = [[]]*len(self.destination)

        # Find the railways that can be purchased to reach each destination
        for i in range(len(self.destination)):
            for rail in chemin_souhaite[i]:
                if rail.possession == None and rail.couleur == "gris" and self.couleurs[max(self.couleurs, key=self.couleurs.get)] + self.couleurs["arc-en-ciel"] >= rail.val:
                    self.peut_acheter[i].append(rail)
                elif rail.possession == None and rail.couleur != "gris" and self.couleurs[rail.couleur] + self.couleurs["arc-en-ciel"] >= rail.val:
                    self.peut_acheter[i].append(rail)

        # Buy the first railway that’s as expensive as possible
        if self.peut_acheter != [[]]*len(self.destination):
            for i in range(len(self.peut_acheter)):
                if self.peut_acheter[i] != []:
                    rail = max(self.peut_acheter[i], key=lambda r: r.val)
                    self.acheter_rail(rail)
                    break

        # If no destination is possible and has less than 3 destination cards, draw another one
        elif chemins == [[]]*len(self.destination) and pile_dest != [] and len(self.destination) < 3:
            pile_dest = self.piocher_dest(pile_dest)

        # Alternatively, buy the most expensive railway you can find
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
        
        # Otherwise, draw cards
        else:
            pile_pioche = self.piocher(pile_pioche)
            pile_pioche = self.piocher(pile_pioche)
        return pile_pioche, pile_dest