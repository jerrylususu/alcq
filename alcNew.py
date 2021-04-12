from alcqObj import *
from typing import Optional, Set, Tuple
from copy import copy, deepcopy
from functools import partial


def expand_formula(f: Formula) -> Formula:
    if isinstance(f, PrimitiveConcept) or isinstance(f, DCConstant):
        return f
    elif isinstance(f, DefinedConcept):
        return expand_formula(f.definition)

    # print(type(f), f)


    if isinstance(f, And):
        return And(expand_formula(f.param1), expand_formula(f.param2))
    elif isinstance(f, Or):
        return Or(expand_formula(f.param1), expand_formula(f.param2))
    elif isinstance(f, Not):
        return Not(expand_formula(f.param))
    elif isinstance(f, ForAll):
        if isinstance(f.concept, PrimitiveConcept) or isinstance(f.concept, DCConstant) or isinstance(f.concept, Relation):
            return ForAll(f.relation, f.concept)
        elif isinstance(f.concept, DefinedConcept):
            dc: DefinedConcept = f.concept
            return ForAll(f.relation, expand_formula(dc.definition))
        else:
            return ForAll(f.concept, expand_formula(f.concept))
    elif isinstance(f, Exists):
        if isinstance(f.concept, PrimitiveConcept) or isinstance(f.concept, DCConstant) or isinstance(f.concept, Relation):
            return Exists(f.relation, f.concept)
        elif isinstance(f.concept, DefinedConcept):
            dc: DefinedConcept = f.concept
            return Exists(f.relation, expand_formula(dc.definition))
        else:
            return Exists(f.relation, expand_formula(f.concept))


    print(type(f), f)
    raise RuntimeError("should not be here")


def expand_concept(c: Concept) -> Formula:
    """
    expand all defined concept to primitive ones
    :param c: concept (defined or primitive)
    :param tbox:
    :return: expaned concept (most possibly a defined one)
    """

    if isinstance(c, PrimitiveConcept) or isinstance(c, DCConstant):
        return c

    if isinstance(c, DefinedConcept):
        defn :Formula = c.definition

        # pre_process
        # if isinstance(defn, ForAll) or isinstance(defn, Exists):
        #     if isinstance(defn.concept, DCConstant):

        expanded :Formula = expand_formula(defn)
        return expanded

    print(type(c))
    raise RuntimeError("should not be here")


def push_in_not(f: Formula) -> Formula:
    """
    Push not into the deepest possible level
    :param f:
    :return:
    """

    if isinstance(f, PrimitiveConcept) or isinstance(f, DCConstant):
        return f
    elif isinstance(f, DefinedConcept):
        raise RuntimeError("should not happen")

    if isinstance(f, Not):
        if isinstance(f.param, And):
            return push_in_not(Or(Not(f.param.param1), Not(f.param.param2)))
        elif isinstance(f.param, Or):
            return push_in_not(And(Not(f.param.param1), Not(f.param.param2)))
        elif isinstance(f.param, Not):
            return push_in_not(f.param.param)
        elif isinstance(f.param, ForAll):
            return push_in_not(Exists(f.param.relation, Not(f.param.concept)))
        elif isinstance(f.param, Exists):
            return push_in_not(ForAll(f.param.relation, Not(f.param.concept)))
        elif isinstance(f.param, PrimitiveConcept) or isinstance(f.param, DCConstant):
            return Not(push_in_not(f.param))

    if isinstance(f, And):
        return And(push_in_not(f.param1), push_in_not(f.param2))
    elif isinstance(f, Or):
        return Or(push_in_not(f.param1), push_in_not(f.param2))
    elif isinstance(f, ForAll):
        return ForAll(f.relation, push_in_not(f.concept))
    elif isinstance(f, Exists):
        return Exists(f.relation, push_in_not(f.concept))

    print(type(f))
    print(f)
    raise RuntimeError("should not be there")


def process_abox(abox: ABox) -> ABox:
    """
    ABox to NNF?
    :param abox:
    :return:
    """
    new_abox : ABox = set()
    for a in abox:
        new_a: Optional[Assertion] = None
        if isinstance(a, ConceptAssertion):
            c = a.concept
            processed_c = expand_concept(c)
            new_a = ComplexAssertion(processed_c, a.obj)
        elif isinstance(a, RelationAssertion):
            new_a = a
        elif isinstance(a, ComplexAssertion):
            f = a.formula
            processed_f = push_in_not(expand_formula(f))
            new_a = ComplexAssertion(processed_f, a.obj)

        if new_a is not None:
            new_abox.add(new_a)
        else:
            raise RuntimeError("should not happen")

    return new_abox

