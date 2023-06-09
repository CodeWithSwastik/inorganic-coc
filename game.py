from compounds import COMPOUNDS, ELEMENTS, REACTIONS
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
    Quest("Create a Linear compound", 20, lambda c: c.shape == "Linear"),
    Quest("Create a Bent (V shaped) compound", 30, lambda c: c.shape == "Bent"),
    Quest("Create a Tetrahedral compound", 30, lambda c: c.shape == "Tetrahedral"),
    Quest("Create a Planar compound", 30, lambda c: c.shape == "Planar"),
    Quest("Create a Trigonal Pyramidal compound", 30, lambda c: c.shape == "Trigonal Pyramidal"),
    Quest("Create a compound with only s block elements", 20, lambda c: all(e.block=="s" for e in c.elements)),
    Quest("Create a compound with only p block elements", 20, lambda c: all(e.block=="p" for e in c.elements)),
    Quest("Create a compound with all elements being more electronegative than Nitrogen", 30, lambda c: all(e.electronegativity > 3.04 for e in c.elements)),
    Quest("Create a compound with a Noble Gas", 10, lambda c: any(e.group=="Noble Gas" for e in c.elements)),
    Quest("Create a compound with only Chalcogens", 10, lambda c: all(e.group=="Chalcogen" for e in c.elements)),
    Quest("Create a compound with only Halogens", 10, lambda c: all(e.group=="Halogen" for e in c.elements)),
    Quest("Create a compound with no period 2 elements", 10, lambda c: all(e.period!=2 for e in c.elements)),
]

class Game:
    def __init__(self, players = None, rounds = 3) -> None:
        
        self.players = []
        self.leaderboard = {}
        self.inventory = {}
        self.compound_inventory = {}
        self.rounds = rounds
        self.current_round = 1
        self.winner = None

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
        self.compound_inventory[player] = []


    def add_atom(self, player = None):
        atom = random.choices(list(ELEMENTS), weights=[1/e.score for e in ELEMENTS.values()], k=1)[0]
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
        
        comp = COMPOUNDS[compound]
        constituents = comp.constituents
        for c in constituents:
            for _ in range(constituents[c]):
                self.inventory[player].remove(c)
        
        
        return self._player_created_compound(player, comp)
        
    def _can_create_compound(self, compound, player):
        constituents = COMPOUNDS[compound].constituents
        for c in constituents:
            if self.inventory[player].count(c) < constituents[c]:
                return False
            
        return True

    def _player_created_compound(self, player, compound):
        if compound.formula not in self.compound_inventory[player]:
            self.compound_inventory[player].append(compound.formula)

        if compound.formula in self.created_compounds:
            return 0, []
        
        points = compound.score
        completed_quests = []
        for quest in self.active_quests:
            if quest.evaluate(compound):
                points += quest.points
                quest.active = False
                completed_quests.append(quest)
                quests = [g for g in DEFAULT_QUESTS if g.active and g not in self.quests]
                if quests:
                    self.quests.append(random.choice(quests))

        self.leaderboard[player] += points
        self.created_compounds.append(compound.formula)
        return compound.score, completed_quests

    def do_reaction(self, reactants, player = None):
        player = player or self.current_turn
        if any(r not in self.compound_inventory[player] for r in reactants):
            raise Exception("You haven't yet created compounds that you are trying to react!")

        rxn = REACTIONS.find_reaction_with_reactants(reactants)
        if rxn is None:
            raise Exception("Those compounds didn't react!")
        
        res = {}
        for p in rxn.products:
            res[p] = self._player_created_compound(player, p)
        
        return rxn, res

    def next_turn(self):
        for i in range(3):
            self.add_atom()

        x = self.players.index(self.current_turn)

        self.current_turn = self.players[(x + 1) % len(self.players)]
        if self.current_turn == self.players[0]:
            if self.current_round < self.rounds:
                self.current_round += 1
            else:
                self.running = False
                self.winner = list(self.sorted_leaderboard)[0]
        
        return self.current_turn

    @property
    def sorted_leaderboard(self):
        return dict(sorted(self.leaderboard.items(), key=lambda item: item[1], reverse=True))
    
    def start(self):
        self.running = True
        self.current_turn = self.players[0]
        for p in self.players:
            for _ in range(6):
                self.add_atom(p)