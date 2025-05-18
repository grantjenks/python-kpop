import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from kpop import k, kpop

class Dummy:
    def __init__(self):
        self.attr = 'value'
        self.data = {'a': 'A'}

    def multiply(self, x):
        return x * 2

    def error_func(self):
        raise RuntimeError('boom')

    def __getitem__(self, key):
        return self.data[key]

class BubbleTests(unittest.TestCase):
    def setUp(self):
        self.obj = Dummy()
        self.default = 'DEF'

    def test_getattr_success(self):
        b = k(self.obj, default=self.default).attr
        self.assertEqual(kpop(b), 'value')
        hist = b._get_history()
        self.assertEqual(len(hist), 1)
        op = hist[0]
        self.assertEqual(op.op, 'getattr')
        self.assertEqual(op.detail, 'attr')
        self.assertEqual(op.result, 'value')
        self.assertIsNone(op.exception)
        self.assertEqual(hist, b._get_error_history())

    def test_getattr_failure(self):
        b = k(self.obj, default=self.default).missing
        self.assertEqual(kpop(b), self.default)
        hist = b._get_history()
        self.assertEqual(len(hist), 1)
        op = hist[0]
        self.assertEqual(op.op, 'getattr')
        self.assertEqual(op.detail, 'missing')
        self.assertIsNone(op.result)
        self.assertIsNotNone(op.exception)
        self.assertEqual(hist, b._get_error_history())

    def test_getitem_success(self):
        b = k(self.obj, default=self.default)['a']
        self.assertEqual(kpop(b), 'A')
        hist = b._get_history()
        self.assertEqual(len(hist), 1)
        op = hist[0]
        self.assertEqual(op.op, 'getitem')
        self.assertEqual(op.detail, 'a')
        self.assertEqual(op.result, 'A')
        self.assertIsNone(op.exception)
        self.assertEqual(hist, b._get_error_history())

    def test_getitem_failure(self):
        b = k(self.obj, default=self.default)['b']
        self.assertEqual(kpop(b), self.default)
        hist = b._get_history()
        self.assertEqual(len(hist), 1)
        op = hist[0]
        self.assertEqual(op.op, 'getitem')
        self.assertEqual(op.detail, 'b')
        self.assertIsNone(op.result)
        self.assertIsNotNone(op.exception)
        self.assertEqual(hist, b._get_error_history())

    def test_call_success(self):
        b = k(self.obj, default=self.default).multiply(3)
        self.assertEqual(kpop(b), 6)
        hist = b._get_history()
        self.assertEqual(len(hist), 2)
        getattr_op, call_op = hist
        self.assertEqual(getattr_op.op, 'getattr')
        self.assertEqual(getattr_op.detail, 'multiply')
        self.assertEqual(call_op.op, 'call')
        self.assertEqual(call_op.detail['args'], (3,))
        self.assertEqual(call_op.result, 6)
        self.assertIsNone(call_op.exception)
        self.assertEqual(hist, b._get_error_history())

    def test_call_failure(self):
        b = k(self.obj, default=self.default).error_func()
        self.assertEqual(kpop(b), self.default)
        hist = b._get_history()
        self.assertEqual(len(hist), 2)
        getattr_op, call_op = hist
        self.assertEqual(getattr_op.op, 'getattr')
        self.assertEqual(getattr_op.detail, 'error_func')
        self.assertEqual(call_op.op, 'call')
        self.assertEqual(call_op.detail['args'], tuple())
        self.assertIsNone(call_op.result)
        self.assertIsNotNone(call_op.exception)
        self.assertEqual(hist, b._get_error_history())

    def test_chain_success_then_failure(self):
        b = k(self.obj, default=self.default).multiply(2).missing
        self.assertEqual(kpop(b), self.default)
        hist = b._get_history()
        self.assertEqual(len(hist), 3)
        getattr_op, call_op, fail_op = hist
        self.assertEqual(getattr_op.op, 'getattr')
        self.assertEqual(call_op.op, 'call')
        self.assertEqual(fail_op.op, 'getattr')
        self.assertEqual(len(b._get_error_history()), 3)

    def test_chain_failure_then_more_ops(self):
        b = k(self.obj, default=self.default).error_func().attr
        self.assertEqual(kpop(b), self.default)
        hist = b._get_history()
        self.assertEqual(len(hist), 3)
        getattr_op, call_op, after_op = hist
        self.assertEqual(getattr_op.op, 'getattr')
        self.assertEqual(call_op.op, 'call')
        self.assertEqual(after_op.op, 'getattr')
        self.assertEqual(len(b._get_error_history()), 2)

if __name__ == '__main__':
    unittest.main()