# concept, formula
def get_cf_search_type(c: Union[Concept, Formula]):
    if isinstance(c, PrimitiveConcept):
        return ConceptAssertion
    elif isinstance(c, DefinedConcept):
        raise RuntimeError("should not happen")
    elif isinstance(c, Formula):
        return ComplexAssertion

def build_cf_query(c: Union[Concept, Formula], a:Constant):
    if isinstance(c, PrimitiveConcept):
        return ConceptAssertion(c, a)
    elif isinstance(c, DefinedConcept):
        raise RuntimeError("Should not happen")
    elif isinstance(c, Formula):
        return ComplexAssertion(c, a)
    else:
        raise RuntimeError("Should not happen")


def and_both_exist(abox: ABox, c: Union[Concept, Formula], d: Union[Concept, Formula], a: Constant) -> bool:
    c_a_exist, d_a_exist = False, False
    c_query, d_query = build_cf_query(c, a), build_cf_query(d, a)

    for assertion in abox:
        if assertion == c_query:
            c_a_exist = True
        if assertion == d_query:
            d_a_exist = True

    return c_a_exist and d_a_exist



# check and apply?
def and_rule(abox: ABox) -> Tuple[bool, List[ABox]]:
    # deep copy?
    found_use_case = False
    found_idx = -1
    found_assertion: Optional[ComplexAssertion] = None
    found_formula: Optional[And] = None

    for idx,a in enumerate(abox):
        if isinstance(a, ComplexAssertion):
            f :Formula = a.formula
            if isinstance(f, And):
                # found And(C,D) (a)
                # need to check if C(a) and D(a) are already here
                # Abox should be a set...
                if not and_both_exist(abox, f.param1, f.param2, a.obj):
                    found_use_case = True
                    found_idx = idx
                    found_assertion = a
                    found_formula = f
                    break

    if found_use_case:
        # and don't change number
        new_abox = set(abox)
        # new_abox.remove(found_assertion)
        new_abox.add(ComplexAssertion(found_formula.param1,found_assertion.obj))
        new_abox.add(ComplexAssertion(found_formula.param2,found_assertion.obj))
        return True, [new_abox]
    else:
        return False, []


def exist_already_exist(abox: ABox, r: Relation, c: Concept, a: Constant) -> bool:
    # check if r(a,c), C(c) exists in current abox

    # first get all r(a,c), get all candidate c
    possible_2nd_set = set()
    for assertion in abox:
        if isinstance(assertion, RelationAssertion):
            if assertion.relation == r and assertion.obj1 == a:
                possible_2nd_set.add(assertion.obj2)

    # then check C(c)
    possible_query = {build_cf_query(c,p) for p in possible_2nd_set}
    for assertion in abox:
        if assertion in possible_query:
            return True

    return False


class ConstantStorage(object):

    def __init__(self):
        self.counter = 0

    def generate(self) -> Constant:
        self.counter += 1
        return Constant(f"${self.counter}")

    def __repr__(self):
        return f"ConstantStorage(counter={self.counter})"


def exist_rule(abox: ABox, cs: ConstantStorage) -> Tuple[bool, List[ABox]]:
    found_use_case = False
    found_idx = -1
    found_assertion: Optional[ComplexAssertion] = None
    found_exists: Optional[Exists] = None

    for idx, a in enumerate(abox):
        if isinstance(a, ComplexAssertion) and isinstance(a.formula, Exists):
            r: Relation = a.formula.relation
            c: Concept = a.formula.concept
            # now we have Exist r.C (a)
            # we need to check r(a,c), C(c)
            # check rest:
            if not exist_already_exist(abox, r, c, a.obj):

                found_use_case = True
                found_idx = idx
                found_assertion = a
                found_exists = a.formula
                break
        else:
            # ??
            pass

    if found_use_case:
        # and don't change number
        new_abox = set(abox)
        # new_abox.remove(found_assertion)
        new_constant: Constant = cs.generate()
        new_abox.add(RelationAssertion(found_exists.relation, found_assertion.obj, new_constant))
        if isinstance(found_exists.concept, PrimitiveConcept):
            new_abox.add(ConceptAssertion(found_exists.concept, new_constant))
        elif isinstance(found_exists.concept, Formula):
            new_abox.add(ComplexAssertion(found_exists.concept, new_constant))
        else:
            raise RuntimeError("should not happen")
        return True, [new_abox]
    else:
        return False, []


