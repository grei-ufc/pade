#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Framework para Desenvolvimento de Agentes Inteligentes PADE

# The MIT License (MIT)

# Copyright (c) 2015 Lucas S Melo

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

try:
    from PySide import QtCore, QtGui
except Exception, e:
    print 'PySide nao esta instalado!'

from pade.acl.messages import ACLMessage
from uuid import uuid1
import sys


class AgentsGui(object):

    def setupUi(self, MainWindow):
        # Configura a instancia da classe MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(784, 542)

        # Instancia e configura o objeto sizePolicy
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())

        # Seta o parametro sizePolicy da instancia da classe MainWindow com o objeto sizePolicy
        MainWindow.setSizePolicy(sizePolicy)

        # Instancia o Objeto QWidget que abrigará os outros widgets
        self.widget = QtGui.QWidget(MainWindow)
        self.widget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.widget.setObjectName("widget")

        # Instancia e configura o objeto de layout verticalLayout
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_4.setObjectName("verticalLayout_4")

        # Instancia e configura o objeto de layout horizontalLayout
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Istancia o obejto groupBox
        self.groupBox = QtGui.QGroupBox(self.widget)
        self.groupBox.setObjectName("groupBox")

        # Instancia e configura o objeto verticalLayout
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        # Instancia o objeto listWidget
        self.listWidget = QtGui.QListWidget(self.groupBox)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout_2.addWidget(self.listWidget)

        # Adiciona o objeto groupBox ao horizontalLayout
        self.horizontalLayout.addWidget(self.groupBox)

        # Instancia o objeto groupBox_2
        self.groupBox_2 = QtGui.QGroupBox(self.widget)
        self.groupBox_2.setObjectName("groupBox_2")

        # Instancia e configura o objeto verticalLayout
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        # Instancia o objeto listWidget_2
        self.listWidget_2 = QtGui.QListWidget(self.groupBox_2)
        self.listWidget_2.setObjectName("listWidget_2")
        self.verticalLayout_3.addWidget(self.listWidget_2)

        # Adiciona o objeto groupBox_2 ao horizontalLayout
        self.horizontalLayout.addWidget(self.groupBox_2)

        # Adiciona o horizontalLayout ao verticalLayout
        self.verticalLayout_4.addLayout(self.horizontalLayout)

        # Seta o objeto self.widget a instancia da classe MainWindow
        MainWindow.setCentralWidget(self.widget)

        # Instancia e configura o obejto menubar
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 784, 25))
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setNativeMenuBar(True)
        MainWindow.setMenuBar(self.menubar)

        # Instancia os objetos menu
        self.fileMenu = QtGui.QMenu('')
        self.preferenciasAction = QtGui.QAction(QtGui.QIcon('./Imagens/preferencias.png'),'',self.fileMenu)
        self.preferenciasAction.triggered.connect(self.showPreferenciasDialog)

        self.fileMenu.addAction(self.preferenciasAction)
        # adiciona os menus
        self.menubar.addMenu(self.fileMenu)

        # instancia e configura o objeto toolbar
        self.toolbar = QtGui.QToolBar(MainWindow)
        self.toolbar.setObjectName("toolbar")
        self.toolbar.addAction(self.preferenciasAction)
        MainWindow.addToolBar(self.toolbar)

        # Instancia e configura o objeto statusbar
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def showPreferenciasDialog(self):
        print 'Abrir Dialog Preferencias'

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Interface de Gerenciamento dos Agentes", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow", "Agentes", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("MainWindow", "Mensagens", None, QtGui.QApplication.UnicodeUTF8))

        self.fileMenu.setTitle(QtGui.QApplication.translate("MainWindow", "Arquivo", None, QtGui.QApplication.UnicodeUTF8))
        self.preferenciasAction.setText(QtGui.QApplication.translate("MainWindow", "Preferências", None, QtGui.QApplication.UnicodeUTF8))


class ControlAgentsGui(QtGui.QMainWindow):
    def __init__(self):
        super(ControlAgentsGui, self).__init__()
        self.ui = AgentsGui()
        self.ui.setupUi(self)


