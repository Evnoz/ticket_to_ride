# Ticket to ride in Python

An implementation of the famous board game *Ticket to Ride* in Python for an engineering school project.

In 2025, we had to create a game using Python and a list of constraints (subclasses, create tests...). This repository is the result of this project made by me and a classmate.


## What you can expect

This is a recreation of the famous board game [*Ticket to Ride*](https://www.daysofwonder.com/game/ticket-to-ride/) (North America edition) in Python. 

We tried to make it as faithful as possible. Thus, it contains many of the [original rules](https://cdn.svc.asmodee.net/production-daysofwonder/uploads/2025/07/7201N_TICKET2RIDEV2_RULES_EN_20250425_WEB.pdf):

- Each turn, you can buy a railway (a route between 2 cities), draw train cards (max 2) or draw a new destination (ticket).
- You gain points by buying a railway, completing a ticket or having the longest route at the end of the game.
- You can use locomotives (rainbow trains) as any train colour.
- You can buy grey railways with any same colour.

To make it even more realistic, tickets and train cards are the same as in the board game (same amount of each colour).

And, of course, all players have 45 trains to play the game. When a player has 2 or less trains left, it is the last turn. Then, all tickets left in a players hand deduct points and the player with the longest route gain 10 bonus points.

However, a few specific rules are not implemented here:

- The longest route does not take loops into account.
- You can have 3 or more locomotives face up without changing the cards.
- Double-routes are not implemented. You can only buy one railway between two cities.

Moreover, you can play with up to 4 friends (5 players) but if you don't have enough friends, fret not! You can play against AIs. We have 3 difficulties implemented:

- Easy: The AI just buy a random railway each turn.
- Intermediate: This one tries to buy the most expensive railways each turn. It likes to spend money.
- Expert: This one is the real deal. I will try to complete all of its tickets and more. Don't worry, it won't try to block other players' objectives, or not on purpose at least.


All of this can be played on a GUI using Pygame. Some sounds are implemented and you can buy railways by clicking directly on them.


## Installation instructions

You will need Pygame and Numpy to run the game.
To launch the game, just launch main.py
```bash
   python3 main.py
   ```
Have fun!

## What you can find here

As this is a school project, the variables and file names are written in French (my native language). However, comments and docs have been translated in English.

The detailed structure of the code can be found in the **docs directory**.
Here is a simplified structure of the different classes.

A series of simple unit tests are also available.

