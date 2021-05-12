from alcqObj import *
from typing import Optional, Set, Tuple
from copy import copy, deepcopy
from functools import partial
import string
from itertools import combinations

def expand_formula(f: Formula) -> Formula:

    if isinstance(f, PrimitiveConcept):
        return f
    elif isinstance(f, DefinedConcept):
        return expand_formula(f.definition)

    if isinstance(f, And):
        return And(expand_formula(f.param1), expand_formula(f.param2))
    elif isinstance(f, Or):
        return Or(expand_formula(f.param1), expand_formula(f.param2))
    elif isinstance(f, Not):
        return Not(expand_formula(f.param))
    elif isinstance(f, ForAll):
        if isinstance(f.concept, PrimitiveConcept)  or isinstance(f.concept,
                                                                                                      Relation):
            return ForAll(f.relation, f.concept)
        elif isinstance(f.concept, DefinedConcept):
            dc: DefinedConcept = f.concept
            return ForAll(f.relation, expand_formula(dc.definition))
        else:
            return ForAll(f.relation, expand_formula(f.concept))
    elif isinstance(f, Exists):

        if isinstance(f.concept, PrimitiveConcept) or isinstance(f.concept,
                                                                                                      Relation):
            return Exists(f.relation, f.concept)
        elif isinstance(f.concept, DefinedConcept):
            dc: DefinedConcept = f.concept
            return Exists(f.relation, expand_formula(dc.definition))
        else:
            return Exists(f.relation, expand_formula(f.concept))
    elif isinstance(f, AtMost):
        if isinstance(f.concept, PrimitiveConcept)  or isinstance(f.concept, Relation):
            return AtMost(f.n, f.relation, f.concept)
        elif isinstance(f.concept, DefinedConcept):
            dc: DefinedConcept = f.concept
            return AtMost(f.n, f.relation, expand_formula(dc.definition))
        else:
            return AtMost(f.n, f.relation, expand_formula(f.concept))
        pass
    elif isinstance(f, AtLeast):
        if isinstance(f.concept, PrimitiveConcept) or isinstance(f.concept,
                                                                                                      Relation):
            return AtLeast(f.n, f.relation, f.concept)
        elif isinstance(f.concept, DefinedConcept):
            dc: DefinedConcept = f.concept
            return AtLeast(f.n, f.relation, expand_formula(dc.definition))
        else:
            return AtLeast(f.n, f.relation, expand_formula(f.concept))


    print(type(f), f)
    raise RuntimeError("should not be here")


def expand_concept(c: Concept) -> Formula:
    """
    expand all defined concept to primitive ones
    :param c: concept (defined or primitive)
    :param tbox:
    :return: expaned concept (most possibly a defined one)
    """

    if isinstance(c, PrimitiveConcept):
        return c

    if isinstance(c, DefinedConcept):
        defn: Formula = c.definition

        # pre_process
        # if isinstance(defn, ForAll) or isinstance(defn, Exists):
        #     if isinstance(defn.concept, DCConstant):

        expanded: Formula = expand_formula(defn)
        return expanded

    print(type(c))
    raise RuntimeError("should not be here")


def push_in_not(f: Formula) -> Formula:
    """
    Push not into the deepest possible level

    :param f:
    :return:
    """

    if isinstance(f, PrimitiveConcept):
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
        elif isinstance(f.param, AtMost):
            return AtLeast(f.param.n + 1, f.param.relation, f.param.concept)
        elif isinstance(f.param, AtLeast):
            if f.param.n == 0:
                return Bottom
            else:
                return AtMost(f.param.n - 1, f.param.relation, f.param.concept)
        elif isinstance(f.param, PrimitiveConcept):
            return Not(push_in_not(f.param))

    if isinstance(f, And):
        return And(push_in_not(f.param1), push_in_not(f.param2))
    elif isinstance(f, Or):
        return Or(push_in_not(f.param1), push_in_not(f.param2))
    elif isinstance(f, ForAll):
        return ForAll(f.relation, push_in_not(f.concept))
    elif isinstance(f, Exists):
        return Exists(f.relation, push_in_not(f.concept))
    elif isinstance(f, AtMost):
        return AtMost(f.n, f.relation, push_in_not(f.concept))
    elif isinstance(f, AtLeast):
        return AtLeast(f.n, f.relation, push_in_not(f.concept))

    print(type(f))
    print(f)
    raise RuntimeError("should not be there")