class ACLMessageDialog(QtGui.QWidget):
    '''
        Esta classe cria uma interface gráfica de configuração de 
        uma mensagem do tipo ACLMessage
    '''

    def setupUi(self, Dialog):
        
        Dialog.setObjectName("Dialog")
        Dialog.resize(372, 512)
        
        self.formLayout = QtGui.QFormLayout(Dialog)
        self.formLayout.setObjectName("formLayout")
        
        self.conversationIdLabel = QtGui.QLabel(Dialog)
        self.conversationIdLabel.setObjectName("conversationIdLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.conversationIdLabel)
        
        self.conversationIdText = QtGui.QLineEdit(Dialog)
        self.conversationIdText.setObjectName("conversationIdText")
        self.conversationIdText.setText(str(uuid1()))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.conversationIdText)
        
        self.senderLabel = QtGui.QLabel(Dialog)
        self.senderLabel.setObjectName("senderLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.senderLabel)
        
        self.senderText = QtGui.QLineEdit(Dialog)
        self.senderText.setObjectName("senderText")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.senderText)
        
        self.receiverLabel = QtGui.QLabel(Dialog)
        self.receiverLabel.setObjectName("receiverLabel")
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.receiverLabel)
        
        # Instancia o objeto listWidget
        self.receiverListWidget = QtGui.QListWidget(Dialog)
        self.receiverListWidget.setObjectName("receiverListWidget")
        
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.receiverListWidget)
        
        self.communicativeActLabel = QtGui.QLabel(Dialog)
        self.communicativeActLabel.setObjectName("communicativeActLabel")
        self.formLayout.setWidget(8, QtGui.QFormLayout.LabelRole, self.communicativeActLabel)
        
        self.communicativeActComboBox = QtGui.QComboBox(Dialog)
        self.communicativeActComboBox.setObjectName("communicativeActComboBox")
        
        for performative in ACLMessage.performaives: 
            self.communicativeActComboBox.addItem(performative)
        
        self.formLayout.setWidget(8, QtGui.QFormLayout.FieldRole, self.communicativeActComboBox)
        
        self.contentLabel = QtGui.QLabel(Dialog)
        self.contentLabel.setObjectName("contentLabel")
        self.formLayout.setWidget(9, QtGui.QFormLayout.LabelRole, self.contentLabel)
        
        self.contentText = QtGui.QTextEdit(Dialog)
        self.contentText.setObjectName("contentText")
        self.formLayout.setWidget(9, QtGui.QFormLayout.FieldRole, self.contentText)
        
        self.protocolLabel = QtGui.QLabel(Dialog)
        self.protocolLabel.setObjectName("protocolLabel")
        self.formLayout.setWidget(10, QtGui.QFormLayout.LabelRole, self.protocolLabel)
        
        self.protocolComboBox = QtGui.QComboBox(Dialog)
        self.protocolComboBox.setObjectName("protocolComboBox")
        
        for protocol in ACLMessage.protocols:
            self.protocolComboBox.addItem(protocol)
        
        self.formLayout.setWidget(10, QtGui.QFormLayout.FieldRole, self.protocolComboBox)
        
        self.languageLabel = QtGui.QLabel(Dialog)
        self.languageLabel.setObjectName("languageLabel")
        self.formLayout.setWidget(11, QtGui.QFormLayout.LabelRole, self.languageLabel)
        
        self.languageText = QtGui.QLineEdit(Dialog)
        self.languageText.setObjectName("languageText")
        self.formLayout.setWidget(11, QtGui.QFormLayout.FieldRole, self.languageText)
        
        self.encodingLabel = QtGui.QLabel(Dialog)
        self.encodingLabel.setObjectName("encodingLabel")
        self.formLayout.setWidget(13, QtGui.QFormLayout.LabelRole, self.encodingLabel)
        
        self.encodingText = QtGui.QLineEdit(Dialog)
        self.encodingText.setObjectName("encodingText")
        self.formLayout.setWidget(13, QtGui.QFormLayout.FieldRole, self.encodingText)
        
        self.ontologyLabel = QtGui.QLabel(Dialog)
        self.ontologyLabel.setObjectName("ontologyLabel")
        self.formLayout.setWidget(14, QtGui.QFormLayout.LabelRole, self.ontologyLabel)
        
        self.ontologyText = QtGui.QLineEdit(Dialog)
        self.ontologyText.setObjectName("ontologyText")
        self.formLayout.setWidget(14, QtGui.QFormLayout.FieldRole, self.ontologyText)
        
        self.inReplyToLabel = QtGui.QLabel(Dialog)
        self.inReplyToLabel.setObjectName("inReplyToLabel")
        self.formLayout.setWidget(15, QtGui.QFormLayout.LabelRole, self.inReplyToLabel)
        
        self.inReplyToText = QtGui.QLineEdit(Dialog)
        self.inReplyToText.setObjectName("inReplyToText")
        self.formLayout.setWidget(15, QtGui.QFormLayout.FieldRole, self.inReplyToText)
        
        self.replyWithLabel = QtGui.QLabel(Dialog)
        self.replyWithLabel.setObjectName("replyWithLabel")
        self.formLayout.setWidget(16, QtGui.QFormLayout.LabelRole, self.replyWithLabel)
        
        self.replyWithText = QtGui.QLineEdit(Dialog)
        self.replyWithText.setObjectName("replyWithText")
        self.formLayout.setWidget(16, QtGui.QFormLayout.FieldRole, self.replyWithText)
        
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(17, QtGui.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "ACL Message", None, QtGui.QApplication.UnicodeUTF8))
        self.senderLabel.setText(QtGui.QApplication.translate("Dialog", "Sender", None, QtGui.QApplication.UnicodeUTF8))
        self.encodingLabel.setText(QtGui.QApplication.translate("Dialog", "Encoding", None, QtGui.QApplication.UnicodeUTF8))
        self.receiverLabel.setText(QtGui.QApplication.translate("Dialog", "Receiver", None, QtGui.QApplication.UnicodeUTF8))
        self.languageLabel.setText(QtGui.QApplication.translate("Dialog", "Language", None, QtGui.QApplication.UnicodeUTF8))
        self.ontologyLabel.setText(QtGui.QApplication.translate("Dialog", "Ontology", None, QtGui.QApplication.UnicodeUTF8))
        self.inReplyToLabel.setText(QtGui.QApplication.translate("Dialog", "In-reply-to", None, QtGui.QApplication.UnicodeUTF8))
        self.replyWithLabel.setText(QtGui.QApplication.translate("Dialog", "Reply-with", None, QtGui.QApplication.UnicodeUTF8))
        self.communicativeActLabel.setText(QtGui.QApplication.translate("Dialog", "Communicative act", None, QtGui.QApplication.UnicodeUTF8))
        self.contentLabel.setText(QtGui.QApplication.translate("Dialog", "Content", None, QtGui.QApplication.UnicodeUTF8))
        self.protocolLabel.setText(QtGui.QApplication.translate("Dialog", "Protocol", None, QtGui.QApplication.UnicodeUTF8))
        self.protocolComboBox.setItemText(0, QtGui.QApplication.translate("Dialog", "FIPA Contract-Net", None, QtGui.QApplication.UnicodeUTF8))
        self.protocolComboBox.setItemText(1, QtGui.QApplication.translate("Dialog", "FIPA Request", None, QtGui.QApplication.UnicodeUTF8))
        self.conversationIdLabel.setText(QtGui.QApplication.translate("Dialog", "Conversation-ID", None, QtGui.QApplication.UnicodeUTF8))


class ControlACLMessageDialog(QtGui.QDialog):
    def __init__(self):
        super(ControlACLMessageDialog, self).__init__()
        self.ui = ACLMessageDialog()
        self.ui.setupUi(self) 
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    controlAgentsGui = ControlAgentsGui()
    controlAgentsGui.show()
    
    sys.exit(app.exec_())
    