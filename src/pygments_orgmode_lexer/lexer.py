# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation, too-few-public-methods
""" OrgMode lexer for Pygments.

    See `Write your own lexer`_ and `Builtin Tokens`_.

    .. _`Write your own lexer`: http://pygments.org/docs/lexerdevelopment/
    .. _`Builtin Tokens`: http://pygments.org/docs/tokens/
"""
# Copyright © 2017 Oliver Runge <oliver.runge@gmail.com>
# Heavily based on https://github.com/jhermann/pygments-markdown-lexer.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import, unicode_literals, print_function

import re

from pygments.lexer import RegexLexer, include, bygroups, using, this, do_insertions, default, words
from pygments.token import *  # pylint: disable=wildcard-import, unused-wildcard-import

from ._compat import encode_filename as state


class OrgMode(object):
    """Symbolic names for org-mode tokens."""
    Markup = Keyword
    Block = Comment.Preproc
    Heading1 = Keyword.Namespace
    Heading2 = Keyword
    Heading3 = Name.Class
    Heading4 = Keyword.Namespace
    HeadingRest = Literal.String
    MetaData = Comment.Preproc
    Drawer = Comment.Multiline
    TodoActive = Keyword.Declaration
    TodoPending = Keyword.Pseudo
    TodoTerminal = Keyword.Reserved
    Timestamp = Name.Function.Magic

    def heading(lexer, match):
        level = match.group(1)
        todo = match.group(2)
        name = match.group(3)
        end = match.group(4)
        levels = [
            OrgMode.Heading1,
            OrgMode.Heading2,
            OrgMode.Heading3,
            OrgMode.Heading4,
            OrgMode.HeadingRest,
        ]
        heading_token = levels[min(len(level) - 1, len(levels) - 1)]
        if todo:
            todo_tokens = {
                'TODO': OrgMode.TodoActive,
                'DONE': OrgMode.TodoTerminal,
                'WAIT': OrgMode.TodoPending,
                'CANCELLED': OrgMode.TodoTerminal,
            }
            todo_token = todo_tokens.get(todo.upper(), OrgMode.TodoActive)

        yield match.start(), heading_token, level
        if todo:
            yield match.start(2), todo_token, todo

        yield match.start(3), heading_token, name
        yield match.start(4), Text, end


class OrgModeLexer(RegexLexer):
    """
        An org-mode lexer for Pygments.

        Some rules adapted from code in ``pygments.lexers.markup`` (BSD-licensed).
    """
    name = 'OrgMode'
    aliases = ['org', 'orgmode']
    filenames = ['*.org', '*.org_archive']
    mimetypes = ["text/x-org-mode"]
    flags = re.MULTILINE

    # from docutils.parsers.rst.states
    closers = u'\'")]}>\u2019\u201d\xbb!?'
    unicode_delimiters = u'\u2010\u2011\u2012\u2013\u2014\u00a0'
    end_string_suffix = (r'((?=$)|(?=[-/:.,; \n\x00%s%s]))'
                         % (re.escape(unicode_delimiters),
                            re.escape(closers)))

    tokens = {
        state('root'): [
            # Headings
            (r'^([*]{1,} *)(TODO|DONE|WAIT|CANCELLED)?(.+?)(\n)',
             OrgMode.heading),

            (r'^ *#\+BEGIN_SRC.*?\n',
             OrgMode.Block,
             state('codeblock')),
            (r'^ *#\+BEGIN_(QUOTE|EXAMPLE|VERSE).*?\n',
             OrgMode.Block,
             state('block')),

            # metadata
            (r'^( *#\+[a-zA-Z0-9].*)(\n)',
             bygroups(OrgMode.MetaData, Text)),
            # drawers and property names: :FOOBAR:
            (r'^( *:[a-zA-Z0-9].*:.*)(\n)',
             bygroups(OrgMode.Drawer, Text)),
            # closed, scheduled, deadline lines
            (r'^ *(CLOSED|SCHEDULED|DEADLINE)',
             OrgMode.Drawer,
             state("scheduled")),

            # Lists
            (r'^\s*[-+]\s', OrgMode.Markup),
            (r'^\s*[0-9]+\.\s', OrgMode.Markup),

            include(state('inline')),
        ],
        state('todo'): [
            (r'TODO', OrgMode.TodoActive, state("#pop")),
            (r'DONE', OrgMode.TodoTerminal, state("#pop")),
            (r'WAIT', OrgMode.TodoPending, state("#pop")),
            (r'CANCELLED', OrgMode.TodoTerminal, state("#pop")),
        ],
        state('scheduled'): [
            (r'[<\[]....-..-.. ... ..:..[\]>]', OrgMode.Timestamp),
            (r'[a-zA-Z0-9 ]+', OrgMode.Drawer),  # optimize normal words a little
            (r'\n', Text, state('#pop')),
            (r'.', OrgMode.Drawer),  # default fallback
        ],
        state('inline'): [
            # escaping (before everything else)
            (r'\\.', String.Escape),

            (r'(=)(.+?)(=)',
             bygroups(OrgMode.Markup, Generic.Emph, OrgMode.Markup)),
            (r'([*])(.+?)([*])',
             bygroups(OrgMode.Markup, Generic.Strong, OrgMode.Markup)),

            (r'[<\[]....-..-.. ... ..:..[\]>]', OrgMode.Timestamp),

            # Remaining text
            (r'[a-zA-Z0-9 ]+', Text),  # optimize normal words a little
            (r'.', Text),  # default fallback
        ],
        state('block'): [
            (r'^ *#\+END_(QUOTE|EXAMPLE|VERSE).*?\n',
             OrgMode.Block, state('#pop')),
            (r'\n', OrgMode.Block), # without this the state is lost
            (r'[a-zA-Z0-9 ]+', OrgMode.Block),  # optimize normal words a little
            (r'.', OrgMode.Block),  # default fallback
        ],
        state('codeblock'): [
            (r'^ *#\+END_SRC.*?\n', OrgMode.Block, state('#pop')),
            (r'\n', OrgMode.Block), # without this the state is lost
            (r'[a-zA-Z0-9 ]+', OrgMode.Block),  # optimize normal words a little
            (r'.', OrgMode.Block),  # default fallback
        ],
    }