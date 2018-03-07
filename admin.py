# coding: utf-8

import binascii
import functools
import ui
import glob
import dialogs
import os

from p3.mdialog import MessageDialog
from p3.utils import Config
from tpp import uipc

CONFIG_PATH = '.admin.config'
config = Config.load(CONFIG_PATH)

PY_DIR = '../esp32/upy/'

def exc_false(f):
    @functools.wraps(f)
    def _f(*args, **kwargs):
        try:
            f(*args, **kwargs)
            return True
        except Exception as e:
            print f.__name__, 'failure:', str(e)
            return False
    return _f

class AdminCommand(object):

    def __init__(self):
        self.cli = None
        self.on_close = None

    @exc_false
    def start(self, ip_address):
        print ip_address
        self.cli = uipc.client((ip_address, 2000))

    @exc_false
    def stop(self):
        self.cli.close()
        if self.on_close:
            self.on_cloase()

    @exc_false
    def put(self, path):
        with open(PY_DIR+path, 'rb') as f:
            self.cli.put_beg(path)
            while True:
                data = f.read(2048)
                if not data:
                    break
                data = binascii.hexlify(data)
                self.cli.put_data(data)
            return self.cli.put_end()

    @exc_false
    def mkdir(self, path):
        self.cli.mkdir(path)
        
    @exc_false
    def service(self, modname, port):
        self.cli.service(modname, port)

    @exc_false
    def reset(self):
        self.cli.reset()
        self.stop()

def list_uploadable():
    n = len(PY_DIR)
    for f in glob.glob(PY_DIR+'*.py') + glob.glob(PY_DIR+'*/*.py'):
        yield f[n:]

class Admin(object):

    def __init__(self, topv, mdiag, admcmd):
        self._admcmd = admcmd
        self._mdiag = mdiag

        topv.background_color = '#2f2f2f'

        v = topv['ip_address']
        v.action = self.enter_ipaddress
        if config.ip_address:
            v.text = config.ip_address

        v = topv['connect']
        v.action = self.do_connect
        
        v = topv['service']
        v.action = self.do_service

        v = topv['upload']
        v.action = self.do_upload

        v = topv['clear_selection']
        v.action = self.do_clear_selection

        v = topv['reset']
        v.action = self.do_reset

        self.v_status = topv['ipc_status']

        v = topv['file_selection']
        v.data_source = ui.ListDataSource(list_uploadable())
        v.allows_multiple_selection = True
        self.v_fileselection = v

    def ipc_ready(self, status):
        if status:
            self.v_status.text = 'Ready'
            self.v_status.background_color = '#00f816'
        else:
            self.v_status.text = 'Not Ready'
            self.v_status.background_color = '#aeaeae'

    def enter_ipaddress(self, sender):
        config.ip_address = sender.text
        config.save()

    def do_connect(self, sender):
        self._admcmd.start(config.ip_address)
        self.ipc_ready(True)

    def do_clear_selection(self, sender):
        v = ui.TextView()

        self.v_fileselection.reload()
        
    def do_service(self, sender):
        #cands = [os.path.basename(f)[:-3] for f in glob.glob(PY_DIR+'service/*.py')]
        #cands.remove('__init__')
        #cands.remove('admin')
        #mod = dialogs.list_dialog('services', cands)
        self._admcmd.service('robot1', 2001)

    def do_upload(self, sender):
        self._mdiag.open()
        files = self.v_fileselection.data_source.items
        for _, row in self.v_fileselection.selected_rows:
            path = files[row]
            ret = self._admcmd.put(path)
            self._mdiag.put('%s ... %s\n' % (path, ('NG', 'OK')[bool(ret)]))
        self.v_fileselection.reload()

    def do_reset(self, sender):
        self._admcmd.reset()
        self.ipc_ready(False)

mainview = ui.load_view()
Admin(mainview, MessageDialog(), AdminCommand())
mainview.present('sheet')

