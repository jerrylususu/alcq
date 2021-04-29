from alcqObj import *
from alcq import *


def good_student():
    """
    smart, studious, good student
    adapted from slides "05-description-logic", page 23~27
    :return:
    """
    Smart = PrimitiveConcept("Smart")
    Studious = PrimitiveConcept("Studious")
    GoodStudent = DefinedConcept("GoodStudent", And(Smart, Studious))
    attendBy = Relation("attendBy")

    c1 = DefinedConcept("c1", And(Exists(attendBy, Smart), Exists(attendBy, Studious)))
    c2 = DefinedConcept("c2", Exists(attendBy, GoodStudent))

    print("is subsumption?", is_subsumption_of(c1, c2))
    # should be false

def hw2q3a_ws3q1a():
    """
    homework 2, question 3a
    worksheet 3, question 1a
    :return:
    """
    A = PrimitiveConcept("A")
    B = PrimitiveConcept("B")
    C = PrimitiveConcept("C")
    r = Relation("r")
    s = Relation("s")

    p1 = ForAll(r, ForAll(s, A))
    p2 = Exists(r, ForAll(s, B))
    p3 = ForAll(r, Exists(s, C))
    p4 = Exists(r, Exists(s, And(A, And(B, C))))

    c1 = DefinedConcept("c1", And(p1, And(p2, p3)))
    c2 = DefinedConcept("c2", p4)

    print("is subsumption?", is_subsumption_of(c1, c2))
    # should be true


def hw2q3b_ws3q1b():
    """
    homework 2, question 3b
    worksheet 3, question 1b
    :return:
    """
    A = PrimitiveConcept("A")
    B = PrimitiveConcept("B")
    C = PrimitiveConcept("C")
    r = Relation("r")
    s = Relation("s")
    p1 = ForAll(r, ForAll(s, A))
    p2 = Or(Exists(r, ForAll(s, Not(A))), ForAll(r, Exists(s, B)))
    p3 = Or(ForAll(r, Exists(s, And(A, B))), Exists(r, ForAll(s, Not(B))))

    c1 = DefinedConcept("c1", And(p1, p2))
    c2 = DefinedConcept("c2", p3)

    print("is subsumption?", is_subsumption_of(c1, c2))
    # should be true


def ws3q2():
    """
    worksheet 3, question 2
    :return:
    """
    A = PrimitiveConcept("A")
    r = Relation("r")

    a = Constant("a")
    b = Constant("b")
    c = Constant("c")
    d = Constant("d")
    w = Exists(r, Or(And(A,Exists(r, A)), Or(Not(A), Exists(r, Exists(r, Not(A))))))
    abox = {r(a,b), r(b,d), r(d,c), r(a,c), r(c,d), A(d), Not(w)(a)}

    print(run_tableau_algo(process_abox(abox)))
    # consistency false -> A is an instance

def notep128_priority1():
    """
    involves priority between rules
    :return:
    """
    P = PrimitiveConcept("P")
    r = Relation("r")
    a = Constant("a")

    abox = {P(a), AtMost(1,r,P)(a), Exists(r,P)(a), ForAll(r, Exists(r, P))(a), r(a,a)}
    print(run_tableau_algo(process_abox(abox)))
    # should finish with consistency true
    # no inf loop


def notep127():
    """
    a obvious inconsistent abox
    :return:
    """
    child = Relation("child")
    Female = PrimitiveConcept("Female")

    p1 = AtLeast(3, child, Top)
    p2 = AtMost(1, child, Female)
    p3 = AtMost(1, child, Not(Female))

    w = And(p1, And(p2, p3))
    a = Constant("a")
    abox = {w(a)}

    print(run_tableau_algo(process_abox(abox)))
    # consistency should be false


def hw2q4():
    """
    homework 2, question 4
    :return:
    """
    hasChild = Relation("HasChild")
    ParentWithMax2Children = DefinedConcept("ParentWithMax2Children", AtMost(2, hasChild, Top))
    joe = Constant("joe")
    ann = Constant("ann")
    eva = Constant("eva")
    mary = Constant("mary")

    abox = {hasChild(joe, ann), hasChild(joe, eva), hasChild(joe,mary),
            ParentWithMax2Children(joe)}

    run_tableau_algo(process_abox(abox))
    # consistency should be true
    # check the world: 3 different build methods (choose 2 from 3 to combine)
    # [CS('eva'), CS('ann~mary')]
    # [CS('ann'), CS('eva~mary')]
    # [CS('mary'), CS('ann~eva')]


