"""
Main game module.

This script launches the graphical application, manages the main game loop,
data initialisation (cities, tracks, destinations, cards), player management
(human and AI players), as well as the display and user interactions.

Key features:
- Loading game board and card data from CSV files.
- Game management: game turns, drawing cards, buying tracks, objectives, scores.
- GUI using Pygame (display of the game board, cards, buttons, etc.).
- Support for multiple types of AI and human players.
- Display of the selection screen, the game screen and the end-of-game screen.

Main class:
    Jeu (Game): Handles the game’s logic and display.

Execution:
    Run this script to start the game with the GUI.

Author: Evann MICHEL
"""

import pygame
import random
from map import Ville, Rail
from ihm import IHM
from cartes import Carte, Destination
import csv
from joueurs import Joueur
from ia import IA_aleatoire, IA_capitaliste, IA_objectif, IA

# Main class
class Jeu:
    """
    The game’s main class.

    Handles the game logic, the graphical user interface, data loading,
    and the management of players, maps, tracks and destinations.
    """
    def __init__(self, dimension):
        """
        Initialises the game, loads the data and sets up the main variables.

        Args:
            dimension (tuple): Dimensions of the game window (width, height).
        """
        self.dimension = dimension

        # Loading data on cities, rails and destinations from CSV files
        self.villes, self.dico_villes, self.dico_id_villes = self.lire_villes("./csv/villes.csv")
        self.rails = self.lire_rails("./csv/chemins.csv")
        self.destinations = self.lire_destination("./csv/destinations.csv")

        random.shuffle(self.destinations)

        self.rails_restants = self.rails.copy()

        # Initialising players and game variables
        self.joueurs = []
        self.ia = []

        for el in self.ia:
            el.jeu = self

        self.tour = 1
        self.joueurActuel = 0
        self.dernier_joueur = None

        self.mute = True

        # Colours available for train cards cards
        self.couleurs_carte = ["rouge", "bleu", "vert", "blanc", "jaune", "orange", "rose", "noir", "arc-en-ciel"]
        self.cartes_complet = self.lire_cartes("./csv/cartes.csv")
        self.pioche = self.cartes_complet.copy()
        random.shuffle(self.pioche)



        self.cartes_revelees = []


    def lire_cartes(self, fichier_cartes):
        """
        Loads train cards from a CSV file.

        Args:
            fichier_cartes (str): Path to the CSV file containing the cards.

        Returns:
            list: A list of Cartes (cards) objects.
        """
        cartes = []
        with open(fichier_cartes, mode='r', encoding='utf-8') as fichier:
            lecteur = csv.DictReader(fichier)
            for ligne in lecteur:
                couleur = ligne['couleur']
                cartes.append(Carte(couleur, "./images/wagons/" + couleur + ".jpg"))
        return cartes


    def lire_villes(self, fichier_villes):
        """
        Loads cities from a CSV file.

        Args:
            fichier_villes (str): Path to the CSV file containing the cities.

        Returns:
            tuple: (list of Ville (cities) objects, dict city name to city id, dict city id to city name)
        """
        villes = []
        dico_villes = {}
        dico_id_villes = {}
        with open(fichier_villes, mode='r', encoding='utf-8') as fichier:
            lecteur = csv.DictReader(fichier)
            for ligne in lecteur:
                nom = ligne['nom']
                id_ville = ligne['id']
                dico_villes[nom] = id_ville
                dico_id_villes[id_ville] = nom
                villes.append(Ville(nom))
        return villes, dico_villes, dico_id_villes

    
    def lire_rails(self, fichier_rails):
        """
        Loads rails from a CSV file.

        Args:
            fichier_rails (str): Path to the rails CSV file.

        Returns:
            list: List of Rail objects.
        """
        rails = []
        vrai_x = 1024
        vrai_y = 683
        with open(fichier_rails, mode='r', encoding='utf-8') as fichier:
            lecteur = csv.DictReader(fichier)
            for ligne in lecteur:
                couleur = ligne['couleur']
                depart = self.villes[int(ligne['depart'])]
                arrivee = self.villes[int(ligne['arrivee'])]
                val = int(ligne['poids'])
                # Calculation of the rail coordinates on the game board based on the window dimensions
                x_a = int(int(ligne['xA']) * self.dimension[0] / vrai_x)
                y_a = int(int(ligne['yA']) * self.dimension[1] / vrai_y)
                x_b = int(int(ligne['xB']) * self.dimension[0] / vrai_x)
                y_b = int(int(ligne['yB']) * self.dimension[1] / vrai_y)
                x_c = int(int(ligne['xC']) * self.dimension[0] / vrai_x)
                y_c = int(int(ligne['yC']) * self.dimension[1] / vrai_y)
                x_d = int(int(ligne['xD']) * self.dimension[0] / vrai_x)
                y_d = int(int(ligne['yD']) * self.dimension[1] / vrai_y)
                rails.append(Rail(couleur, depart, arrivee, val, None, (x_a, y_a), (x_b, y_b), (x_c, y_c), (x_d,y_d)))
        return rails

    def lire_destination(self, fichier_destinations):
        """
        Loads destinations (objectives) from a CSV file.

        Args:
            fichier_destinations (str): Path to the CSV file containing the destinations.

        Returns:
            list: A list of Destination objects.
        """
        destinations = []
        with open(fichier_destinations, mode='r', encoding='utf-8') as fichier:
            lecteur = csv.DictReader(fichier)
            for ligne in lecteur:
                id_depart = self.dico_villes[ligne['depart']]
                id_arrivee = self.dico_villes[ligne['arrivee']]
                points = int(ligne['points'])
                destinations.append(Destination(id_depart, id_arrivee, points, self.dico_id_villes))
        return destinations

    def piocher_wagon(self, joueur):
        """
        Draw a train card for the player and add it to their hand.

        Args:
            joueur (Joueur): The player in question.
        """
        carte = self.pioche.pop()
        joueur.cartes.append(carte)
        joueur.couleurs[carte.couleur] += 1

        if len(self.pioche) == 0:
            self.pioche = self.cartes_complet.copy()
            random.shuffle(self.pioche)

    def piocher_destination(self, joueur, nb):
        """
        Draws a certain number of destination cards for the player.

        Args:
            joueur (Joueur): The player in question.
            nb (int): The number of cards to draw.
        """
        for _ in range(nb):
            choix = self.destinations.pop()
            joueur.destination.append(choix)

    def debut(self):
        """
        Sets up the start of the game: deals cards and destinations to each player.
        """
        for i in range(5):
            carte = self.pioche.pop()
            self.cartes_revelees.append(carte)

        for joueur in self.joueurs:
            self.piocher_destination(joueur, 3)
            for couleur in self.couleurs_carte:
                joueur.couleurs[couleur] = 0
            for i in range(4):
                self.piocher_wagon(joueur)

    def main(self):
        """
        The game’s main loop.

        Handles the display, user events, turn progression,
        player and AI actions, and the end of the game.
        """

        # Pygame and window initialisation
        pygame.init()
        pygame.mixer.init()
        largeur, hauteur = self.dimension
        screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("Ticket to ride")

        ihm = IHM(self, screen) # GUI Initialisation

        # Loading the background image (game board)
        background = pygame.image.load("./images/map.jpg")
        background_dim = pygame.transform.scale(background, (largeur, hauteur))
        running = True

        afficher_cartes = False
        souhait_achat = False
        souhait_pioche = False

        # Start of the game
        self.debut()

        # Game variables to limit the number of cards that can be drawn and the number of rails that can be purchased in one turn
        nb_carte_prise = 0
        nb_rail_achete = 0
        nb_dest_prise = 0

        # Main game loop
        while running:
            screen.blit(background_dim, (0, 0))

            # Retrieving the current player
            joueur = self.joueurs[self.joueurActuel]

            # make player play turn if AI
            if joueur in self.ia:
                self.pioche, self.destinations = joueur.jouer(self.couleurs_carte, self.rails_restants, self.pioche, self.destinations)
                self.joueurActuel += 1
                if self.joueurActuel >= len(self.joueurs):
                    self.joueurActuel = 0
                    self.tour += 1


            # Displaying game information (turn, score, etc.)
            ihm.dessiner_bouton(str(joueur.pseudo) + "'s turn!", largeur - 200, 0, 200, 20, joueur.couleur_joueur)
            ihm.dessiner_bouton("Turn " + str(self.tour) + ", " + str(joueur.wagons_restants) + " train cards left", largeur - 200, 20, 200, 25, (255, 255, 255))
            ihm.dessiner_bouton("Score : " + str(joueur.score), largeur - 200, 40, 200, 25, (255, 255, 255))

            if self.dernier_joueur is not None:
                ihm.dessiner_texte("Last turn !", largeur//2-100, hauteur-40, ihm.couleurs["rouge"], 50)

            # Event handling (buttons, window closure, etc.)
            if not (souhait_achat or souhait_pioche):
                for event in pygame.event.get():
                    # Closing the window
                    if event.type == pygame.QUIT:
                        running = False
                    # Mouse clicks
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = event.pos

                        # Mute button
                        if largeur - 45 <= mouse_x <= largeur - 5 and hauteur - 70 <= mouse_y <= hauteur - 30:
                            self.mute = not self.mute

                        # Deck button
                        if 0 <= mouse_x <= 100 and 0 <= mouse_y <= 25 and not (souhait_achat or souhait_pioche):
                            afficher_cartes = not afficher_cartes

                        # Draw card
                        if 0 <= mouse_x <= 100 and 40 <= mouse_y <= 65 and not (afficher_cartes or souhait_achat):
                            souhait_pioche = True

                        # Draw destination
                        if 0 <= mouse_x <= 150 and hauteur-30 <= mouse_y <= hauteur and not (afficher_cartes or souhait_achat or souhait_pioche) and nb_dest_prise == 0 and self.destinations != []:
                            self.piocher_destination(joueur, 1)
                            ihm.jouer_son('./sons/pioche.wav', self.mute)
                            nb_carte_prise = 2
                            nb_rail_achete = 1
                            nb_dest_prise = 1

                        # End player turn
                        if largeur - 100 <= mouse_x <= largeur and hauteur - 25 <= mouse_y <= hauteur and not (afficher_cartes or souhait_achat or souhait_pioche):
                            self.joueurActuel += 1
                            nb_carte_prise = 0
                            nb_rail_achete = 0
                            nb_dest_prise = 0
                            ihm.jouer_son('./sons/tchoutchou.wav', self.mute)
                            if self.joueurActuel >= len(self.joueurs):
                                self.joueurActuel = 0
                                self.tour += 1

                        # Buy rail
                        for rail in self.rails_restants:
                            if rail.xC == 0 and rail.yC == 0:
                                y_min = min(rail.yA, rail.yB)
                                y_max = max(rail.yA, rail.yB)
                                x_min = min(rail.xA, rail.xB) - 8
                                x_max = max(rail.xA, rail.xB) + 8
                            else:
                                y_min = rail.a * mouse_x**2 + rail.b * mouse_x + rail.c - 10
                                y_max = rail.a * mouse_x**2 + rail.b * mouse_x + rail.c + 10
                                x_min = min(rail.xA, rail.xB) - 8
                                x_max = max(rail.xA, rail.xB) + 8
                            if x_min <= mouse_x <= x_max and y_min <= mouse_y <= y_max:
                                souhait_achat = True
                                rail_souhaite = rail


            # Display flags on the rails bought
            for rail in self.rails:
                if rail.possession is not None:
                    image = pygame.image.load("./images/drapeau.png").convert_alpha()
                    image = pygame.transform.scale(image, (25, 25))
                    ihm.dessiner_image(image, rail.xD, rail.yD, rail.possession.couleur_joueur)

            # Display action buttons
            ihm.dessiner_bouton("Draw", 0, 40, 100, 25, ihm.couleurs["bleu clair"])
            ihm.dessiner_bouton("End of turn", largeur - 100, hauteur - 25, 100, 25, ihm.couleurs["bleu clair"])

            if self.destinations != []:
                ihm.dessiner_bouton("Draw Destination", 0, hauteur-30, 150, 30, ihm.couleurs["bleu clair"])
            else:
                ihm.dessiner_bouton("More destinations", 0, hauteur-30, 150, 30, ihm.couleurs["gris"])

            if self.mute:
                ihm.dessiner_bouton("Mute", largeur - 45, hauteur - 70, 40, 40, ihm.couleurs["vert"])
            else:
                ihm.dessiner_bouton("Mute", largeur - 45, hauteur - 70, 40, 40, ihm.couleurs["rouge"])


            # Display deck overlay if button was pressed
            if afficher_cartes:
                if jouer_son:
                    ihm.jouer_son('./sons/main-cartes.wav', self.mute)
                    jouer_son = False
                ihm.fenetre_cartes(largeur, hauteur, joueur)
            else:
                jouer_son = True
    
            ihm.dessiner_bouton("Deck", 0, 0, 100, 25, (0, 128, 255))

            # Display draw cards overlay
            if souhait_pioche:
                souhait_pioche, changer_carte = ihm.fenetre_pioche(self.pioche, self.cartes_revelees, joueur, largeur, hauteur, nb_carte_prise < 2)
                if changer_carte == 2:
                    self.cartes_revelees.append(self.pioche.pop())
                if changer_carte >= 1:
                    if len(self.pioche) == 0:
                        self.pioche = self.cartes_complet.copy()
                        random.shuffle(self.pioche)
                        print("shuffle")

                    ihm.jouer_son('sons/pioche.wav', self.mute)
                    nb_carte_prise += 1
                    nb_rail_achete = 1
                    nb_dest_prise = 1


            # Display buy rail overlay
            if souhait_achat:
                souhait_achat, a_achete = ihm.fenetre_achat(rail_souhaite, joueur, largeur, hauteur, self.mute, nb_rail_achete < 1)
                if a_achete:
                    self.rails_restants.remove(rail_souhaite)
                    nb_rail_achete = 1
                    nb_carte_prise = 2
                    nb_dest_prise = 1

             # Last turn
            if joueur.wagons_restants <= 2 and self.dernier_joueur is None:
                self.dernier_joueur = joueur
                dernier_tour = self.tour+1

            # End of the game? Subtract the points from the remaining destinations and award 10 points to the player with the longest route
            if (joueur == self.dernier_joueur and self.tour == dernier_tour) or self.rails_restants == []:
                plus_long_chemin = (self.joueurs[0], self.joueurs[0].plus_long_chemin())
                for j in self.joueurs:
                    long_chemin = j.plus_long_chemin()
                    if long_chemin > plus_long_chemin[1]:
                        plus_long_chemin = (j, long_chemin)
                    for dest in j.destination:
                        j.score -= dest.points
                        print(j.pseudo + " lost " + str(dest))
                print("The longest railway is from " + str(plus_long_chemin[1]) + " for " + plus_long_chemin[0].pseudo)
                plus_long_chemin[0].score += 10
                pygame.quit()
                self.end()

            # Update screen
            pygame.display.flip()

        # Quit game
        pygame.quit()
        exit()

    def start(self):
        """
        Displays the player selection screen and starts the game.
        """
        pygame.init()
        pygame.mixer.init()
        largeur, hauteur = self.dimension
        screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("Ticket to ride")

        ihm = IHM(self, screen) # GUI init

        running = True

        nb_joueur = 3

        couleur_bouton = [ihm.couleurs["bleu clair"]]*nb_joueur

        couleur_bouton_ia = [ihm.couleurs["gris"]]*5

        pseudos = ["name"]*nb_joueur

        ia = [False]*3

        niveau_ia = 1
        niveau_ia_texte = ["beginner", "intermediate", "expert"]

        couleurs_joueurs = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0)]

        selected = [False]*nb_joueur

        y = 115


        while running:
            screen.fill(ihm.couleurs["noir"])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # buttons : add players, AI difficulty...
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if 220 <= mouse_x <= 250 and 55 <= mouse_y <= 85:
                        if nb_joueur > 2:
                            nb_joueur -= 1
                            couleur_bouton.pop()
                            selected.pop()
                            pseudos.pop()
                            ia.pop()
                    elif 310 <= mouse_x <= 340 and 55 <= mouse_y <= 85:
                        if nb_joueur < 5:
                            nb_joueur += 1
                            couleur_bouton.append(ihm.couleurs["bleu clair"])
                            selected.append(False)
                            pseudos.append("nom")
                            ia.append(False)

                    for i in range(nb_joueur):
                        if 125 <= mouse_x <= 225 and y-5+i*50 <= mouse_y <= y-5+i*50 + 30:
                            couleur_bouton[i] = ihm.couleurs["blanc"]
                            selected[i] = True
                            text = pseudos[i]
                        else:
                            couleur_bouton[i] = ihm.couleurs["bleu clair"]
                            selected[i] = False

                        if 250 <= mouse_x <= 300 and y-5+i*50 <= mouse_y <= y-5+i*50 + 30:
                            if ia[i]:
                                couleur_bouton_ia[i] = ihm.couleurs["gris"]
                                ia[i] = False
                            else:
                                couleur_bouton_ia[i] = ihm.couleurs["vert"]
                                ia[i] = True


                    if 160 <= mouse_x <= 180 and y+295 <= mouse_y <= y+295 + 30:
                        if niveau_ia > 0:
                            niveau_ia -= 1

                    elif 290 <= mouse_x <= 320 and y+295 <= mouse_y <= y+295 + 30:
                        if niveau_ia < len(niveau_ia_texte) - 1:
                            niveau_ia += 1
                
                    # Start a game with the selected settings
                    elif largeur - 100 <= mouse_x <= largeur - 20 and hauteur - 50 <= mouse_y <= hauteur - 10:
                            joueurs = []
                            ia_joueur = []
                            for i in range(nb_joueur):
                                if not ia[i]:
                                    joueurs.append(Joueur(couleurs_joueurs[i], pseudos[i], self.villes))
                                else:
                                    if niveau_ia == 0:
                                        ia_joueur.append(IA_aleatoire(couleurs_joueurs[i], pseudos[i], self.villes, self.cartes_complet))
                                    elif niveau_ia == 1:
                                        ia_joueur.append(IA_capitaliste(couleurs_joueurs[i], pseudos[i], self.villes, self.cartes_complet))
                                    else:
                                        ia_joueur.append(IA_objectif(couleurs_joueurs[i], pseudos[i], self.villes, self.cartes_complet))
                                    joueurs.append(ia_joueur[-1])
                            self.joueurs = joueurs
                            self.ia = ia_joueur
                            pygame.quit()
                            self.main()
                            
                # Write usernames
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif event.key == pygame.K_RETURN:
                        for i in range(nb_joueur):
                            if selected[i]:
                                couleur_bouton[i] = ihm.couleurs["bleu clair"]
                                selected[i] = False
                    else:
                        text += event.unicode

                    for i in range(nb_joueur):
                        if selected[i]:
                            pseudos[i] = text

            ihm.dessiner_texte("Select the number of players", 10, 10, ihm.couleurs["blanc"], 30)

            ihm.dessiner_texte("Number of players : ", 10, 60, ihm.couleurs["blanc"], 30)

            ihm.dessiner_bouton("<", 220, 55, 30, 30, ihm.couleurs["bleu clair"])
            ihm.dessiner_bouton(str(nb_joueur), 255, 55, 50, 30, ihm.couleurs["blanc"])
            ihm.dessiner_bouton(">", 310, 55, 30, 30, ihm.couleurs["bleu clair"])

            for i in range(nb_joueur):
                ihm.dessiner_texte("Player " + str(i+1) + ":", 20, y+i*50, couleurs_joueurs[i], 30)
                ihm.dessiner_bouton(pseudos[i], 125, y-5+i*50, 100, 30, couleur_bouton[i])
                ihm.dessiner_bouton("AI", 250, y-5+i*50, 50, 30, couleur_bouton_ia[i])

            ihm.dessiner_texte("AI difficulty :", 10, y+300, ihm.couleurs["blanc"], 30)
            ihm.dessiner_bouton("<", 160, y+295, 30, 30, ihm.couleurs["bleu clair"])
            ihm.dessiner_bouton(niveau_ia_texte[niveau_ia], 195, y+295, 90, 30, ihm.couleurs["blanc"])
            ihm.dessiner_bouton(">", 290, y+295, 30, 30, ihm.couleurs["bleu clair"])


            ihm.dessiner_bouton("Play", largeur - 100, hauteur - 50, 80, 40, ihm.couleurs["vert"])

            pygame.display.flip()
        pygame.quit()
        exit()

    def end(self):
        """
        Displays the end-of-game screen with the scores and offers the option to play again.
        """
        pygame.init()
        pygame.mixer.init()
        largeur, hauteur = self.dimension
        screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("Ticket to ride")

        ihm = IHM(self, screen) # GUI init

        running = True

        print("Game ended")

        while running:
            screen.fill(ihm.couleurs["noir"])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    # Restart a game
                    if largeur - 100 <= mouse_x <= largeur and hauteur - 50 <= mouse_y <= hauteur:
                        self.__init__(self.dimension)
                        pygame.quit()
                        self.start()

            ihm.dessiner_bouton("Play again", largeur - 100, hauteur - 50, 80, 40, ihm.couleurs["vert"])

            ihm.dessiner_texte("The game ended in " + str(self.tour) + " turns", 10, 10, ihm.couleurs["blanc"], 30)
            ihm.dessiner_texte("Scores :", 10, 60, ihm.couleurs["blanc"], 30)
            y = 100
            for joueur in self.joueurs:
                ihm.dessiner_texte(joueur.pseudo + " : " + str(max(0,joueur.score)) + " points", 10, y, joueur.couleur_joueur, 30)
                y += 40

            gagnant = max(self.joueurs, key=lambda j: j.score)

            ihm.dessiner_texte("The winner is " + gagnant.pseudo + " !", 10, y, ihm.couleurs["blanc"], 30)

            pygame.display.flip()
        pygame.quit()
        exit()
            
                    



# The game starts with 3 players (red, blue and green) on a 1100 by 800 screen
if __name__ == "__main__":
    jeu = Jeu((1100, 800))
    jeu.start()