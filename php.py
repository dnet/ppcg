#!/usr/bin/env python

from itertools import imap
from subprocess import Popen, PIPE

class PHP(object):
	def __init__(self, php_executable='php'):
		self._statements = []
		self._php_exec = php_executable

	def __str__(self):
		php = Popen([self._php_exec], stdin=PIPE, stdout=PIPE, stderr=PIPE)
		php.stdin.write('<?')
		for stmt in self._statements:
			php.stdin.write(str(stmt))
		php.stdin.write('?>');
		stdout, stderr = php.communicate()
		if php.returncode != 0:
			raise PhpError(stderr)
		self._statements = []
		return stdout
	
	def new(self, class_name, *args):
		return self.__getattr__('new ' + class_name)(*args)

	def _add_statement(self, stmt):
		self._statements.append(stmt)

	def __getattr__(self, name):
		stmt = Statement(name)
		self._add_statement(stmt)
		return Token(self, stmt)


class PhpError(RuntimeError):
	pass

class Statement(object):
	VARNUM = 0

	def __init__(self, contents):
		self.contents = contents
		self.retval_in = None
	
	def append(self, value):
		self.contents += value

	def _get_php(self):
		if self.retval_in is None:
			self.retval_in = '$v{0}'.format(Statement.VARNUM)
			Statement.VARNUM += 1
			self.contents = self.retval_in + ' = ' + self.contents
		return self.retval_in

	def __str__(self):
		return self.contents + ';\n'


class Token(object):
	def __init__(self, php, stmt):
		self.php = php
		self.stmt = stmt
	
	def __call__(self, *args):
		self.stmt.append('({args})'.format(
			args=', '.join(imap(format_value, args))))
		return self

	def _get_php(self):
		return self.stmt._get_php()

	def __getattr__(self, name):
		stmt = Statement(self.stmt._get_php() + '->' + name)
		self.php._add_statement(stmt)
		return Token(self.php, stmt) 


def format_value(value):
	if isinstance(value, basestring):
		return "'" + value.replace('\\', r'\\').replace("'", r"\'") + "'"
	elif value is None:
		return 'null'
	elif isinstance(value, (Statement, Token)):
		return value._get_php()
	else:
		return str(value)