def parent_child_extensive():
    """
    an extensive check for number restrictions
    :return:
    """
    # need to uncomment the part you want to test before running

    hasChild = Relation("HasChild")
    ParentWithMax5Children = DefinedConcept("ParentWithMax5Children", AtMost(5, hasChild, Top))
    ParentWithMax4Children = DefinedConcept("ParentWithMax4Children", AtMost(4, hasChild, Top))
    ParentWithMax3Children = DefinedConcept("ParentWithMax3Children", AtMost(3, hasChild, Top))
    ParentWithMax2Children = DefinedConcept("ParentWithMax2Children", AtMost(2, hasChild, Top))
    ParentWithMax1Children = DefinedConcept("ParentWithMax1Children", AtMost(1, hasChild, Top))
    ParentWithMax0Children = DefinedConcept("ParentWithMax0Children", AtMost(0, hasChild, Top))

    ParentWithMin0Children = DefinedConcept("ParentWithMin0Children", AtLeast(0, hasChild, Top))
    ParentWithMin1Children = DefinedConcept("ParentWithMin0Children", AtLeast(1, hasChild, Top))
    ParentWithMin2Children = DefinedConcept("ParentWithMin0Children", AtLeast(2, hasChild, Top))
    ParentWithMin3Children = DefinedConcept("ParentWithMin0Children", AtLeast(3, hasChild, Top))
    ParentWithMin4Children = DefinedConcept("ParentWithMin0Children", AtLeast(4, hasChild, Top))
    ParentWithMin5Children = DefinedConcept("ParentWithMin0Children", AtLeast(5, hasChild, Top))

    joe = Constant("joe")

    ann = Constant("ann")
    eva = Constant("eva")
    mary = Constant("mary")
    andy = Constant("andy")

    abox_base = {hasChild(joe, ann), hasChild(joe, eva), hasChild(joe, mary), hasChild(joe, andy)}

    # 1 world
    # abox_base.add(ParentWithMax5Children(joe))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world
    # min 6, no ineq, need to generate 6 constant
    # abox_base.add(Not(ParentWithMax5Children)(joe))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world
    # abox_base.add(ParentWithMax4Children(joe))
    # run_tableau_algo(process_abox(abox_base))

    ## 6 worlds: c(4,3)
    # 6 [True, True, True, True, True, True]
    # abox_base.add(ParentWithMax3Children(joe))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world
    # max 3 -> min 4
    # no eq, should generate 4 constant
    # abox_base.add(Not(ParentWithMax3Children)(joe))
    # run_tableau_algo(process_abox(abox_base))

    # 7 worlds: c(4,2)/2 + c(4,3)
    #  7 [True, True, True, True, True, True, True]
    # abox_base.add(ParentWithMax2Children(joe))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world
    # max 2 -> min 3
    # no ineq, generate 3
    # abox_base.add(Not(ParentWithMax2Children)(joe))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world: all combined
    # abox_base.add(ParentWithMax1Children(joe))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world, direct false
    # abox_base.add(ParentWithMax0Children(joe))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world, true
    # abox_base.add(ParentWithMin0Children(joe))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world, true
    # if there already child, then just check
    # abox_base.add(ParentWithMin1Children(joe))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world, true
    # if there is no child, then build a child
    # abox_base = set()
    # abox_base.add(ParentWithMin1Children(joe))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world, true
    # here is 2, but no ineq exists, thus should build 2
    abox_base.add(ParentWithMin2Children(joe))
    run_tableau_algo(process_abox(abox_base))

    # 1 world, true
    # here one ineq exists, no need to build
    # abox_base.add(ParentWithMin2Children(joe))
    # abox_base.add(ne(andy, ann))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world, true
    # no ineq, build 3
    # abox_base.add(ParentWithMin3Children(joe))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world, true
    # only 1 eq, need to build 3
    # abox_base.add(ParentWithMin3Children(joe))
    # abox_base.add(ne(andy, ann))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world true
    # no choose 3 exist, need to build
    # abox_base.add(ParentWithMin3Children(joe))
    # abox_base.add(ne(andy, ann))
    # abox_base.add(ne(andy, eva))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world, true
    # have one n=3 combination, no need to build 3 new constant
    # abox_base.add(ParentWithMin3Children(joe))
    # abox_base.add(ne(andy, ann))
    # abox_base.add(ne(andy, eva))
    # abox_base.add(ne(ann, eva))
    # run_tableau_algo(process_abox(abox_base))

    # not min 3 = max 2
    # find the first n=3 combination that all inequlity combination (C(3,2)=3) is not a subset of abox
    # if there is overlap, but not fully in, is not a subset
    # thus find the first subset [CS('mary'), CS('eva'), CS('ann')]
    # not the subset [andy, ann, eva} that has full ineq
    # and as eva!=ann, only 2 combine -> 2 world
    # seems legit to me
    # abox_base.add(Not(ParentWithMin3Children)(joe))
    # abox_base.add(ne(andy, ann))
    # abox_base.add(ne(andy, eva))
    # abox_base.add(ne(ann, eva))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world
    # no ineq, build 4 constant
    # abox_base.add(ParentWithMin4Children(joe))
    # run_tableau_algo(process_abox(abox_base))

    # reduce to max 3 child
    # should have 6 world: c(4,2)
    # abox_base.add(Not(ParentWithMin4Children)(joe))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world
    # no ineq, build 5 constant
    # abox_base.add(ParentWithMin5Children(joe))
    # run_tableau_algo(process_abox(abox_base))

    # 1 world, true
    # reduce to min 4 child
    # abox_base.add(Not(ParentWithMin5Children)(joe))
    # run_tableau_algo(process_abox(abox_base))


