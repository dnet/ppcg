#!/usr/bin/env python

from __future__ import with_statement
from php import PHP, PhpError
from time import time
import unittest

class TestPHP(unittest.TestCase):
	TEST_STRING = 'foobar"\\\'\n'
	def test_echo(self):
		php = PHP()
		php.echo(self.TEST_STRING)
		self.assertEquals(str(php), self.TEST_STRING)
	
	def test_error(self):
		php = PHP()
		php.nonexistant_method()
		with self.assertRaises(PhpError):
			str(php)
	
	def test_new(self):
		php = PHP()
		dt = php.new('DateTime')
		ts = dt.getTimestamp()
		php.echo(ts)
		output = str(php)
		self.assertAlmostEquals(int(output), time(), delta=10)
	
	def test_null(self):
		php = PHP()
		php.var_dump(None)
		self.assertEquals(str(php), 'NULL\n')
	
	def test_number(self):
		php = PHP()
		php.var_dump(5)
		self.assertEquals(str(php), 'int(5)\n')

	def test_compose(self):
		php = PHP()
		php.echo(php.strlen(self.TEST_STRING))
		output = str(php)
		self.assertEquals(output, str(len(self.TEST_STRING)))

	def test_deep_compose(self):
		php = PHP()
		php.echo(php.strlen(php.strrev(self.TEST_STRING)))
		output = str(php)
		self.assertEquals(output, str(len(self.TEST_STRING)))

	def test_repr(self):
		php = PHP()
		self.assertEquals(repr(php), '<PHP object with 0 statement(s)>')

	TEST_RANGE = 6
	def test_list(self):
		php = PHP()
		php.echo(php.count(range(self.TEST_RANGE)))
		output = str(php)
		self.assertEquals(output, str(self.TEST_RANGE))

	TEST_DICT = {'foo': 'bar', 2: 'qux'}
	def test_dict(self):
		php = PHP()
		values = php.array_values(self.TEST_DICT)
		php.sort(values)
		php.echo(php.implode(',', values))
		expected = ','.join(sorted(self.TEST_DICT.itervalues()))
		self.assertEquals(str(php), expected)

	def test_getitem(self):
		php = PHP()
		array_params = range(self.TEST_RANGE)
		array = php.array(*array_params)
		php.echo(array[0])
		self.assertEquals(str(php), str(array_params[0]))

	def test_dyn_getitem(self):
		php = PHP()
		array_params = range(self.TEST_RANGE)
		array = php.array(*array_params)
		php.shuffle(array)
		php.echo(array[array[0]])
		self.assertIn(int(str(php)), array_params)


if __name__ == '__main__':
    unittest.main()
