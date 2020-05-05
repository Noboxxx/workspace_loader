"""
package : 
file : messages.py

description : 
"""

# imports python
import sys

# imports third-parties
import maya.cmds


def f_msg(msg, prefix, suffix, new_line_after):
    """doc string here

    :param msg:
    :type msg:
    :param prefix:
    :type prefix:
    :param suffix:
    :type suffix:
    :param new_line_after:
    :type new_line_after:
    :return:
    :rtype:
    """


    s = ''

    if prefix != '':
        s += '{0} : '.format(prefix)

    s += str(msg)

    if suffix != '':
        s += ' / {0}'.format(suffix)

    if new_line_after:
        s += '\n'

    return s


def warning(msg='', prefix='', suffix='', new_line_after=False):
    """doc string here

    :param msg:
    :type msg:
    :param prefix:
    :type prefix:
    :param suffix:
    :type suffix:
    :param new_line_after:
    :type new_line_after:
    :return:
    :rtype:
    """

    maya.cmds.warning(f_msg(msg, prefix, suffix, new_line_after))


def error(msg='', prefix='', suffix='', new_line_after=False):
    """docstring here

    :param msg:
    :type msg:
    :param prefix:
    :type prefix:
    :param suffix:
    :type suffix:
    :param new_line_after:
    :type new_line_after:
    :return:
    :rtype:
    """

    maya.cmds.error(f_msg(msg, prefix, suffix, new_line_after))


def info(msg='', prefix='', suffix='', new_line_after=False):
    """doc string here

    :param msg:
    :type msg:
    :param prefix:
    :type prefix:
    :param suffix:
    :type suffix:
    :param new_line_after:
    :type new_line_after:
    :return:
    :rtype:
    """

    sys.stdout.write('{0}\n'.format(f_msg(msg, prefix, suffix, new_line_after)))