def process_abox(abox: ABox) -> ABox:
    """
    ABox to NNF?
    :param abox:
    :return:
    """
    new_abox: ABox = set()
    for a in abox:
        new_a: Optional[Assertion] = None
        if isinstance(a, ConceptAssertion):
            c = a.concept
            processed_c = push_in_not(expand_concept(c))
            if isinstance(processed_c, PrimitiveConcept):
                new_a = ConceptAssertion(processed_c, a.obj)
            else:
                new_a = ComplexAssertion(processed_c, a.obj)
        elif isinstance(a, RelationAssertion):
            new_a = a
        elif isinstance(a, ComplexAssertion):
            f = a.formula
            processed_f = push_in_not(expand_formula(f))
            new_a = ComplexAssertion(processed_f, a.obj)
        elif isinstance(a, InequalityAssertion):
            new_a = a

        if new_a is not None:
            new_abox.add(new_a)
        else:
            print(type(a), a)
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


def build_cf_query(c: Union[Concept, Formula], a: Constant):
    if isinstance(c, PrimitiveConcept):
        return ConceptAssertion(c, a)
    elif isinstance(c, DefinedConcept):
        raise RuntimeError("Should not happen")
    elif isinstance(c, Formula):
        return ComplexAssertion(c, a)
    else:
        print("eror: ", c)
        raise RuntimeError("Should not happen")


def and_both_exist(abox: ABox, c: Union[Concept, Formula], d: Union[Concept, Formula], a: Constant) -> bool:

    # note: here c&d has been splited, need to check in and_rule, before this invocation
    # if is_this_concept_top(c):
    #     return True

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

    for idx, a in enumerate(abox):
        if isinstance(a, ComplexAssertion):
            f: Formula = a.formula
            if isinstance(f, And):

                if is_this_bottom_something(f):
                    # no need to apply and on top
                    continue

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
        print("and found", found_assertion)
        # and don't change number
        new_abox = set(abox)

        # DONE: check all alike...
        for param in [found_formula.param1, found_formula.param2]:
            if isinstance(param, PrimitiveConcept):
                new_abox.add(ConceptAssertion(param, found_assertion.obj))
            elif isinstance(param, DefinedConcept):
                raise RuntimeError("should not happen")
            elif isinstance(param, Formula):
                new_abox.add(ComplexAssertion(param, found_assertion.obj))
            else:
                raise RuntimeError("should not happen")
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
    # remark: no need to handle top here, all constant are added top in preprocessing

    possible_query = {build_cf_query(c, p) for p in possible_2nd_set}
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
        print("exist found", found_assertion)

        # and don't change number
        new_abox = set(abox)

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
    # if is_this_top_something(C):
    #     return not True and not True

    c_a_exist, d_a_exist = False, False
    c_query, d_query = build_cf_query(C, a), build_cf_query(D, a)

    for assertion in abox:
        if assertion == c_query:
            c_a_exist = True
        if assertion == d_query:
            d_a_exist = True

    return not c_a_exist and not d_a_exist


def union_rule(abox: ABox) -> Tuple[bool, List[ABox]]:
    found_use_case = False
    found_idx = -1
    found_assertion: Optional[ComplexAssertion] = None
    found_or: Optional[Or] = None

    for idx, a in enumerate(abox):
        if isinstance(a, ComplexAssertion) and isinstance(a.formula, Or):

            # don't decompose top
            if is_this_top_something(a.formula):
                continue

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
        print("union found", found_assertion)

        # and don't change number
        new_abox = set(abox)

        abox_c = set(new_abox)
        if isinstance(found_or.param1, PrimitiveConcept):
            abox_c.add(ConceptAssertion(found_or.param1, found_assertion.obj))
        else:
            abox_c.add(ComplexAssertion(found_or.param1, found_assertion.obj))

        abox_d = set(new_abox)
        if isinstance(found_or.param2, PrimitiveConcept):
            abox_d.add(ConceptAssertion(found_or.param2, found_assertion.obj))
        else:
            abox_d.add(ComplexAssertion(found_or.param2, found_assertion.obj))

        return True, [abox_c, abox_d]
    else:
        return False, []


