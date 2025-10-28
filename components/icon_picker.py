import sys


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from resources.icon_data_base import IconDatabase, IconList


class IconPickerWindow(QDialog):
    
    icon_selected = pyqtSignal(dict,int) 
    
    def __init__(self,event_type,row):
        super().__init__()
        self.iconlist = IconList()
        self.event_type = event_type
        self.row = row
        #self.icons = sorted([attr for attr in dir(QStyle) if attr.startswith("SP_")])
        
        layout = QGridLayout()
        self.load_icons()
        for n, icono in enumerate(self.icons):
            name = icono.name
            btn = QPushButton(f"{icono.emoji}" )

            #pixmapi = getattr(QStyle, name)
            #icon = self.style().standardIcon(pixmapi)
            icon  = QIcon(icono.emoji)
            #btn.setIcon(icon)
            #btn.click = (lambda checked, n=icon: self.icon_selected(n))
            btn.clicked.connect(lambda checked, n=icono: self.on_icon_selected(n))
            layout.addWidget(btn, n // 10, n % 10)

        self.setLayout(layout)
        
    def on_icon_selected(self, icon):
            print("Icon selected:", icon)
            new_icon = {
                "name": icon.name,
                "emoji": icon.emoji,
                "category": icon.category,
                "keywords": icon.keywords
            }
            self.icon_selected.emit(new_icon,self.row)
            self.accept()
        
    def load_icons(self):
        self.icons = self.iconlist.get_all_icons()

'''
app = QApplication(sys.argv)

w = Window()
w.show()

app.exec_
'''