def union_neither_exists(abox: ABox, C: Union[Concept, Formula], D: Union[Concept, Formula], a: Constant) -> bool:
    c_a_exist, d_a_exist = False, False
    c_query, d_query = build_cf_query(C, a), build_cf_query(D, a)

    for assertion in abox:
        if assertion == c_query:
            c_a_exist = True
        if assertion == d_query:
            d_a_exist = True

    return not c_a_exist and not d_a_exist


def union_rule(abox: ABox) -> Tuple[bool,List[ABox]]:
    found_use_case = False
    found_idx = -1
    found_assertion: Optional[ComplexAssertion] = None
    found_or: Optional[Or] = None

    for idx, a in enumerate(abox):
        if isinstance(a, ComplexAssertion) and isinstance(a.formula, Or):
            C: Formula = a.formula.param1
            D: Formula = a.formula.param2
            # now we have Or(C,D) (a)
            # we need to check either C(a) or D(a)
            # check rest:
            if union_neither_exists(abox, C, D, a.obj):
                found_use_case = True
                found_idx = idx
                found_assertion = a
                found_or = a.formula
                break
        else:
            # ??
            pass

    if found_use_case:
        # and don't change number
        new_abox = set(abox)
        # new_abox.remove(found_assertion)

        abox_c = set(new_abox)
        abox_c.add(ComplexAssertion(found_or.param1, found_assertion.obj))

        abox_d = set(new_abox)
        abox_d.add(ComplexAssertion(found_or.param2, found_assertion.obj))

        return True, [abox_c, abox_d]
    else:
        return False, []


def forall_apply_list(abox: ABox, r: Relation, C: Union[Concept, Formula], a: Constant) -> Tuple[bool, Set[Constant]]:
    # first find all possible b
    possible_2nd_set = set()
    for assertion in abox:
        if isinstance(assertion, RelationAssertion) and assertion.obj1 == a:
            possible_2nd_set.add(assertion.obj2)

    print("debug2", possible_2nd_set)
    # not C(b)
    should_be_added_set = set()
    for b in possible_2nd_set:
        b_query = build_cf_query(C, b)
        found_b = False
        for assertion in abox:
            if assertion == b_query:
                found_b =True
                break

        if not found_b:
            should_be_added_set.add(b)

    print("debug3", should_be_added_set)

    return len(should_be_added_set) != 0, should_be_added_set


def forall_rule(abox: ABox) -> Tuple[bool, List[ABox]]:
    found_use_case = False
    found_idx = -1
    found_assertion: Optional[ComplexAssertion] = None
    found_forall: Optional[ForAll] = None
    found_apply_list: Optional[Set[Constant]] = None

    for idx, a in enumerate(abox):
        if isinstance(a, ComplexAssertion) and isinstance(a.formula, ForAll):
            print("debug", a)
            r: Relation = a.formula.relation
            c: Concept = a.formula.concept
            # now we have Or(C,D) (a)
            # we need to check either C(a) or D(a)
            # check rest:
            need_apply, apply_list = forall_apply_list(abox,r,c,a.obj)
            if need_apply:
                found_use_case = True
                found_idx = idx
                found_assertion = a
                found_forall = a.formula
                found_apply_list = apply_list
                break
        else:
            # ??
            pass

    if found_use_case:
        # and don't change number
        new_abox = set(abox)
        # new_abox.remove(found_assertion)

        for b in found_apply_list:
            if isinstance(found_forall.concept, PrimitiveConcept):
                new_abox.add(ConceptAssertion(found_forall.concept, b))
            elif isinstance(found_forall.concept, DefinedConcept):
                raise RuntimeError("should not happen")
            elif isinstance(found_forall.concept, Formula):
                new_abox.add(ComplexAssertion(found_forall.concept, b))
            else:
                raise RuntimeError("should not happen")

        return True, [new_abox]
    else:
        return False, []


def is_abox_open(abox: ABox) -> bool:
    not_set: Set[Assertion] = set()
    for assertion in abox:
        if isinstance(assertion, ConceptAssertion) and isinstance(assertion.concept, PrimitiveConcept):
            not_set.add(ComplexAssertion(Not(assertion.concept), assertion.obj))
        elif isinstance(assertion, RelationAssertion):
            # TODO: should we consider this?
            pass
        elif isinstance(assertion, ComplexAssertion):
            not_set.add(ComplexAssertion(push_in_not(Not(assertion.formula)), assertion.obj))
        else:
            raise RuntimeError("should not happen")

    for assertion in abox:
        if assertion in not_set:
            return False

    return True