def forall_apply_list(abox: ABox, r: Relation, C: Union[Concept, Formula], a: Constant) -> Tuple[bool, Set[Constant]]:

    # if Top, can let it add, will be handled by post processing

    # first find all possible b
    possible_2nd_set = set()
    for assertion in abox:
        if isinstance(assertion, RelationAssertion) and assertion.relation == r and assertion.obj1 == a:
            possible_2nd_set.add(assertion.obj2)

    # not C(b)
    should_be_added_set = set()
    for b in possible_2nd_set:
        b_query = build_cf_query(C, b)
        found_b = False
        for assertion in abox:
            if assertion == b_query:
                found_b = True
                break

        if not found_b:
            should_be_added_set.add(b)

    return len(should_be_added_set) != 0, should_be_added_set


def forall_rule(abox: ABox) -> Tuple[bool, List[ABox]]:
    found_use_case = False
    found_idx = -1
    found_assertion: Optional[ComplexAssertion] = None
    found_forall: Optional[ForAll] = None
    found_apply_list: Optional[Set[Constant]] = None

    for idx, a in enumerate(abox):
        if isinstance(a, ComplexAssertion) and isinstance(a.formula, ForAll):

            r: Relation = a.formula.relation
            c: Concept = a.formula.concept
            # now we have Or(C,D) (a)
            # we need to check either C(a) or D(a)
            # check rest:
            need_apply, apply_list = forall_apply_list(abox, r, c, a.obj)
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
        print("forall found", found_assertion)


        # and don't change number
        new_abox = set(abox)

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


class ConstantBuilder:
    def __init__(self):
        self.counter = 0
        # DONE: prefix > 26
        self.prefix = 0

    # Excel column style A...Z,AA,AB...
    # https://stackoverflow.com/a/48984697
    def _divmod_excel(self, n):
        a, b = divmod(n, 26)
        if b == 0:
            return a - 1, b + 26
        return a, b

    def _to_excel(self, num):
        chars = []
        while num > 0:
            num, d = self._divmod_excel(num)
            chars.append(string.ascii_uppercase[d - 1])
        return ''.join(reversed(chars))

    def generate(self) -> Constant:
        self.counter += 1
        return Constant(f"${self._to_excel(self.prefix)}-{self.counter}")

    def new_prefix(self):
        self.prefix += 1

    def __repr__(self):
        return f"ConstantBuilder(prefix={self.prefix}, counter={self.counter})"



def at_least_should_apply(abox: ABox, n: int, r: Relation, c: Union[Concept, Formula], a: Constant) -> bool:
    can_apply = True

    # find all possible c_is
    all_c_li = []
    for assertion in abox:
        if isinstance(assertion, RelationAssertion) and assertion.relation == r and assertion.obj1 == a:
            all_c_li.append(assertion.obj2)

    # do a filter by C
    new_all_c_li = []
    for current_ci in all_c_li:
        # if success then add
        # special case
        if is_this_top_something(c):
            pass
            # DONE: always success
            new_all_c_li.append(current_ci)
        else:
            query = build_cf_query(c, current_ci)
            if query in abox:
                new_all_c_li.append(current_ci)

    all_c_li = new_all_c_li

    all_c_li = list(set(all_c_li))

    # early check
    if len(all_c_li) < n:
        return True

    # check with basic permutation?
    for comb in combinations(all_c_li, n):
        # now we have an tuple of size N
        current_comb_ok = True

        # goal: check if in "any" combination, "all" the inequality pair exists in abox
        # if such combination (a qualified one, all pair exists) is found, then no need to apply
        # otherwise need to apply


        for bi,bj in combinations(comb, 2):
            if ne(bi, bj) not in abox and ne(bj, bi) not in abox:
                # one inequality pair not exist
                # current combination is not qualified
                current_comb_ok = False
                break

        if current_comb_ok:
            # found one such (qualified) combination, no need to apply
            return False
        else:
            # this combination failed, just keep finding
            pass

    # all combination failed, need to apply
    # no more combination, just return false
    return True

