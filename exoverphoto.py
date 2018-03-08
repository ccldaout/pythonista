# coding: utf-8

import os
import ui
import dialogs
import photos
from p3 import imgwrap

DOC_ROOT = os.getenv('HOME') + '/Documents'

class Candidate(object):
    
    TOP_EXCL = ['Examples', 'Experiment', 'demo', 'site-packages', 'stash_extensions']
    
    @classmethod
    def dirs(cls):
        topsubdirs = []
        for f in os.listdir('.'):
            if f not in cls.TOP_EXCL:
                if os.path.isdir(f):
                    topsubdirs.append(f)
        yield '.' 
        for d in topsubdirs:
            for dir, _, _ in os.walk(d):
                yield dir

    @classmethod
    def files(cls, dir):
        if dir == '.':
            topsubdirs = []
            for f in os.listdir('.'):
                if f not in cls.TOP_EXCL:
                    if os.path.isdir(f):
                        topsubdirs.append(f)
                    else:
                        yield f
            for d in topsubdirs:
                for f in cls.files(d):
                    yield f
        else:
            for subdir, _, files in os.walk(dir):
                yield subdir
                for f in files:
                    yield subdir + '/' + f

class Command(object):
    
    def __init__(self, topv):
        self._root_dir = '.'
        self._selected_files = []
        
        v = topv['root_dir']
        v.text = '  .'
        self._v_root_dir = v
        
        v = topv['select_dir']
        v.action = self.select_dir
        
        v = topv['add_files']
        v.action = self.add_files
        
        v = topv['selected_files']
        v.editable = False
        self._v_selected_files = v
        
        v = topv['clear_files']
        v.action = self.clear_files
        
        v = topv['save_image']
        v.enabled = False
        v.action = self.save_image
        self._v_save_image = v
        
    def select_dir(self, sender):
        cands = list(Candidate.dirs())
        selected = dialogs.list_dialog('', cands)
        if selected:
            self._root_dir = selected
            self._v_root_dir.text = '  ' + selected
            
    def add_files(self, sender):
        cands = list(Candidate.files(self._root_dir))
        selected = dialogs.list_dialog('', cands, True)
        if selected:
            self._selected_files.extend(selected)
            self._v_selected_files.text += '\n'.join(selected)
            self._v_selected_files.text += '\n'
            self._v_save_image.enabled = True
            
    def clear_files(self, sender):
        self._selected_files = []
        self._v_selected_files.text = ''
        self._v_save_image.enabled = False
        
    def save_image(self, sender):
        png = 'tmp.png'
        img = imgwrap.tar2png(self._selected_files, png)
        photos.create_image_asset(png)
        os.remove(png)


v = ui.load_view()
os.chdir(DOC_ROOT)
Command(v)
v.present('sheet')