def run_tableau_algo(abox: ABox):
    # hash?
    # duplicate abox?
    worlds : List[ABox] = [abox]

    found_one_apply = False

    cs = ConstantStorage()

    while True:

        current_idx = -1
        replace_new_list = None

        rules = [and_rule, union_rule, forall_rule, partial(exist_rule, cs=cs)]

        # rules = [and_rule, forall_rule ,partial(exist_rule, cs=cs)]


        for rule in rules:
            for idx, w in enumerate(worlds):
                found, new_list = rule(w)
                if found:
                    print("apply on world ", idx )
                    print("found!", idx, w)
                    print("rule!", rule)
                    found_one_apply = True
                    current_idx = idx
                    replace_new_list = new_list
                    break

            if current_idx != -1:
                break

        if current_idx != -1 and replace_new_list is not None:
            worlds.pop(current_idx)
            worlds += replace_new_list

        # print world
        print("------------------")
        print("Current Worlds: ", len(worlds))
        for idx, w in enumerate(worlds):
            print(idx, "len", len(w) ,w)
            for idx2, l in enumerate(w):
                print("world", idx, "line", idx2, l)
        print("------------------")

        # jump out if no more rules can be applied
        if not found_one_apply:
            break

        # reset
        found_one_apply = False

    # while: no more rules can be applied
    # rule has priority
    #

    # remove with index?

    # check if has an open world
    print("Worlds: ", len(worlds))
    world_open_list: List[bool] = []
    for idx, w in enumerate(worlds):
        print(idx, w)
        for idx2, l in enumerate(w):
            print("world", idx, "line", idx2, l)

        world_open_bool: bool = is_abox_open(w)
        print(idx, "open?", world_open_bool)
        world_open_list.append(world_open_bool)

    print("final verdict: ", any(world_open_list))




if __name__ == '__main__':
    Smart = PrimitiveConcept("Smart")
    Studious = PrimitiveConcept("Studious")
    GoodStudent = DefinedConcept("GoodStudent", And(Smart, Studious))
    attendBy = Relation("attendBy")

    StraightA = PrimitiveConcept("StraightA")
    MultiOffer = PrimitiveConcept("MultiOffer")
    NBStudnet = DefinedConcept("NBStudent", Or(StraightA, MultiOffer))
    NiuWa = DefinedConcept("NiuWa", And(NBStudnet, GoodStudent))
    print(NiuWa)
    print(expand_concept(NiuWa))

    # tbox = [Smart, Studious, GoodStudent, StraightA, MultiOffer, NBStudnet, NiuWa]


    a = Constant("a")
    s1 = Constant("Student 1")
    c1 = Constant("Course 1")
    print(GoodStudent(a))
    print(attendBy(c1, s1))


    topic = Relation("topic")

    # anything that has a topic is a course
    Course = DefinedConcept("Course", Exists(topic, Top))
    Good = PrimitiveConcept("Good")
    GoodCourse = DefinedConcept("GoodCourse", And(Good, Course))

    print(expand_concept(GoodStudent))
    print(expand_concept(GoodCourse))

    w = And(Exists(attendBy, Smart), And(Exists(attendBy, Studious), Not(Exists(attendBy, GoodStudent))))(a)
    print(w)
    print(type(w.formula))
    print(expand_formula(w.formula))
    print(push_in_not(expand_formula(w.formula)))

    # abox = [w, GoodStudent(a), attendBy(c1,s1)]

    print(type(w))

    abox = {w}

    print(abox)
    print(process_abox(abox))

    processed_abox = process_abox(abox)
    run_tableau_algo(processed_abox)


    A = PrimitiveConcept("A")
    B = PrimitiveConcept("B")
    C = PrimitiveConcept("C")
    r = Relation("r")
    s = Relation("s")

    p1 = ForAll(r, ForAll(s, A))
    p2 = Exists(r, ForAll(s, B))
    p3 = ForAll(r, Exists(s, C))
    p4 = Exists(r, Exists(s, And(A,And(B,C))))

    w2 = And(p1, And(p2, And(p3, Not(p4))))

    print(w2)
    abox = {w2(a)}
    pb = process_abox(abox)

    # run_tableau_algo(pb)

    # TOD0: test top/bottom


    p1 = ForAll(r, ForAll(s, A))
    p2 = Or(Exists(r, ForAll(s, Not(A))), ForAll(r, Exists(s, B)))
    p3 = Or(ForAll(r, Exists(s, And(A,B))), Exists(r, ForAll(s, Not(B))))

    w3 = And(p1, And(p2, Not(p3)))

    print(w3)
    abox = {w3(a)}
    # pb = process_abox(abox)
    # run_tableau_algo(pb)

