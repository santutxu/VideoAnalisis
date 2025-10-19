#!/usr/bin/env python3
"""
VideoTacticsAnalyzer - Aplicación de análisis táctico deportivo
Similar a OpenShot + Longomatch para análisis de video deportivo
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QIcon, QPalette, QColor

# Configurar información de la aplicación
QCoreApplication.setOrganizationName("TacticalSports")
QCoreApplication.setApplicationName("VideoTacticsAnalyzer")
QCoreApplication.setApplicationVersion("1.0.0")

from windows.main_window import MainWindow

def setup_application_style(app):
    """Configura el estilo visual de la aplicación"""
    app.setStyle('Fusion')
    
    # Cargar hoja de estilos si existe
    style_path = 'resources/styles/dark_theme.qss'
    if os.path.exists(style_path):
        with open(style_path, 'r') as f:
            app.setStyleSheet(f.read())
    else:
        # Estilo oscuro por defecto si no existe el archivo
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(palette)

def main():
    # Habilitar DPI alto en Windows
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Configurar estilo
    setup_application_style(app)
    
    # Configurar icono de la aplicación
    icon_path = 'resources/icons/app_icon.png'
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Crear y mostrar ventana principal
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()