def at_least_rule(abox: ABox, cb: ConstantBuilder) -> Tuple[bool, List[ABox]]:
    found_use_case = False
    found_idx = -1
    found_assertion: Optional[ComplexAssertion] = None
    found_at_least: Optional[AtLeast] = None


    for idx, a in enumerate(abox):
        if isinstance(a, ComplexAssertion) and isinstance(a.formula, AtLeast):
            n: int = a.formula.n
            r: Relation = a.formula.relation
            c: Concept = a.formula.concept
            if at_least_should_apply(abox, n, r,c,a.obj):
                found_use_case = True
                found_idx = idx
                found_assertion = a
                found_at_least = a.formula
                break
        else:
            # ??
            pass

    if found_use_case:
        print("at least found", found_assertion)


        # and don't change number
        new_abox = set(abox)

        cb.new_prefix()
        new_constant_li: List[Constant] = []
        for idx in range(found_at_least.n):
            new_constant: Constant = cb.generate()
            new_constant_li.append(new_constant)
            # add relation
            new_abox.add(RelationAssertion(found_at_least.relation, found_assertion.obj, new_constant))
            # add concept
            if isinstance(found_at_least.concept, PrimitiveConcept):
                new_abox.add(ConceptAssertion(found_at_least.concept, new_constant))
            elif isinstance(found_at_least.concept, Formula):
                new_abox.add(ComplexAssertion(found_at_least.concept, new_constant))
            else:
                # Top & Bottom?

                print(type(found_at_least.concept))
                raise RuntimeError("should not happen")

        # add inequality
        for bi, bj in combinations(new_constant_li, 2):
            new_abox.add(InequalityAssertion(bi, bj))

        return True, [new_abox]
    else:
        return False, []


def at_most_should_apply(abox: ABox, n: int, r: Relation, c: Union[Concept, Formula], a: Constant) -> Tuple[bool, List[Constant]]:
    # need to check: has more than expected

    # get initial list by relation
    possible_b_li = []
    for assertion in abox:
        if isinstance(assertion, RelationAssertion) and assertion.relation == r and assertion.obj1 == a:
            possible_b_li.append(assertion.obj2)

    # filter by concept
    new_possible_b_li = []
    for current_b in possible_b_li:

        if is_this_top_something(c):
            new_possible_b_li.append(current_b)
        else:
            b_query = build_cf_query(c, current_b)
            if b_query in abox:
                new_possible_b_li.append(current_b)

    possible_b_li = new_possible_b_li

    possible_b_li = list(set(possible_b_li))

    # early check
    if len(possible_b_li) <= n:
        # less then n, no need to apply
        return False, []

    # check inequality with permutation
    # need to choose n+1

    # check not all exist
    # as long as one equality don't exist, we can use

    for comb in combinations(possible_b_li, n+1):
        for bi, bj in combinations(comb, 2):
            if InequalityAssertion(bi, bj) not in abox and InequalityAssertion(bj,bi) not in abox:
                # we found one eq not in...
                return True, list(comb)

    # can not use by default
    return False, []


def make_substitution(abox: ABox, src: Constant, dst: Constant) -> ABox:
    new_abox = []
    for assertion in abox:
        new_assertion : Optional[Assertion] = None
        if isinstance(assertion, ConceptAssertion):
            new_assertion = assertion
            if assertion.obj == src:
                new_assertion = ConceptAssertion(assertion.concept, dst)
        elif isinstance(assertion, RelationAssertion):
            new_assertion = assertion
            obj1, obj2 = assertion.obj1, assertion.obj2
            found1, found2 = False, False
            if obj1 == src:
                obj1 = dst
                found1 = True
            if obj2 == src:
                obj2 = dst
                found2 = True
            if found1 or found2:
                new_assertion = RelationAssertion(assertion.relation, obj1, obj2)
        elif isinstance(assertion, ComplexAssertion):
            new_assertion = assertion
            if assertion.obj == src:
                new_assertion = ComplexAssertion(assertion.formula, dst)
        elif isinstance(assertion, InequalityAssertion):
            new_assertion = assertion
            obj1, obj2 = assertion.obj1, assertion.obj2
            found1, found2 = False, False
            if obj1 == src:
                obj1 = dst
                found1 = True
            if obj2 == src:
                obj2 = dst
                found2 = True
            if found1 or found2:
                new_assertion = InequalityAssertion(obj1, obj2)
        else:
            raise RuntimeError("should not be here")

        if new_assertion is not None:
            new_abox.append(new_assertion)
        else:
            raise RuntimeError("should not be here")

    return new_abox


