"""
IHM module
==========

This module manages the game’s graphical user interface (GUI) using Pygame.
It provides the IHM (=Interface Homme machine/Human-machine interface) class for displaying game elements, managing buttons,
displaying cards and rails, and managing the purchase and draw windows.

Author: Evann MICHEL
"""

import pygame

class IHM:
    """
    Class managing the game’s GUI.
    """
    def __init__(self, jeu, screen):
        """
        Initialises the GUI.

        Args:
            jeu: Game instance.
            screen: Pygame canvas for the main window.
        """
        self.jeu = jeu
        self.fenetre = screen

        # colours for the GUI
        self.couleurs = {
            "rouge": (255, 0, 0),
            "bleu": (0, 0, 255),
            "vert": (0, 255, 0),
            "noir": (0, 0, 0),
            "blanc": (255, 255, 255),
            "gris": (128, 128, 128),
            "jaune": (255, 255, 0),
            "orange": (255, 165, 0),
            "rose": (255, 192, 203),
            "bleu clair": (0, 128, 255),
            "gris clair": (200, 200, 200)
        }

    def jouer_son(self, fichier, mute):
        """
        Plays a sound if mute mode is not enabled.

        Args:
            fichier (str): Path to the sound file to be played.
            mute (bool): True if the sound is to be muted, False otherwise.
        """
        if not mute:
            sound = pygame.mixer.Sound(fichier)
            pygame.mixer.Sound.play(sound)

    def dessiner_bouton(self, texte, x, y, largeur, hauteur, couleur):
        """
        Draw a rectangular button with text.
        Do not check whether the button has been clicked; just display it.

        Args:
            texte (str): Text to display on the button.
            x (int): Horizontal position.
            y (int): Vertical position.
            largeur (int): Width of the button.
            hauteur (int): Height of the button.
            couleur (tuple): RGB colour of the button.
        """
        pygame.draw.rect(self.fenetre, couleur, (x, y, largeur, hauteur))
        font = pygame.font.Font(None, 20)
        text_surface = font.render(texte, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(x + largeur // 2, y + hauteur // 2))
        self.fenetre.blit(text_surface, text_rect)
    
    def dessiner_texte(self, texte, x, y, couleur, taille):
        """
        Write text at a given position.

        Args:
            texte (str): Text to display.
            x (int): Horizontal position.
            y (int): Vertical position.
            couleur (tuple): RGB colour of the text.
            taille (int): Font size.
        """
        font = pygame.font.Font(None, taille)
        text_surface = font.render(texte, True, couleur)
        self.fenetre.blit(text_surface, (x, y))

    def dessiner_image(self, image, x, y, couleur):
        """
        Draws an image at a given position, tinted with a colour.

        Args:
            image (pygame.Surface): The image to display.
            x (int): Horizontal position.
            y (int): Vertical position.
            couleur (tuple): The RGB colour to apply to the image.
        """
        image.fill(couleur, special_flags=pygame.BLEND_RGBA_MULT)
        self.fenetre.blit(image, (x, y))

    def dessiner_cartes(self, cartes, taille_carte, largeur, hauteur, besoin_coords=False):
        """
        Displays a list of cards in the window, resized and spaced out.

        Args:
            cartes (list): List of cards to display.
            taille_carte (tuple): Dimensions (width, height) of a card.
            largeur (int): Width of the window.
            hauteur (int): Height of the window.
            besoin_coords (bool): If True, returns the coordinates of the cards.

        Returns:
            list: A list of the coordinates of the maps if `besoin_coords` is True; otherwise, None.
        """
        max_cartes = largeur // (taille_carte[0] + 20)
        coords_cartes = []
        j = 0
        for i, carte in enumerate(cartes):
            image_redimensionnee = pygame.transform.scale(carte.image, taille_carte)
            x = taille_carte[0]/2 + j * (taille_carte[0] + 20)
            y = taille_carte[1]/2 + i//max_cartes * (taille_carte[1] + 20)
            if besoin_coords:
                coords_cartes.append((x, y))
            j += 1
            if j >= max_cartes:
                j = 0
            self.fenetre.blit(image_redimensionnee, (x, y))
        if besoin_coords:
            return coords_cartes

    def fenetre_cartes(self, largeur, hauteur, joueur):
        """
        Displays the player’s cards window (train cars and destinations).

        Args:
            largeur (int): Width of the window.
            hauteur (int): Height of the window.
            joueur (Joueur): The player whose cards are being displayed.
        """
        overlay = pygame.Surface((largeur, hauteur))
        overlay.set_alpha(150) 
        overlay.fill((0, 0, 0))
        self.fenetre.blit(overlay, (0, 0))

        taille_carte = (150, 100)
        cartes = joueur.cartes
        self.dessiner_cartes(cartes, taille_carte, largeur, hauteur)
        for i in range(len(joueur.destination)):
            self.dessiner_texte(joueur.destination[i].__str__(), 10, hauteur - 30 - i * 30, self.couleurs["blanc"], 35)

    def fenetre_achat(self, rail, joueur, largeur, hauteur, mute, peut_achete, cartes_select=[]):
        """
        Displays the railway purchase window and manages card selection.

        Args:
            rail (Track): The track to be purchased.
            joueur (Joueur): The player making the purchase.
            largeur (int): Width of the window.
            hauteur (int): Height of the window.
            mute (bool): True if the sound is muted.
            peut_achete (bool): True if the purchase is permitted this turn.
            cartes_select (list): Cards already selected for purchase.

        Returns:
            tuple: (continue (bool), purchase_completed (bool))
        """
        overlay = pygame.Surface(self.jeu.dimension)
        overlay.set_alpha(150) 
        overlay.fill((0, 0, 0))
        self.fenetre.blit(overlay, (0, 0))
        self.dessiner_texte(str(rail), largeur//4, 10, self.couleurs["blanc"], 30)

        taille_carte = (150, 100)

        if rail.couleur == "gris":
            cartes_possibles = joueur.cartes.copy()
        else:
            cartes_possibles = [carte for carte in joueur.cartes if carte.couleur == rail.couleur or carte.couleur == "arc-en-ciel"]

        for carte, x, y in cartes_select:
            largeur_select = taille_carte[0] + 2*taille_carte[0]//20
            hauteur_select = taille_carte[1] + 2*taille_carte[1]//20
            self.dessiner_bouton("", x-taille_carte[0]//20, y-taille_carte[1]//20, largeur_select, hauteur_select, self.couleurs["gris clair"])

        if not cartes_possibles:
            self.dessiner_texte("You don’t have any cards of the colour requested.", largeur//4, 150, self.couleurs["rouge"], 30)
        else:
            coords_cartes = self.dessiner_cartes(cartes_possibles, taille_carte, largeur, hauteur, True)

        if not peut_achete:
            self.dessiner_texte("No more than 2 train car cards, 1 destination or 1 rail per turn", largeur//4, hauteur-150, self.couleurs["rouge"], 30)
        elif joueur.wagons_restants < rail.val:
            self.dessiner_texte("You don't have enough train cars to buy this railway.", largeur//4, hauteur-150, self.couleurs["rouge"], 30)
        
        ok = True
        if rail.couleur == "gris" and len(cartes_select) >= 1:
            couleur = cartes_select[0][0].couleur
            for carte in cartes_select:
                if carte[0].couleur != couleur and carte[0].couleur != "arc-en-ciel":
                    ok = False

        self.dessiner_bouton("Back", 0, 0, 100, 25, self.couleurs["bleu clair"])
        if len(cartes_select) != rail.val or not ok or joueur.wagons_restants < rail.val or not peut_achete:
            self.dessiner_bouton("Buy", 100, hauteur - 100, largeur-200, 80, self.couleurs["gris"])
        else:
            self.dessiner_bouton("Buy", 100, hauteur - 100, largeur-200, 80, self.couleurs["bleu clair"])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if 0 <= mouse_x <= 100 and 0 <= mouse_y <= 25:
                    cartes_select.clear()
                    return False, False
                elif 100 <= mouse_x <= largeur-100 and hauteur - 100 <= mouse_y <= hauteur - 20:
                    if len(cartes_select) == rail.val and ok and joueur.wagons_restants >= rail.val and peut_achete:
                        self.jouer_son('./sons/money.wav', mute)
                        rail.achat(joueur, cartes_select)
                        cartes_select.clear()
                        return False, True

                elif cartes_possibles:
                    for i, (x, y) in enumerate(coords_cartes):
                        carte = (cartes_possibles[i],x,y)
                        if x <= mouse_x <= x + taille_carte[0] and y <= mouse_y <= y + taille_carte[1]:
                                if carte in cartes_select:
                                    cartes_select.remove(carte)
                                else:
                                    cartes_select.append(carte)

        return True, False

    def fenetre_pioche(self, pioche, cartes_revelees, joueur, largeur, hauteur, achat_possible):
        """
        Displays the train cards draw window and manages the selection.

        Args:
            pioche (list): Stack of cards to be drawn from.
            cartes_revelees (list): Visible cards to be drawn from.
            joueur (Joueur): The player drawing cards.
            largeur (int): Width of the window.
            hauteur (int): Height of the window.
            achat_possible (bool): True if drawing is permitted this turn.

        Returns:
            tuple: (continue (bool), draw_type (int))
                - continuer: False if 'back' button pressed, True otherwise.
                - type_pioche: 0 (none), 1 (draw), 2 (face-up cards)
        """
        overlay = pygame.Surface(self.jeu.dimension)
        overlay.set_alpha(150) 
        overlay.fill((0, 0, 0))
        self.fenetre.blit(overlay, (0, 0))

        self.dessiner_bouton("Back", 0, 0, 100, 25, self.couleurs["bleu clair"])

        taille_carte = (150, 100)

        coords_cartes = self.dessiner_cartes(cartes_revelees, taille_carte, largeur, hauteur, True)

        xc, yc = coords_cartes[2][0], coords_cartes[2][1]

        self.dessiner_bouton("Draw", xc, yc*3.5, taille_carte[0], taille_carte[1], self.couleurs["bleu clair"])

        if not achat_possible:
            self.dessiner_texte("No more than 2 cards, 1 destination or 1 railway per turn!", largeur//4, yc*4.5 + taille_carte[1] + 10, self.couleurs["rouge"], 30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if 0 <= mouse_x <= 100 and 0 <= mouse_y <= 25:
                    return False, 0
                elif xc <= mouse_x <= xc + taille_carte[0] and yc*3.5 <= mouse_y <= yc*3.5 + taille_carte[1] and achat_possible:
                    carte = pioche.pop()
                    joueur.cartes.append(carte)
                    joueur.couleurs[carte.couleur] += 1
                    return True, 1

                for i, (x, y) in enumerate(coords_cartes):
                    carte = cartes_revelees[i]
                    if x <= mouse_x <= x + taille_carte[0] and y <= mouse_y <= y + taille_carte[1] and achat_possible:
                        joueur.cartes.append(carte)
                        joueur.couleurs[carte.couleur] += 1
                        cartes_revelees.remove(carte)
                        return True, 2

        return True, 0