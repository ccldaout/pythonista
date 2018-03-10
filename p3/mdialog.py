# coding: utf-8

import ui
from p3.utils import self_pyui

class MessageDialog(object):
    def __init__(self):
        self.view = ui.load_view(self_pyui(__name__))
        self.textview = self.view['message_view']
        self.ok_button = self.view['ok_button']
        self.ok_button.action = self.close

    def open(self):
        self.textview.text = ''
        self.view.present('popover')

    def close(self, sender=None):
        self.view.close()

    def put(self, message):
        self.textview.text += message

