# Caltech SURF 2013
# FILE: test_plink_load.py
# 09.03.13

'''tests for plink_load.py'''
# functions also tested (indirectly) in test_graph_quad.py

from plink_load import *
import nose, os
from nose.tools import assert_raises

def test_is_nonsplit():
    path = os.path.abspath(os.path.dirname(sys.argv[0]))
    data5 = load_plink('%s/testing/t5_out_of_order.txt' % path)
    assert is_nonsplit(2, data5[1], data5[2])
    
    assert_raises(ValueError, load_plink, \
                  '%s/testing/t6_split_outoforder.txt' % path)
    assert_raises(ValueError, load_plink, \
                  '%s/testing/t7_split_unknot.txt' % path)
    assert_raises(ValueError, load_plink, \
                  '%s/testing/t8_split_3comp.txt' % path)
    assert_raises(ValueError, load_plink, \
                  '%s/testing/t9_3unknots.txt' % path)

if __name__ == '__main__':
    nose.runmodule()