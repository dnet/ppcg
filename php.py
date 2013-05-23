#!/usr/bin/env python

from __future__ import with_statement
from itertools import imap
from subprocess import Popen, PIPE
from threading import RLock

class PHP(object):
	def __init__(self, php_executable='php'):
		self._statements = []
		self._php_exec = php_executable
		self._queue = []

	def __str__(self):
		php = Popen([self._php_exec], stdin=PIPE, stdout=PIPE, stderr=PIPE)
		php.stdin.write('<?\n')
		for stmt in self._statements:
			php.stdin.write(str(stmt))
		php.stdin.write('?>\n')
		stdout, stderr = php.communicate()
		if php.returncode != 0:
			raise PhpError(stderr)
		self._statements = []
		return stdout
	
	def new(self, class_name, *args):
		return getattr(self, 'new ' + class_name)(*args)

	def _add_statement(self, stmt):
		self._statements.append(stmt)

	def _align_statement(self, stmt):
		if self._queue:
			leader = self._queue[0]
			q_idx = self._statements.index(leader)
			s_idx = self._statements.index(stmt)
			if q_idx > s_idx:
				return
			self._statements.remove(leader)
			self._statements.insert(s_idx + 1, leader)

	def __getattr__(self, name):
		stmt = Statement(self, name)
		self._add_statement(stmt)
		return Token(self, stmt)

	def __repr__(self):
		return '<PHP object with {0} statement(s)>'.format(len(self._statements))


class PhpError(RuntimeError):
	pass


class Statement(object):
	VARNUM = 0
	VARNUM_LOCK = RLock()

	def __init__(self, php, contents):
		self.php = php
		self.contents = contents
		self.retval_in = None
	
	def append(self, value):
		self.contents += value

	def _get_php(self):
		if self.retval_in is None:
			self.php._align_statement(self)
			with self.VARNUM_LOCK:
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
		self.php._queue.append(self.stmt)
		self.stmt.append('({args})'.format(
			args=', '.join(imap(format_value, args))))
		self.php._queue.pop()
		return self

	def _get_php(self):
		return self.stmt._get_php()

	def __getattr__(self, name):
		return self._handle_op('{left}->' + name)

	def __getitem__(self, name):
		return self._handle_op('{left}[{right}]', name)

	def __add__(self, value):
		return self._handle_op('{left}' +
				(' . ' if isinstance(value, basestring) else ' + ') +
				'{right}', value)

	def _handle_op(self, fmt, value=None):
		stmt = Statement(self.php, fmt.format(
			left=self.stmt._get_php(), right=format_value(value)))
		self.php._add_statement(stmt)
		return Token(self.php, stmt)


def format_value(value):
	if isinstance(value, basestring):
		return "'" + value.replace('\\', r'\\').replace("'", r"\'") + "'"
	elif value is None:
		return 'null'
	elif isinstance(value, (Statement, Token)):
		return value._get_php()
	elif isinstance(value, list):
		return 'array({items})'.format(items=', '.join(imap(format_value, value)))
	elif isinstance(value, dict):
		return 'array({items})'.format(items=', '.join(' => '.join(
			imap(format_value, item)) for item in value.iteritems()))
	else:
		return str(value)
