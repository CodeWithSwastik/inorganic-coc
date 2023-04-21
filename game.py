from compounds import COMPOUNDS, ELEMENTS
import random

class Quest:
    def __init__(self, objective, points, eval_fn) -> None:
        self.objective = objective
        self.points = points
        self._eval = eval_fn

        self.active = True

    def evaluate(self, compound):
        return self.active and self._eval(compound)
    

DEFAULT_QUESTS = [
    Quest("Create a Linear compound!", 20, lambda c: c.shape == "Linear"),
    Quest("Create a Bent (V shaped) compound!", 30, lambda c: c.shape == "Bent"),
    Quest("Create a Tetrahedral compound!", 30, lambda c: c.shape == "Tetrahedral"),
    Quest("Create a Non Planar compound!", 30, lambda c: c.shape == "Non Planar"),
    Quest("Create a Planar compound!", 30, lambda c: c.shape == "Planar"),
    Quest("Create a Trigonal Pyramidal compound!", 30, lambda c: c.shape == "Trigonal Pyramidal"),
    Quest("Create a compound with only s block elements!", 20, lambda c: all(e.block=="s" for e in c.elements)),
    Quest("Create a compound with only p block elements!", 20, lambda c: all(e.block=="p" for e in c.elements)),
    Quest("Create a compound with all elements being more electronegative than Nitrogen!", 30, lambda c: all(e.electronegativity > 3.04 for e in c.elements)),
]

class Game:
    def __init__(self, players = None) -> None:
        
        self.players = []
        self.leaderboard = {}
        self.inventory = {}
        
        if players is not None:
            for p in players:
                self.add_player(p)
        
            self.current_turn = self.players[0]
        else:
            self.current_turn = None

        self.running = False
        self.created_compounds = []

        random.shuffle(DEFAULT_QUESTS)
        self.quests = DEFAULT_QUESTS[:3]

    @property
    def active_quests(self):
        return [g for g in self.quests if g.active]
    
    def add_player(self, player):
        self.players.append(player)
        self.leaderboard[player] = 0
        self.inventory[player] = []


    def add_atom(self, player = None):
        ATOMS = list(ELEMENTS)
        atom = random.choice(ATOMS)
        player = player or self.current_turn
        self.inventory[player].append(atom)
        return atom
    
    def create_compound(self, compound, player = None):
        player = player or self.current_turn
        if compound not in COMPOUNDS:
            raise Exception("Invalid Compound!")
        
        if not self._can_create_compound(compound, player):
            raise Exception("You don't have enough atoms to make that compound!")

        if compound in self.created_compounds:
            raise Exception("That compound has already been made by someone before!")
        
        constituents = COMPOUNDS[compound].constituents
        total_atoms_used = 0
        for c in constituents:
            total_atoms_used += constituents[c]
            for _ in range(constituents[c]):
                self.inventory[player].remove(c)
        
        points = total_atoms_used*10
        completed_quests = []
        for quest in self.active_quests:
            if quest.evaluate(COMPOUNDS[compound]):
                points += quest.points
                quest.active = False
                completed_quests.append(quest)
                quests = [g for g in DEFAULT_QUESTS if g.active and g not in self.Quests]
                if quests:
                    self.Quests.append(random.choice(quests))

        self.leaderboard[player] += points
        self.created_compounds.append(compound)
        return total_atoms_used*10, completed_quests
        
    def _can_create_compound(self, compound, player):
        constituents = COMPOUNDS[compound].constituents
        for c in constituents:
            if self.inventory[player].count(c) < constituents[c]:
                return False
            
        return True

    def next_turn(self):
        for i in range(3):
            self.add_atom()

        self.current_turn = self.players[(self.players.index(self.current_turn) + 1) % len(self.players)]
        return self.current_turn

    def start(self):
        self.running = True
        self.current_turn = self.players[0]
        for p in self.players:
            for _ in range(6):
                self.add_atom(p)