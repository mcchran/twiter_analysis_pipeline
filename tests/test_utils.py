import os
import sys
from unittest import TestCase
from mock import MagicMock, patch

# importing our own code:
root = os.path.join(os.path.dirname(__file__))
package = os.path.join(root, "..")
sys.path.insert(0, os.path.abspath(package))

from analyzer.utils import Chain, ChainExcpetion


class ChainTestCase(TestCase):

    def setUp(self):
        self.logger = MagicMock()
        self.chain = Chain(self.logger.log)
        self.func1 = MagicMock(return_value=[1,2])
        self.func2 = MagicMock(return_value="test")
        self.chain.append(self.func1)
        self.chain.append(self.func2)

    def test_success(self):
        last_func = MagicMock(return_value="fine")
        self.chain.append(last_func)

        result = self.chain.run("data")
        self.func1.assert_called_once_with('data')
        self.func2.assert_called_once_with([1,2])
        last_func.assert_called_once_with("test")
        self.assertEqual(result, 'fine')

    def test_raises(self):
        last_func = MagicMock(side_effect=Exception('something went really wrong'))
        self.chain.append(last_func)
        with self.assertRaises(ChainExcpetion):
            result = self.chain.run("data")
        self.logger.log.assert_called_once()