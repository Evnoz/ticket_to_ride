import unittest

import sys

parent_dir = "../src/ticket_to_ride"
sys.path.append(parent_dir)

from main import Jeu
from joueurs import Joueur
from ia import IA
from cartes import Carte, Destination
from map import Ville, Rail


class Test_Aventurier(unittest.TestCase):
	def test_aventurier(self):
		jeu = Jeu(((1100, 800)))
		self.assertEqual(jeu.dimension, (1100, 800))
		self.assertEqual(len(jeu.joueurs), 0)
		self.assertEqual(jeu.tour, 1)

	def test_joueurs(self):
		jeu = Jeu(((1100, 800)))
		joueur1 = Joueur((255,0,0), "Alice", jeu.villes)
		joueur2 = Joueur((0,255,0), "Evann", jeu.villes)
		jeu.joueurs.append(joueur1)
		jeu.joueurs.append(joueur2)
		self.assertEqual(len(jeu.joueurs), 2)
		self.assertIn(joueur1, jeu.joueurs)
		self.assertIn(joueur2, jeu.joueurs)
		self.assertEqual(joueur1.pseudo, "Alice")
		self.assertEqual(joueur2.couleur_joueur, (0,255,0))
		self.assertEqual(joueur1.wagons_restants, 45)
		self.assertEqual(joueur2.score, 0)
		self.assertEqual(joueur1.cartes, [])
		self.assertEqual(joueur2.rails, [])

	def test_debut(self):
		jeu = Jeu(((1100, 800)))
		joueur1 = Joueur((255,0,0), "Alice", jeu.villes)
		joueur2 = Joueur((0,255,0), "Evann", jeu.villes)
		jeu.joueurs.append(joueur1)
		jeu.joueurs.append(joueur2)
		jeu.debut()
		self.assertEqual(len(joueur1.cartes), 4)
		self.assertEqual(len(joueur2.destination), 3) 
		self.assertEqual(len(jeu.cartes_revelees), 5)


	def test_tour(self):
		jeu = Jeu(((1100, 800)))
		joueur1 = Joueur((255,0,0), "Alice", jeu.villes)
		ia1 = IA((0,255,0), "Evann", jeu.villes, jeu.cartes_complet)
		jeu.joueurs.append(joueur1)
		jeu.joueurs.append(ia1)
		jeu.debut()
		nb_carte = len(jeu.pioche)
		jeu.piocher_destination(joueur1,1)
		self.assertEqual(len(joueur1.destination), 4)
		jeu.pioche = ia1.piocher(jeu.pioche)
		self.assertEqual(len(ia1.cartes), 5)
		self.assertEqual(len(jeu.pioche), nb_carte - 1)