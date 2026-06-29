"""
Module ihm
==========

Ce module gère l'interface graphique du jeu avec Pygame.
Il fournit la classe IHM pour l'affichage des éléments du jeu, la gestion des boutons,
l'affichage des cartes, des rails, et la gestion des fenêtres d'achat et de pioche.

Auteur : Evann MICHEL
"""

import pygame

class IHM:
    """
    Classe gérant l'interface graphique du jeu.

    Attributs :
        jeu : Instance du jeu.
        fenetre : Surface Pygame de la fenêtre principale.
        couleurs : Dictionnaire de couleurs utilisées dans l'interface.
    """
    def __init__(self, jeu, screen):
        """
        Initialise l'interface graphique.

        Args:
            jeu : Instance du jeu.
            screen : Surface Pygame de la fenêtre principale.
        """
        self.jeu = jeu
        self.fenetre = screen

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
        Joue un son si le mode muet n'est pas activé.

        Args:
            fichier (str): Chemin du fichier son à jouer.
            mute (bool): True si le son doit être coupé, False sinon.
        """
        if not mute:
            sound = pygame.mixer.Sound(fichier)
            pygame.mixer.Sound.play(sound)

    def dessiner_bouton(self, texte, x, y, largeur, hauteur, couleur):
        """
        Dessine un bouton rectangulaire avec du texte.
        Ne vérigie pas si le bouton est cliqué, juste l'affiche.

        Args:
            texte (str): Texte à afficher sur le bouton.
            x (int): Position horizontale.
            y (int): Position verticale.
            largeur (int): Largeur du bouton.
            hauteur (int): Hauteur du bouton.
            couleur (tuple): Couleur RGB du bouton.
        """
        pygame.draw.rect(self.fenetre, couleur, (x, y, largeur, hauteur))
        font = pygame.font.Font(None, 20)
        text_surface = font.render(texte, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(x + largeur // 2, y + hauteur // 2))
        self.fenetre.blit(text_surface, text_rect)
    
    def dessiner_texte(self, texte, x, y, couleur, taille):
        """
        Dessine du texte à une position donnée.

        Args:
            texte (str): Texte à afficher.
            x (int): Position horizontale.
            y (int): Position verticale.
            couleur (tuple): Couleur RGB du texte.
            taille (int): Taille de la police.
        """
        font = pygame.font.Font(None, taille)
        text_surface = font.render(texte, True, couleur)
        self.fenetre.blit(text_surface, (x, y))

    def dessiner_image(self, image, x, y, couleur):
        """
        Dessine une image à une position donnée, teintée d'une couleur.

        Args:
            image (pygame.Surface): Image à afficher.
            x (int): Position horizontale.
            y (int): Position verticale.
            couleur (tuple): Couleur RGB à appliquer à l'image.
        """
        image.fill(couleur, special_flags=pygame.BLEND_RGBA_MULT)
        self.fenetre.blit(image, (x, y))

    def dessiner_cartes(self, cartes, taille_carte, largeur, hauteur, besoin_coords=False):
        """
        Affiche une liste de cartes sur la fenêtre, redimensionnées et espacées.

        Args:
            cartes (list): Liste de cartes à afficher.
            taille_carte (tuple): Dimensions (largeur, hauteur) d'une carte.
            largeur (int): Largeur de la fenêtre.
            hauteur (int): Hauteur de la fenêtre.
            besoin_coords (bool): Si True, retourne les coordonnées des cartes.

        Returns:
            list: Liste des coordonnées des cartes si besoin_coords est True, sinon None.
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
        Affiche la fenêtre des cartes du joueur (wagons et destinations).

        Args:
            largeur (int): Largeur de la fenêtre.
            hauteur (int): Hauteur de la fenêtre.
            joueur (Joueur): Joueur dont on affiche les cartes.
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
        Affiche la fenêtre d'achat d'un rail et gère la sélection des cartes.

        Args:
            rail (Rail): Rail à acheter.
            joueur (Joueur): Joueur effectuant l'achat.
            largeur (int): Largeur de la fenêtre.
            hauteur (int): Hauteur de la fenêtre.
            mute (bool): True si le son est coupé.
            peut_achete (bool): True si l'achat est autorisé ce tour-ci.
            cartes_select (list): Cartes déjà sélectionnées pour l'achat.

        Returns:
            tuple: (continuer (bool), achat_effectue (bool))
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
            self.dessiner_texte("Vous n'avez pas de carte de la couleur demandée.", largeur//4, 150, self.couleurs["rouge"], 30)
        else:
            coords_cartes = self.dessiner_cartes(cartes_possibles, taille_carte, largeur, hauteur, True)

        if not peut_achete:
            self.dessiner_texte("Pas plus de 2 cartes wagon, 1 destination ou 1 rail par tour", largeur//4, hauteur-150, self.couleurs["rouge"], 30)
        elif joueur.wagons_restants < rail.val:
            self.dessiner_texte("Vous n'avez pas assez de wagons pour acheter ce rail.", largeur//4, hauteur-150, self.couleurs["rouge"], 30)
        
        ok = True
        if rail.couleur == "gris" and len(cartes_select) >= 1:
            couleur = cartes_select[0][0].couleur
            for carte in cartes_select:
                if carte[0].couleur != couleur and carte[0].couleur != "arc-en-ciel":
                    ok = False

        self.dessiner_bouton("Retour", 0, 0, 100, 25, self.couleurs["bleu clair"])
        if len(cartes_select) != rail.val or not ok or joueur.wagons_restants < rail.val or not peut_achete:
            self.dessiner_bouton("Acheter", 100, hauteur - 100, largeur-200, 80, self.couleurs["gris"])
        else:
            self.dessiner_bouton("Acheter", 100, hauteur - 100, largeur-200, 80, self.couleurs["bleu clair"])

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
                        self.jouer_son('sons/money.wav', mute)
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
        Affiche la fenêtre de pioche de cartes wagons et gère la sélection.

        Args:
            pioche (list): Pile de cartes à piocher.
            cartes_revelees (list): Cartes visibles à piocher.
            joueur (Joueur): Joueur qui pioche.
            largeur (int): Largeur de la fenêtre.
            hauteur (int): Hauteur de la fenêtre.
            achat_possible (bool): True si la pioche est autorisée ce tour-ci.

        Returns:
            tuple: (continuer (bool), type_pioche (int))
                - continuer : False si retour, True sinon.
                - type_pioche : 0 (rien), 1 (pioche), 2 (cartes visibles)
        """
        overlay = pygame.Surface(self.jeu.dimension)
        overlay.set_alpha(150) 
        overlay.fill((0, 0, 0))
        self.fenetre.blit(overlay, (0, 0))

        self.dessiner_bouton("Retour", 0, 0, 100, 25, self.couleurs["bleu clair"])

        taille_carte = (150, 100)

        coords_cartes = self.dessiner_cartes(cartes_revelees, taille_carte, largeur, hauteur, True)

        xc, yc = coords_cartes[2][0], coords_cartes[2][1]

        self.dessiner_bouton("Pioche", xc, yc*3.5, taille_carte[0], taille_carte[1], self.couleurs["bleu clair"])

        if not achat_possible:
            self.dessiner_texte("Pas plus de 2 cartes wagons, 1 destination ou 1 rail par tour", largeur//4, yc*4.5 + taille_carte[1] + 10, self.couleurs["rouge"], 30)

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