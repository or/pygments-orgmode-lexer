# -*- coding: utf-8 -*-
# pylint: disable=bad-whitespace
# flake8: noqa
"""
    Pygments org-mode Lexer – An org-mode lexer for Pygments to
    highlight org-mode code snippets.

    Copyright © 2017 Oliver Runge <oliver.runge@gmail.com>
    Heavily based on https://github.com/jhermann/pygments-markdown-lexer.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from __future__ import absolute_import, unicode_literals, print_function

from .lexer import OrgModeLexer

__url__             = "https://github.com/or/pygments-orgmode-lexer"
__version__         = "0.1"
__license__         = "Apache 2.0"
__author__          = "Oliver Runge"
__author_email__    = "oliver.runge@gmail.com"
__keywords__        = "hosted.by.github pygments orgmode lexer highlighting"


def setup(app):
    """ Initializer for Sphinx extension API.

        See http://www.sphinx-doc.org/en/stable/extdev/index.html#dev-extensions.
    """
    lexer = OrgModeLexer()
    for alias in lexer.aliases:
        app.add_lexer(alias, lexer)

    return dict(version=__version__)


__all__ = ['OrgModeLexer', 'setup']
