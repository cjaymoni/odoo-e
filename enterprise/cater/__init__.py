# -*- coding: utf-8 -*-

from . import models
from . import controllers
from .hooks import post_init_hook
# Don't import tests module - it's loaded automatically by Odoo when running tests