def at_most_rule(abox: ABox) -> Tuple[bool, List[ABox]]:
    found_use_case = False
    found_idx = -1
    found_assertion: Optional[ComplexAssertion] = None
    found_at_most: Optional[AtMost] = None
    found_combination: Optional[List[Constant]] = None

    for idx, a in enumerate(abox):
        if isinstance(a, ComplexAssertion) and isinstance(a.formula, AtMost):
            n: int = a.formula.n
            r: Relation = a.formula.relation
            c: Concept = a.formula.concept
            should_apply, possible_comb = at_most_should_apply(abox, n, r, c, a.obj)
            if should_apply:
                found_use_case = True
                found_idx = idx
                found_assertion = a
                found_at_most = a.formula
                found_combination = possible_comb
                break
        else:
            # ??
            pass

    if found_use_case:
        print("at most found", found_assertion)

        # and don't change number

        new_abox_li: List[ABox] = []
        # do some kind of substitution?
        for bi, bj in combinations(found_combination, 2):
            bi: Constant
            bj: Constant
            if ne(bi,bj) not in abox and ne(bj,bi) not in abox:
                # DONE: choose one direction to substitute?
                abox_copy = set(abox)

                # fix 4 child has at most 2 problem
                bi_names = bi.name.split("~")
                bj_names = bj.name.split("~")
                bi_names += bj_names
                all_names = sorted(bi_names)

                new_constant = Constant("~".join(all_names))
                new_abox = make_substitution(abox_copy, bi, new_constant)
                new_abox = make_substitution(new_abox, bj, new_constant)
                new_abox_li.append(new_abox)

        return True, new_abox_li
    else:
        return False, []


def choose_rule_can_apply(abox: ABox, r: Relation, c: Concept, a: Constant) -> Tuple[bool, Optional[Constant]]:
    # don't apply if C is top
    # if is_this_top_something(c):
    #     return False, None


    # check all possible b
    possible_b_list: List[Constant] = []
    for assertion in abox:
        if isinstance(assertion, RelationAssertion) and assertion.relation == r and assertion.obj1 == a:
            possible_b_list.append(assertion.obj2)

    # check all C(b)
    # DONE: add check for not c(b)
    for current_b in possible_b_list:
        b_query = build_cf_query(c, current_b)

        # inside it's all XA
        # if isinstance(b_query, ConceptAssertion):
        #     b_query = ComplexAssertion(b_query.concept, current_b)

        not_b_query: Assertion = None
        if isinstance(b_query, ConceptAssertion) and isinstance(b_query.concept, PrimitiveConcept):
            not_b_query = ComplexAssertion(Not(b_query.concept), current_b)
        elif isinstance(b_query, ComplexAssertion):
            inside = push_in_not(Not(b_query.formula))
            if isinstance(inside, Concept):
                not_b_query = ConceptAssertion(inside, current_b)
            else:
                not_b_query = ComplexAssertion(push_in_not(Not(b_query.formula)), current_b)
            # c itself is a not?: should not happen, should use (Not(concept))(constant)
        else:
            raise RuntimeError("should not be here")

        if not_b_query is None:
            raise RuntimeError("should not happen")

        if b_query not in abox and not_b_query not in abox:
            # neither C(b) nor NOT(C(b)) exists
            print("choose rule: chosen", current_b, "with C:",c)
            return True, current_b

    return False, None


