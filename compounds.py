import json

class Element:
    def __init__(
            self, 
            symbol,
            name, 
            score,
            atomic_number, 
            group, 
            period, 
            block,
            electronegativity
        ) -> None:

        self.symbol = symbol
        self.name = name
        self.score = score
        self.atomic_number = atomic_number
        self.group = group
        self.period = period
        self.block = block
        self.electronegativity = electronegativity

    def __repr__(self) -> str:
        return f"<Element: {self.name} [{self.symbol}]>"
    
class Compound:
    def __init__(self, formula, constituents, shape) -> None:
        self.formula = formula
        self.constituents = constituents
        self.elements = [ELEMENTS[e] for e in self.constituents]
        self.shape = shape
        self.score = sum(e.score*self.constituents[e.symbol] for e in self.elements)

    def __repr__(self) -> str:
        return f"<Compound: {self.formula}>"
    
class Reaction:
    def __init__(self, reactants, products):
        self.reactants = [COMPOUNDS[i] for i in reactants]
        self.products = [COMPOUNDS[i] for i in products]


    def __repr__(self) -> str:
        return f"<Reaction: {self.reactants} -> {self.products}>"
    
class ReactionManager:
    def __init__(self) -> None:
        self.reaction_list = []

    def add(self, rxn):
        self.reaction_list.append(rxn)

    def find_reaction_with_reactants(self, *reactants):
        rxns = [r for r in self.reaction_list if set(c.formula for c in r.reactants) == set(reactants)]
        if rxns:
            return rxns[0]
        else:
            raise Exception("Invalid reaction.")
        
    
ELEMENTS = {}
with open("elements.json") as f:
    for symbol, data in json.load(f).items():
        ELEMENTS[symbol] = Element(
            symbol, 
            data["name"], 
            data["score"],
            data["Z"],
            data["group"],
            data["period"],
            data["block"],
            data["electronegativity"]
        )


COMPOUNDS = {}
with open("compounds.json") as f:
    for formula, data in json.load(f).items():
        COMPOUNDS[formula] = Compound(formula, data["Constituents"], data["Shape"])


REACTIONS = ReactionManager()

with open("reactions.json") as f:
    for data in json.load(f):
        r = Reaction(data["reactants"], data["products"])
        REACTIONS.add(r)