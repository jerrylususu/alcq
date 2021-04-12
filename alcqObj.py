# formula and or not
# forall exists (tbox)
# concept, primitive concept, defined concept
# relation
# assertion, concept assertion, relation assertion
# abox, tbox
# constant, top, bottom

from typing import Union, Set, List

class DCConstant(object):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"DConstant({self.name!r})"

    def __eq__(self, other):
        return isinstance(other, DCConstant) and self.name == other.name

    def __hash__(self):
        return hash(self.__repr__())

class DCTop(DCConstant):
    def __init__(self):
        DCConstant.__init__(self, "Top")

    def __repr__(self):
        return "⊤"


class DCBottom(DCConstant):
    def __init__(self):
        DCConstant.__init__(self, "Bottom")

    def __repr__(self):
        return "⊥"


Top = DCTop()
Bottom = DCBottom()


class Constant(object):
    """
    Individual
    """
    def __init__(self, name:str):
        self.name = name

    def __repr__(self):
        return f"CS({self.name!r})"

    def __eq__(self, other):
        return isinstance(other, Constant) and self.name == other.name

    def __hash__(self):
        return hash(self.__repr__())


class Concept(object):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Concept({self.name!r})"

    def __call__(self, obj: Constant, *args, **kwargs):
        return ConceptAssertion(self, obj)

    def __hash__(self):
        return hash(self.__repr__())


class Formula(object):
    def __init__(self):
        pass

    def __call__(self, obj:Constant, *args, **kwargs):
        return ComplexAssertion(self, obj)

    def __hash__(self):
        return hash(self.__repr__())


class PrimitiveConcept(Concept, Formula):
    def __init__(self, name: str):
        Concept.__init__(self, name)

    def __repr__(self):
        return f"PC({self.name!r})"

    def __eq__(self, other):
        return isinstance(other, PrimitiveConcept) and self.name == other.name

    def __hash__(self):
        return Concept.__hash__(self)


class Relation(object):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"R({self.name!r})"

    def __call__(self, obj1: Constant, obj2: Constant,*args, **kwargs):
        return RelationAssertion(self, obj1, obj2)

    def __eq__(self, other):
        return isinstance(other, Relation) and self.name == other.name

    def __hash__(self):
        return hash(self.__repr__())


class Operator(Formula):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __hash__(self):
        return hash(self.__repr__())


# class Formula(object):
#     def __init__(self, content: Union[PrimitiveConcept, Operator]):
#         self.content = content
#
#     def __repr__(self):
#         return f"{self.content!r}"





class DefinedConcept(Concept, Formula):
    def __init__(self, name: str, defn: Formula):
        Concept.__init__(self, name)
        self.definition = defn

    def __repr__(self):
        return f"DC({self.name}: {self.definition})"

    def __eq__(self, other):
        return isinstance(other, DefinedConcept) and self.name == other.name and self.definition == other.definition

    def __hash__(self):
        return Concept.__hash__(self)


class And(Operator):
    def __init__(self, param1:Formula, param2:Formula):
        Operator.__init__(self, "And")
        self.param1 = param1
        self.param2 = param2

    def __repr__(self):
        return f"And({self.param1!r}, {self.param2!r})"

    def __eq__(self, other):
        return isinstance(other, And) and ( (self.param1 == other.param1 and self.param2 == other.param2)  or (self.param1 == other.param2 and self.param2== other.param1) )

    def __hash__(self):
        return Operator.__hash__(self)


class Or(Operator):
    def __init__(self, param1:Formula, param2:Formula):
        Operator.__init__(self, "Or")
        self.param1 = param1
        self.param2 = param2

    def __repr__(self):
        return f"Or({self.param1!r}, {self.param2!r})"

    def __eq__(self, other):
        return isinstance(other, Or) and ( (self.param1 == other.param1 and self.param2 == other.param2)  or (self.param1 == other.param2 and self.param2== other.param1) )

    def __hash__(self):
        return Operator.__hash__(self)


class Not(Operator):
    def __init__(self, param:Formula):
        Operator.__init__(self, "Not")
        self.param = param

    def __repr__(self):
        return f"Not({self.param!r})"

    def __eq__(self, other):
        return isinstance(other, Not) and self.param == other.param

    def __hash__(self):
        return Operator.__hash__(self)

class ForAll(Operator):
    def __init__(self, relation: Relation, concept: Union[DCConstant, Concept, Formula]):
        Operator.__init__(self, "ForAll")
        self.relation = relation
        self.concept = concept

    def __repr__(self):
        return f"ForAll({self.relation!r}, {self.concept!r})"

    def __eq__(self, other):
        return isinstance(other, ForAll) and self.relation == other.relation and self.concept == other.concept

    def __hash__(self):
        return Operator.__hash__(self)

class Exists(Operator):
    def __init__(self, relation: Relation, concept: Union[DCConstant, Concept, Formula]):
        Operator.__init__(self, "Exists")
        self.relation = relation
        self.concept = concept

    def __repr__(self):
        return f"Exists({self.relation!r}, {self.concept!r})"

    def __eq__(self, other):
        return isinstance(other, Exists) and self.relation == other.relation and self.concept == other.concept

    def __hash__(self):
        return Operator.__hash__(self)


class Assertion(object):
    def __init__(self):
        pass

    def __hash__(self):
        return hash(self.__repr__())


class ConceptAssertion(Assertion):
    def __init__(self, concept: Concept, obj: Constant):
        Assertion.__init__(self)
        self.concept = concept
        self.obj = obj

    def __repr__(self):
        return f"CA[{self.concept!r}:({self.obj!r})]"

    def __eq__(self, other):
        return isinstance(other, ConceptAssertion) and self.concept == other.concept and self.obj == other.obj

    def __hash__(self):
        return Assertion.__hash__(self)

class RelationAssertion(Assertion):
    def __init__(self, relation: Relation, obj1: Constant, obj2: Constant):
        Assertion.__init__(self)
        self.relation = relation
        self.obj1 = obj1
        self.obj2 = obj2

    def __repr__(self):
        return f"RA[{self.relation!r}:({self.obj1!r},{self.obj2!r})]"

    def __eq__(self, other):
        return isinstance(other, RelationAssertion) and self.relation == other.relation and self.obj1 == other.obj1 and self.obj2 == other.obj2

    def __hash__(self):
        return Assertion.__hash__(self)

# TODO: make this a set?
ABox = Set[Assertion]
TBox = List[Concept]


class ComplexAssertion(Assertion):
    def __init__(self, formula: Formula, obj: Constant):
        super().__init__()
        self.formula = formula
        self.obj = obj

    def __repr__(self):
        return f"XA[{self.formula!r}({self.obj!r})]"

    def __eq__(self, other):
        return isinstance(other, ComplexAssertion) and self.formula == other.formula and self.obj == other.obj

    def __hash__(self):
        return Assertion.__hash__(self)