def choose_rule(abox: ABox) -> Tuple[bool, List[ABox]]:
    found_use_case = False
    found_idx = -1
    found_assertion: Optional[ComplexAssertion] = None
    found_at_most: Optional[AtMost] = None
    found_constant : Optional[Constant] = None

    for idx, a in enumerate(abox):
        if isinstance(a, ComplexAssertion) and isinstance(a.formula, AtMost):
            n: int = a.formula.n
            r: Relation = a.formula.relation
            c: Concept = a.formula.concept
            can_apply, b = choose_rule_can_apply(abox, r,c,a.obj)
            if can_apply:
                found_use_case = True
                found_idx = idx
                found_assertion = a
                found_at_most = a.formula
                found_constant = b
                break
        else:
            # ??
            pass

    if found_use_case:
        print("choose found", found_assertion)

        # and don't change number
        new_abox_list = []

        new_assertion: Optional[Assertion] = None

        if isinstance(found_at_most.concept, PrimitiveConcept):
            new_assertion = ConceptAssertion(found_at_most.concept, found_constant)
        elif isinstance(found_at_most.concept, DefinedConcept):
            raise RuntimeError("should not happen")
        elif isinstance(found_at_most.concept, Formula):
            new_assertion = ComplexAssertion(found_at_most.concept, found_constant)
        else:
            print(type(found_at_most.concept))
            raise RuntimeError("should not happen")


        # add positive
        pos_abox = set(abox)
        neg_abox = set(abox)

        neg_assertion : Assertion = None

        # DONE: push into...
        if isinstance(new_assertion, ConceptAssertion) and isinstance(new_assertion.concept, PrimitiveConcept):
            inside = push_in_not(expand_concept(new_assertion.concept))
            if isinstance(inside, PrimitiveConcept):
                neg_assertion = ConceptAssertion(inside, found_constant)
            else:
                neg_assertion = ComplexAssertion(inside, found_constant)
        elif isinstance(new_assertion, ComplexAssertion):
            inside = push_in_not(expand_formula(new_assertion.formula))
            if isinstance(inside, PrimitiveConcept):
                neg_assertion = ConceptAssertion(inside, found_constant)
            else:
                neg_assertion = ComplexAssertion(inside, found_constant)
        else:
            raise RuntimeError("should not be here")

        pos_abox.add(new_assertion)
        neg_abox.add(neg_assertion)



        return True, [pos_abox, neg_abox]
    else:
        return False, []


def exist_same_inequality(abox: ABox) -> bool:
    for assertion in abox:
        if isinstance(assertion, InequalityAssertion) and assertion.obj1 == assertion.obj2:
            return True
    return False


def exist_certain_at_most_violation(abox: ABox, source: Assertion):
    if not isinstance(source, ComplexAssertion) or not isinstance(source.formula, AtMost):
        raise ValueError("parameter not at most assertion")

    # just check one given abox
    n = source.formula.n

    # first get all b_i by relations
    all_b_list = []
    for assertion in abox:
        if isinstance(assertion, RelationAssertion) and assertion.relation == source.formula.relation and assertion.obj1 == source.obj:
            all_b_list.append(assertion.obj2)


    # then filter by C
    filtered_all_b_list = []
    for b in all_b_list:

        if is_this_top_something(source.formula.concept):
            filtered_all_b_list.append(b)
            continue


        b_query = build_cf_query(source.formula.concept, b)
        if b_query in abox:
            filtered_all_b_list.append(b)

    all_b_list = filtered_all_b_list


    # quick test
    if len(all_b_list) <= n:
        return False

    # finally check inequality
    # by default no violation, unless one such violation is found
    for comb in combinations(all_b_list, n+1):
        # for each combination
        all_have_inequality = True
        for bi, bj in combinations(comb, 2):
            if ne(bi,bj) not in abox and ne(bj,bi) not in abox:
                all_have_inequality = False
                break

        if all_have_inequality:
            # find one violation
            return True

    # if nothing is found, then safe
    return False

def exist_at_most_violation(abox: ABox) -> bool:
    # get all <= nr.C(a)
    all_at_most_list = []
    for assertion in abox:
        if isinstance(assertion, ComplexAssertion) and isinstance(assertion.formula, AtMost):
            all_at_most_list.append(assertion)

    # check one by one
    for atmost in all_at_most_list:
        if exist_certain_at_most_violation(abox, atmost):
            return True

    # should be safe by default
    return False



