import json

class Element:
    def __init__(
            self, 
            symbol,
            name, 
            atomic_number, 
            group, 
            period, 
            block,
            electronegativity
        ) -> None:

        self.symbol = symbol
        self.name = name
        self.atomic_number = atomic_number
        self.group = group
        self.period = period
        self.block = block
        self.electronegativity = electronegativity

class Compound:
    def __init__(self, formula, constituents, shape) -> None:
        self.formula = formula
        self.constituents = constituents
        self.elements = [ELEMENTS[e] for e in self.constituents]
        self.shape = shape

ELEMENTS = {}
with open("elements.json") as f:
    for symbol, data in json.load(f).items():
        ELEMENTS[symbol] = Element(
            symbol, 
            data["name"], 
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

