(set-logic QF_BV)
(set-option :produce-models true)

(declare-const used (_ BitVec 64))
(declare-const requested (_ BitVec 64))
(declare-const capacity (_ BitVec 64))

; A 65-bit sum can represent the sum of any two unsigned 64-bit values.
(define-fun reference () Bool
  (bvule (bvadd ((_ zero_extend 1) used) ((_ zero_extend 1) requested))
         ((_ zero_extend 1) capacity)))
(define-fun wrapping () Bool
  (bvule (bvadd used requested) capacity))
(define-fun guarded () Bool
  (and (bvule used capacity) (bvule requested (bvsub capacity used))))

(echo "Wrapping predicate disagrees with reference")
(push 1)
(assert (distinct wrapping reference))
(check-sat)

(echo "Reported witness")
(assert (= used #xfffffffffffffffd))
(assert (= requested #x0000000000000003))
(assert (= capacity #xfffffffffffffffe))
(check-sat)
(get-value (used requested capacity wrapping reference))
(pop 1)

(echo "Guarded predicate disagrees with reference")
(push 1)
(assert (distinct guarded reference))
(check-sat)
(pop 1)
