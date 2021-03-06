# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bs4 import BeautifulSoup
from django.test import override_settings
from cms.api import add_plugin
from cms.utils.plugins import build_plugin_tree
from cmsplugin_cascade.bootstrap3.container import (BootstrapContainerPlugin, BootstrapRowPlugin,
        BootstrapColumnPlugin)
from cmsplugin_cascade.bootstrap3.accordion import (BootstrapAccordionPlugin,
    BootstrapAccordionPanelPlugin)
from cmsplugin_cascade import app_settings
from .test_base import CascadeTestCase


BS3_BREAKPOINT_KEYS = list(tp[0] for tp in app_settings.CMSPLUGIN_CASCADE['bootstrap3']['breakpoints'])


class AccordionPluginTest(CascadeTestCase):

    def build_accordion_plugins(self):
        # create container
        container_model = add_plugin(self.placeholder, BootstrapContainerPlugin, 'en',
            glossary={'breakpoints': BS3_BREAKPOINT_KEYS})
        container_plugin = container_model.get_plugin_class_instance()
        self.assertIsInstance(container_plugin, BootstrapContainerPlugin)

        # add one row
        row_model = add_plugin(self.placeholder, BootstrapRowPlugin, 'en', target=container_model,
                               glossary={})
        row_plugin = row_model.get_plugin_class_instance()
        self.assertIsInstance(row_plugin, BootstrapRowPlugin)

        # add one column
        column_model = add_plugin(self.placeholder, BootstrapColumnPlugin, 'en', target=row_model,
            glossary={'xs-column-width': 'col-xs-12', 'sm-column-width': 'col-sm-6',
                      'md-column-width': 'col-md-4', 'lg-column-width': 'col-lg-3'})
        column_plugin = column_model.get_plugin_class_instance()
        self.assertIsInstance(column_plugin, BootstrapColumnPlugin)

        # add accordion plugin
        accordion_model = add_plugin(self.placeholder, BootstrapAccordionPlugin, 'en', target=column_model)
        accordion_plugin = accordion_model.get_plugin_class_instance()
        self.assertIsInstance(accordion_plugin, BootstrapAccordionPlugin)
        accordion_plugin.cms_plugin_instance = accordion_model.cmsplugin_ptr

        # add accordion panel
        panel_model = add_plugin(self.placeholder, BootstrapAccordionPanelPlugin, 'en',
            target=accordion_model, glossary={'panel_type': "panel-danger", 'panel_title': "Foo"})
        panel_plugin = panel_model.get_plugin_class_instance()
        self.assertIsInstance(panel_plugin, BootstrapAccordionPanelPlugin)
        panel_plugin.cms_plugin_instance = panel_model.cmsplugin_ptr

        # render the plugins
        plugin_list = [container_model, row_model, column_model, accordion_model, panel_model]
        build_plugin_tree(plugin_list)

        self.assertEqual(accordion_plugin.get_identifier(accordion_model), 'with 1 panel')
        self.assertEqual(panel_plugin.get_identifier(panel_model), 'Foo')

        return self.get_html(container_model, self.get_request_context())

    @override_settings()
    def test_bootstrap_accordion(self):
        try:
            del app_settings.CMSPLUGIN_CASCADE['bootstrap3']['template_basedir']
        except KeyError:
            pass
        html = self.build_accordion_plugins()
        soup = BeautifulSoup(html)
        panel_group = soup.find('div', class_='panel-group')
        self.assertIsNotNone(panel_group)

    @override_settings()
    def test_angular_bootstrap_accordion(self):
        app_settings.CMSPLUGIN_CASCADE['bootstrap3'].update({'template_basedir': 'angular-ui'})
        html = self.build_accordion_plugins()
        soup = BeautifulSoup(html)
        accordion = soup.find('uib-accordion')
        self.assertIsNotNone(accordion)
