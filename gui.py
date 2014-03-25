# -*- coding: utf-8 -*-
# ***************************************************
# Módulo com interfaces gráficas que têm como objetivo
# facilitar a interação do SMA Python com o usuário
#
# Created: Tue Mar 18 10:31:29 2014
#      by: Lucas S Melo
# ****************************************************

from PySide import QtCore, QtGui
from messages import ACLMessage
from uuid import uuid1
import sys

class ACLMessage_Dialog(QtGui.QWidget):
    '''
        Esta classe cria uma interface gráfica de configuração de 
        uma mensagem do tipo ACLMessage
    '''
    def __init__(self):
        super(ACLMessage_Dialog, self).__init__()
        self.dialog = QtGui.QDialog(self)    
        self.setupUi(self.dialog)
        self.dialog.exec_()
        
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
        
        self.receiverText = QtGui.QLineEdit(Dialog)
        self.receiverText.setObjectName("receiverText")
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.receiverText)
        
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

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    fileDialog = ACLMessage_Dialog()
    sys.exit(app.exec_())
    
    
    
            