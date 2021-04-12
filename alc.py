from folObj import *


def expandDefinedConcept(concept: DefinedConcept, tbox: TBox) -> Formula:
    if isinstance(concept, PrimitiveConcept):
        return concept
    elif isinstance(concept, DefinedConcept):
        defn = concept.definition
    else:
        defn = concept

    if isinstance(defn, And):
        return And(expandDefinedConcept(defn.formula1, tbox), expandDefinedConcept(defn.formula2, tbox))
    elif isinstance(defn, Or):
        return Or(expandDefinedConcept(defn.formula1, tbox), expandDefinedConcept(defn.formula2, tbox))
    elif isinstance(defn, Not):
        return Not(expandDefinedConcept(defn.formula, tbox))
    elif isinstance(defn, TBoxExists):
        return expandDefinedConcept(defn.concept, tbox)
    elif isinstance(defn, TBoxForAll):
        return expandDefinedConcept(defn.concept, tbox)
    elif isinstance(defn, DefinedConcept):
        return expandDefinedConcept(defn, tbox)

    print(type(concept))
    raise RuntimeError("should not be here...")

def pushInNot(formula: Formula) -> Formula:
    if isinstance(formula, PrimitiveConcept):
        return formula

    if isinstance(formula, Not):
        if isinstance(formula.formula, And):
            return pushInNot(Or(Not(formula.formula.formula1), Not(formula.formula.formula2)))
        elif isinstance(formula.formula, Or):
            return pushInNot(And(Not(formula.formula.formula1), Not(formula.formula.formula2)))
        elif isinstance(formula.formula, Not):
            return formula.formula
        elif isinstance(formula.formula, PrimitiveConcept):
            return Not(pushInNot(formula.formula))
        else:
            print("why here 1?")
            print(formula, type(formula))
            raise RuntimeError()
    elif isinstance(formula, Or) or isinstance(formula, And):
        formula.recursive_apply(pushInNot)
        return formula

    else:
        print("why here 2?")
        print(formula, type(formula))

        raise RuntimeError()

def expandABox(abox: ABox, tbox: TBox):
    new_abox = []
    for assertion in abox:
        if isinstance(assertion, Assertion):
            expanded = expandDefinedConcept(assertion.predicate, tbox)
        elif isinstance(assertion, And) or isinstance(assertion, Or) or isinstance(assertion, Not):
            expanded = expandDefinedConcept(assertion, tbox)
        elif isinstance(assertion, TBoxExists) or isinstance(assertion, TBoxForAll):
            expanded = expandDefinedConcept(assertion, tbox)
        else:
            print(type(assertion))
            raise RuntimeError("Should not happen")



if __name__ == '__main__':

    Smart = PrimitiveConcept("Smart")
    Studious = PrimitiveConcept("Studious")
    GoodStudent = DefinedConcept("GoodStudent", And(Smart, Studious))

    attendBy = Relation("attendBy")

    tbox = [Smart, Studious, GoodStudent]

    a = ConstantSymbol("a")

    abox = [(And(TBoxExists(attendBy, Smart), And(TBoxExists(attendBy, Studious), Not(TBoxExists(attendBy, GoodStudent)))))(a)]

    print(abox)
    print(expandDefinedConcept(abox[0], tbox))





    # A = PrimitiveConcept("A")
    # B = PrimitiveConcept("B")
    # C = PrimitiveConcept("C")
    # r = Relation("R")
    # s = Relation("S")
    #
    #
    # Male = PrimitiveConcept("Male")
    # Female = PrimitiveConcept("Female")
    # Person = PrimitiveConcept("Person")
    # Board = PrimitiveConcept("Board")
    # Sleepy = PrimitiveConcept("Sleepy")
    #
    # hasChild = Relation("hasChild")
    # topic = Relation("topic")
    # teaches = Relation("teaches")
    # attends = Relation("attends")
    # attendedBy = Relation("attendedBy")
    #
    # Women = DefinedConcept("Women", And(Person, Female))
    # Men = DefinedConcept("Men", And(Person, Not(Female)))
    # Course = DefinedConcept("Course", TBoxExists(topic, Top))
    # Lecturer = DefinedConcept("Lecturer", And(Person, TBoxExists(teaches, Course)))
    # Student = DefinedConcept("Student", And(Person, TBoxExists(attends, Course)))
    # BadLecturer = DefinedConcept("BadLecturer", TBoxForAll(teaches, TBoxForAll(attendedBy, Or(Board, Sleepy))))
    #
    # tBox = [Male, Female, Person, Board, Sleepy, Women, Men, Course, Lecturer, Student, BadLecturer]
    #
    # teacher1 = ConstantSymbol("teacher1")
    # student1 = ConstantSymbol("student1")
    # topic1 = ConstantSymbol("topic1")
    #
    #
    #
    #
    # Men2 = DefinedConcept("Men2", And(Person, Not(Women)))
    # Men3 = DefinedConcept("Men3", Men2)
    #
    # aBox = [Male(teacher1), Men2(teacher1), teaches(teacher1, topic1)]
    #
    # # print(expandDefinedConcept(Men3, tBox))
    #
    # m2 = Men3(teacher1)
    # print(m2)
    # print(m2.concept)
    # print(pushInNot(expandDefinedConcept(m2.concept, tBox)))
    #
    # print(Course)

    # print(aBox)
    #
    #
    #
    #
    # print(Women)
    # print(Men)
    # print(expandDefinedConcept(Men2, tBox))
    # print(pushInNot(expandDefinedConcept(Men2, tBox)))

    # print(BadLecturer)
    #
    # hi = BadLecturer(teacher1)
    # print(hi)
    #
    # hi = teaches(teacher1, topic1)
    # print(hi)