def is_abox_open(abox: ABox) -> bool:
    # DONE: add support for TOP/BOTTOM
    if exist_same_inequality(abox):
        print("is_abox_open: exist same inequality")
        return False

    # DONE: another contradiction
    if exist_at_most_violation(abox):
        print("is_abox_open: exist at most violation")
        return False


    not_set: Set[Assertion] = set()
    for assertion in abox:
        if isinstance(assertion, ConceptAssertion) and isinstance(assertion.concept, PrimitiveConcept):
            not_set.add(ComplexAssertion(Not(assertion.concept), assertion.obj))
        elif isinstance(assertion, RelationAssertion):
            # should not do anything
            pass
        elif isinstance(assertion, ComplexAssertion):
            not_set.add(ComplexAssertion(push_in_not(Not(assertion.formula)), assertion.obj))
        elif isinstance(assertion, InequalityAssertion):
            # checked before
            pass
        else:
            raise RuntimeError("should not happen")

    for assertion in abox:
        if assertion in not_set:
            return False

    return True

def is_this_top_something(c: Union[DefinedConcept, ComplexAssertion, Formula, Concept]):
    return c == Top \
        or (c == Top.definition or c == push_in_not(Not(Bottom.definition))) \
        or (isinstance(c, DefinedConcept) and (c.definition == Top.definition or c == push_in_not(Not(Bottom.definition)))) \
        or (isinstance(c, ComplexAssertion) and (c.formula == Top.definition or c == push_in_not(Not(Bottom.definition)))) \
        or (isinstance(c, Formula) and (c == Top.definition or c == push_in_not(Not(Bottom.definition))))


def is_this_bottom_something(c: Union[DefinedConcept, ComplexAssertion, Formula, Concept]):
    return c == Bottom \
           or (c == Bottom.definition or c == push_in_not(Not(Top.definition))) \
           or (isinstance(c, DefinedConcept) and (
                c.definition == Bottom.definition or c == push_in_not(Not(Top.definition)))) \
           or (isinstance(c, ComplexAssertion) and (
                c.formula == Bottom.definition or c == push_in_not(Not(Top.definition)))) \
           or (isinstance(c, Formula) and (c == Bottom.definition or c == push_in_not(Not(Top.definition))))


def is_this_assertion_top(ca: ComplexAssertion) -> bool:
    if not isinstance(ca, ComplexAssertion):
        raise ValueError
    obj: Constant = ca.obj
    return is_this_top_something(ca.formula) or build_cf_query(Top.definition, obj) == ca

def is_this_assertion_bottom(ca: ComplexAssertion) -> bool:
    if not isinstance(ca, ComplexAssertion):
        raise ValueError
    obj: Constant = ca.obj
    return is_this_bottom_something(ca.formula) or build_cf_query(Bottom.definition, obj) == ca


def pre_process_top(abox: ABox):
    # directly edit in place
    new_tops : Set[Assertion] = set()
    for assertion in abox:
        if isinstance(assertion, ConceptAssertion):
            new_tops.add(Top(assertion.obj))
        elif isinstance(assertion, RelationAssertion):
            new_tops.add(Top(assertion.obj1))
            new_tops.add(Top(assertion.obj2))
        elif isinstance(assertion, ComplexAssertion):
            new_tops.add(Top(assertion.obj))
        elif isinstance(assertion, InequalityAssertion):
            new_tops.add(Top(assertion.obj1))
            new_tops.add(Top(assertion.obj2))

    new_tops = process_abox(new_tops)
    # just an add all
    abox.update(new_tops)


def post_process_bottom(abox: ABox) -> Optional[ABox]:
    # this clears abox containing bottom, so they can later be deleted
    # and removes top from existing abox

    new_abox = set()

    for assertion in abox:
        if isinstance(assertion, ComplexAssertion):
            # print("checking:", assertion)
            if is_this_assertion_bottom(assertion):
                print("bottom found", assertion)
                return None
            elif is_this_assertion_top(assertion):
                # in fact need to add all top, don't remove...
                pass
                # print("top found", assertion)
                # don't add
                # continue
            else:
                # print("neither")
                new_abox.add(assertion)
        else:
            new_abox.add(assertion)

    return new_abox