def love_hate():
    """
    mainly for checking subsumptions
    :return:
    """

    alice = Constant("alice")
    bob = Constant("bob")
    charile = Constant("charile")
    zoe = Constant("zoe")

    lovedBy = Relation("love")
    hatedBy = Relation("hate")

    BeLoved = DefinedConcept("BeLoved", AtLeast(1, lovedBy, Top))
    BeHated = DefinedConcept("BeHated", AtLeast(1, hatedBy, Top))
    LovedByAtMost2 = DefinedConcept("LovedByAtMost3", AtMost(2, lovedBy, Top))
    LovedByAtMost3 = DefinedConcept("LovedByAtMost3", AtMost(3, lovedBy, Top))
    HatedByAtLeast2 = DefinedConcept("HatedByAtLeast2", AtLeast(2, hatedBy, Top))
    HatedByAtLeast3 = DefinedConcept("HatedByAtLeast2", AtLeast(3, hatedBy, Top))
    AllLoved = DefinedConcept("AllLoved", ForAll(lovedBy, Top))
    AllHated = DefinedConcept("AllHated", ForAll(hatedBy, Top))

    LovedByAtLeast1 = DefinedConcept("ll1", AtLeast(1, lovedBy, Top))
    LovedByExist = DefinedConcept("le", Exists(lovedBy, Top))

    # Simple: 2nd argument is the larger
    # C ⊑T D
    print("is subsumption?", is_subsumption_of(LovedByAtMost2, LovedByAtMost3)) # true
    # print("is subsumption?", is_subsumption_of(LovedByAtMost3, LovedByAtMost2)) # false
    # print("is subsumption?", is_subsumption_of(HatedByAtLeast2, HatedByAtLeast3)) # false
    # print("is subsumption?", is_subsumption_of(HatedByAtLeast3, HatedByAtLeast2)) # true

    # print("is subsumption?", is_subsumption_of(LovedByAtMost3, HatedByAtLeast2)) # false

    # print("is subsumption?", is_subsumption_of(LovedByAtLeast1, LovedByExist)) # true
    # print("is subsumption?", is_subsumption_of(LovedByExist, LovedByAtLeast1)) # true

    abox_base = {lovedBy(alice, bob), lovedBy(alice, charile), lovedBy(alice, zoe),
                 hatedBy(zoe, bob), hatedBy(alice, zoe), hatedBy(zoe, charile), hatedBy(zoe, zoe)}

    # Remark: using *not* to check if constance is an instance of a concept...

    # abox_base.add(Not(LovedByAtMost3)(alice))
    # run_tableau_algo(process_abox(abox_base))

    # abox_base.add(Not(HatedByAtLeast2)(zoe))
    # run_tableau_algo(process_abox(abox_base))

def main():
    """
    all test cases

    hw = homework = assignment
    ws = worksheet
    :return:
    """

    # good_student()
    # hw2q3a_ws3q1a()
    # hw2q3b_ws3q1b()
    # ws3q2()
    # notep128_priority1()
    # notep127()
    hw2q4()
    # parent_child_extensive()
    # love_hate()

if __name__ == '__main__':
    main()