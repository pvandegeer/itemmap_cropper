# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ItemMapCropper
                                 A QGIS plugin
 This plugin crops (resizes) the map item on a layout to precisely fit a map layer.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-02-21
        git sha              : $Format:%H$
        copyright            : (C) 2021 by P. van de Geer
        email                : pvandegeer@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os.path

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject, QgsLayoutItemRegistry

from .resources import *
from .itemmap_cropper_dialog import ItemMapCropperDialog

class ItemMapCropper:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ItemMapCropper_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ItemMapCropper', message)

    def initGui(self):
        """Setup hooks and prepare dialog"""
        self.iface.layoutDesignerOpened.connect(self.layout_opened)
        self.iface.layoutDesignerWillBeClosed.connect(self.layout_will_close)
        self.dlg = ItemMapCropperDialog()

    def unload(self):
        """Clean up after plugin is unloaded"""
        self.iface.layoutDesignerOpened.disconnect(self.layout_opened)
        self.iface.layoutDesignerWillBeClosed.disconnect(self.layout_will_close)

    def crop_itemmaps(self, designer):
        """Prompt for layer to crop to and resize itemmaps accordingly"""
        layout = designer.layout()

        if not layout.selectedLayoutItems():
            mb = designer.messageBar()
            mb.pushInfo(self.tr(u'No map item selected'), self.tr(u'select the item(s) you want to resize first.'))
            return

        if QgsProject.instance().count() == 0:
            return
        elif QgsProject.instance().count() == 1:
            layer = list(QgsProject.instance().mapLayers().values())[0]
        else:
            self.dlg.show()
            if self.dlg.exec_():
                layer = self.dlg.mMapLayerComboBox.currentLayer()
            else:
                return

        ext = layer.extent()
        items = layout.selectedLayoutItems()
        found = False
        for item in items:
            if item.type() == QgsLayoutItemRegistry.LayoutMap:
                item.setExtent(ext)
                found = True

        if not found:
            mb = designer.messageBar()
            mb.pushInfo(self.tr(u'No map item selected'), self.tr(u'function only works on map items.'))

    def layout_opened(self, designer):
        """Add customizations to the composer interface"""
        icon = QIcon(':/plugins/itemmap_cropper/mActionResizeToLayer.svg')
        action = QAction(icon, self.tr(u'&Crop map to layer...'), designer)
        action.triggered.connect(lambda: self.crop_itemmaps(designer))
        action.setEnabled(True)

        toolbar = designer.actionsToolbar()
        toolbar.insertAction(None, action)
        menu = designer.itemsMenu()
        menu.addSeparator()
        menu.insertAction(None, action)

        # todo: maybe add to context menu (https://gis.stackexchange.com/questions/250139/)
        # designer.view().menuProvider() / QgsLayoutViewMenuProvider / view.setMenuProvider(provider)

        # todo: hookup when bug in QGis is fixed
        # layout = designer.layout()
        # layout.selectedItemChanged.connect(self.selection_changed)

    def layout_will_close(self, designer):
        # cleanup
        pass

    def selection_changed(self, item):
        """Activate/deactivate button and menu when itemmap is selected"""
        # The user selected an item on the print layout
        # Not used ftm as there is a bug in QGis related to this: https://github.com/qgis/QGIS/issues/41721
        # if item is None:
        #     print ("deselected")
        # if item.type() == QgsLayoutItemRegistry.LayoutMap:
        #     print (".. is a map!")
        #     # activate menus and buttons
        pass