def run_tableau_algo(abox: ABox, verbose=False):
    # hash?
    # duplicate abox?
    worlds: List[ABox] = [abox]

    if verbose:
        print("---initial----")
        print("Current Worlds: ", len(worlds))
        for idx, w in enumerate(worlds):
            print(idx, "len", len(w), "----")
            for idx2, l in enumerate(w):
                print("world", idx, "line", idx2, l)

    found_one_apply = False

    cs = ConstantStorage()
    cb = ConstantBuilder()

    while True:

        # pre process
        for world in worlds:
            pre_process_top(world)

        current_idx = -1
        replace_new_list = None

        rules = [and_rule, union_rule, forall_rule, choose_rule, partial(at_least_rule, cb=cb), at_most_rule, partial(exist_rule, cs=cs),]

        # rules = [and_rule, forall_rule ,partial(exist_rule, cs=cs)]

        for rule in rules:
            for idx, w in enumerate(worlds):
                found, new_list = rule(w)
                if found:
                    print("apply on world ", idx)
                    # print("found! on world", idx)
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


        # process top/bottom
        post_processed_world_list = []
        for world in worlds:
            new_world: Optional[ABox] = post_process_bottom(world)
            if new_world is not None:
                post_processed_world_list.append(new_world)
            else:
                if verbose:
                    print("BOTTOM FOUND: world eliminated!")
                    print("eliminated world: ")
                    for idx, assertion in enumerate(world):
                        print(idx, assertion)

        worlds = post_processed_world_list

        # post process 2: remove same world
        # simulate a set of aboxes

        if verbose:
            print("--dedupe world--")
            print("before dedupe len=", len(worlds))
            frozen_worlds = {frozenset(world) for world in worlds}
            worlds = [set(world) for world in frozen_worlds]
            print("after dedupe len=", len(worlds))

            # print world
            print("-------intermediate-----------")
            print("Current Worlds: ", len(worlds))
            for idx, w in enumerate(worlds):
                print(idx, "len", len(w), "----")
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
    print("-------final-----------")

    print("Worlds: ", len(worlds))
    world_open_list: List[bool] = []
    for idx, w in enumerate(worlds):
        if verbose:
            print(idx, w)
            for idx2, l in enumerate(w):
                print("world", idx, "line", idx2, l)

        world_open_bool: bool = is_abox_open(w)
        print(idx, "open?", world_open_bool)
        world_open_list.append(world_open_bool)

    print("world overview: ", len(world_open_list), world_open_list)
    print("final (consistency, true=open) verdict: ", any(world_open_list))

    return any(world_open_list)


def is_subsumption_of(c1: Concept, c2: Concept) -> bool:
    """
    C ⊑T D
    :param c1: C
    :param c2: D
    :return:
    """
    anded = push_in_not(And(expand_concept(c1),Not(expand_concept(c2))))
    a = Constant("$a")
    abox = {(anded)(a)}

    is_consistent = run_tableau_algo(process_abox(abox))
    return not is_consistent


if __name__ == '__main__':

    Smart = PrimitiveConcept("Smart")
    Studious = PrimitiveConcept("Studious")
    GoodStudent = DefinedConcept("GoodStudent", And(Smart, Studious))
    attendBy = Relation("attendBy")

    topic = Relation("topic")
    Course = DefinedConcept("Course", Exists(topic, Top))
    Good = PrimitiveConcept("Good")
    GoodCourse = DefinedConcept("GoodCourse", And(Good, Course))

    # print(expand_concept(GoodCourse))


    s1 = Constant("Student 1")
    c1 = Constant("Course 1")
    # print(GoodStudent(a))
    # print(attendBy(c1, s1))

    a = Constant("a")
    assertion = And(Exists(attendBy, Smart), And(Exists(attendBy, Studious), Not(Exists(attendBy, GoodStudent))))(a)
    abox = {assertion}
    run_tableau_algo(process_abox(abox))


    c1 = DefinedConcept("c1", And(Exists(attendBy, Smart), Exists(attendBy, Studious)))
    c2 = DefinedConcept("c2", Exists(attendBy, GoodStudent))
    # should be false
    # print("is subsumption?", is_subsumption_of(c1, c2))



