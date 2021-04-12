# formula and or not
# forall exists (tbox)
# concept, primitive concept, defined concept
# relation
# assertion, concept assertion, relation assertion
# abox, tbox
# constant, top, bottom

from typing import Union, Set, List


# Description Logic Constant
class DLConstant(object):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"DConstant({self.name!r})"

    def __eq__(self, other):
        return isinstance(other, DLConstant) and self.name == other.name

    def __hash__(self):
        return hash(self.__repr__())


class DLTop(DLConstant):
    def __init__(self):
        DLConstant.__init__(self, "Top")

    def __repr__(self):
        return "⊤"


class DLBottom(DLConstant):
    def __init__(self):
        DLConstant.__init__(self, "Bottom")

    def __repr__(self):
        return "⊥"


# Top = DLTop()
# Bottom = DLBottom()



class Constant(object):
    """
    Individual
    """

    def __init__(self, name: str):
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

    def __call__(self, obj: Constant, *args, **kwargs):
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

    def __call__(self, obj1: Constant, obj2: Constant, *args, **kwargs):
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
    def __init__(self, param1: Formula, param2: Formula):
        Operator.__init__(self, "And")
        self.param1 = param1
        self.param2 = param2

    def __repr__(self):
        return f"And({self.param1!r}, {self.param2!r})"

    def __eq__(self, other):
        return isinstance(other, And) and ((self.param1 == other.param1 and self.param2 == other.param2) or (
                self.param1 == other.param2 and self.param2 == other.param1))

    def __hash__(self):
        return Operator.__hash__(self)


class Or(Operator):
    def __init__(self, param1: Formula, param2: Formula):
        Operator.__init__(self, "Or")
        self.param1 = param1
        self.param2 = param2

    def __repr__(self):
        return f"Or({self.param1!r}, {self.param2!r})"

    def __eq__(self, other):
        return isinstance(other, Or) and ((self.param1 == other.param1 and self.param2 == other.param2) or (
                self.param1 == other.param2 and self.param2 == other.param1))

    def __hash__(self):
        return Operator.__hash__(self)


class Not(Operator):
    def __init__(self, param: Formula):
        Operator.__init__(self, "Not")
        self.param = param

    def __repr__(self):
        return f"Not({self.param!r})"

    def __eq__(self, other):
        return isinstance(other, Not) and self.param == other.param

    def __hash__(self):
        return Operator.__hash__(self)


class ForAll(Operator):
    def __init__(self, relation: Relation, concept: Union[DLConstant, Concept, Formula]):
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
    def __init__(self, relation: Relation, concept: Union[DLConstant, Concept, Formula]):
        Operator.__init__(self, "Exists")
        self.relation = relation
        self.concept = concept

    def __repr__(self):
        return f"Exists({self.relation!r}, {self.concept!r})"

    def __eq__(self, other):
        return isinstance(other, Exists) and self.relation == other.relation and self.concept == other.concept

    def __hash__(self):
        return Operator.__hash__(self)


class AtLeast(Operator):
    def __init__(self, n: int, relation: Relation, concept: Union[DLConstant, Concept, Formula]):
        Operator.__init__(self, "AtLeast")
        if n < 0:
            raise ValueError("invalid n")

        self.n = n
        self.relation = relation
        self.concept = concept

    def __repr__(self):
        return f"AtLeast[{self.n!r}]({self.relation!r}, {self.concept!r})"

    def __eq__(self, other):
        return isinstance(other,
                          AtLeast) and self.n == other.n and self.relation == other.relation and self.concept == other.concept

    def __hash__(self):
        return hash(self.__repr__())

class AtMost(Operator):
    def __init__(self, n: int, relation: Relation, concept: Union[DLConstant, Concept, Formula]):
        Operator.__init__(self, "AtMost")
        if n < 0:
            raise ValueError("invalid n")

        self.n = n
        self.relation = relation
        self.concept = concept

    def __repr__(self):
        return f"AtMost[{self.n!r}]({self.relation!r}, {self.concept!r})"

    def __eq__(self, other):
        return isinstance(other,
                          AtMost) and self.n == other.n and self.relation == other.relation and self.concept == other.concept

    def __hash__(self):
        return hash(self.__repr__())


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
        return isinstance(other,
                          RelationAssertion) and self.relation == other.relation and self.obj1 == other.obj1 and self.obj2 == other.obj2

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


class InequalityAssertion(Assertion):
    def __init__(self, obj1: Constant, obj2: Constant):
        super().__init__()
        self.obj1 = obj1
        self.obj2 = obj2

    def __repr__(self):
        return f"NEQ[{self.obj1!r}, {self.obj2!r}]"

    def __eq__(self, other):
        return isinstance(other, InequalityAssertion) and ((self.obj1 == other.obj1 and self.obj2 == other.obj2)
                                                           or (self.obj1 == other.obj2 and self.obj2 == other.obj1))

    # TODO: x1=x2, x2=x1? AND/OR also has a similar problem?
    __hash__ = Assertion.__hash__


def ne(obj1: Constant, obj2: Constant) -> InequalityAssertion:
    """
    Simple method to build inequality assertion
    :param obj1:
    :param obj2:
    :return:
    """
    if not isinstance(obj1, Constant) or not isinstance(obj2, Constant):
        raise ValueError("Param not constant")
    return InequalityAssertion(obj1, obj2)


InternalA = PrimitiveConcept("$InternalA")
Top = DefinedConcept("Top", Or(InternalA, Not(InternalA)))
InternalB = PrimitiveConcept("$InternalB")
Bottom = DefinedConcept("Bottom", And(InternalB, Not(InternalB)))