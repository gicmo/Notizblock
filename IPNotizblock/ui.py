#!/usr/bin/env python
license_bsd = \
    '''Copyright (c) 2011, Christian Kellner
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the author nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.'''

__author__ = "Christian Kellner"
__email__ = "kellner@bio.lmu.de"
__copyright__ = " Christian Kellner"
__license__ = "New BSD License"


import sys
import gtk
import webkit
import gio
from html_templates import *
from core import NotebookConnection

class Event(object):
    def __init__(self):
        self._handlers = []

    def __add__(self, other):
        self._handlers.append(other)
        return self

    def __sub__(self, other):
        self._handlers.remove(other)

    def __call__(self, *args, **kwargs):
        for handler in self._handlers:
            handler(*args, **kwargs)


class DashboardModel(gtk.ListStore):
    def __init__(self, nbc):
        gtk.ListStore.__init__(self, str, str)
        self._nbc = nbc

    def update(self):
        nbc = self._nbc
        notebooks = nbc.getNotebooks()

        newnbs = {nb['notebook_id'] : nb['name'] for nb in notebooks}

        old = {}
        iter = self.get_iter_first()
        while iter is not None:
            name = self.get_value(iter, 0)
            nid = self.get_value(iter, 1)
            if not newnbs.has_key(nid):
                self.remove(iter)
            else:
                old[nid] = name
                print name, newnbs[nid]
                if name != newnbs[nid]:
                    self.set_value(iter, 0, newnbs[nid])

            iter = self.iter_next(iter)

        for item in newnbs.iterkeys():
            if not old.has_key(item):
                self.append([newnbs[item], item])
        


class DashboardView(gtk.TreeView):
    def __init__(self, model=None):
        gtk.TreeView.__init__(self)

        self._osc_cb = None

        name = gtk.TreeViewColumn('Notebooks')
        self.append_column (name)
        cell = gtk.CellRendererText()
        name.pack_start(cell, True)
        name.add_attribute(cell, 'text', 0)
        self.set_search_column(0)
        name.set_sort_column_id(0)

        if model:
            self.set_model(model)

        selection = self.get_selection()
        selection.set_mode(gtk.SELECTION_BROWSE)
        selection.connect("changed", self._on_selection_change)
        selection.unselect_all()

    def unselect_all(self):
        selection = self.get_selection()
        selection.unselect_all()

    def select(self, nid):
        model = self.get_model()
        iter = model.get_iter_first()
        while iter is not None:
            cur_id = model.get_value(iter, 1)
            if nid == cur_id:
                break
            iter = model.iter_next(iter)

        if iter is not None:
            selection = self.get_selection()
            selection.select_iter(iter)

    # selection change handling
    def _on_selection_change(self, tree_selection):
        (model, tree_iter) = tree_selection.get_selected()
        if tree_iter:
            nid =  model.get_value(tree_iter, 1)
        else:
            nid = None
        self.on_selection_change(nid)
    
    on_selection_change = Event()


class Notebook(webkit.WebView):

    def __init__(self, nbc):
        webkit.WebView.__init__(self)
        self.set_full_content_zoom(True)
        self._id = None
        self.load_string(ABOUT_PAGE, "text/html", "iso-8859-15", "about")
        self._nbc = nbc
        self.connect("notify::load-status", self._load_status_changed)

    def _load_status_changed(self, *args, **kwargs):
        status = self.get_load_status()
        if status == webkit.LOAD_FINISHED:
            self.execute_script("document.title=$('span#notebook_id').text();")
            self._id = self.get_main_frame().get_title()
            self.execute_script("document.title=$('input#notebook_name').attr('value');")
            self._name = self.get_main_frame().get_title()

            self.on_load_finished()

    on_load_finished = Event()

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    # Notebook methods
    def load(self, notebookdId):
        if self._id == notebookdId:
            return

        self._id = notebookdId

        if not notebookdId:
            self.load_string(ABOUT_PAGE, "text/html", "iso-8859-15", "about")
            return

        html = IPYTHON_NOTEBOOK_HTML.replace("@NOTEBOOK_ID@", self._id)
        self.load_html_string(html, base_uri=self._nbc.baseUrl)

    def save(self):
        script = "IPython.save_widget.set_notebook_name('%s');" % self.name
        self.execute_script(script)
        script = "IPython.notebook.save_notebook('%s');" % self.name
        self.execute_script(script)

    # Cell methods
    def cell_delete(self):
        self.execute_script("IPython.notebook.delete_cell();")

    def cell_insert_above(self):
        self.execute_script("IPython.notebook.insert_code_cell_above();")

    def cell_insert_below(self):
        self.execute_script("IPython.notebook.insert_code_cell_below();")

    def cell_move_up(self):
        self.execute_script("IPython.notebook.move_cell_up(0);")

    def cell_move_down(self):
        self.execute_script("IPython.notebook.move_cell_down(0);")

    def cell_2_code(self):
        self.execute_script("IPython.notebook.to_code();")

    def cell_2_markdown(self):
        self.execute_script("IPython.notebook.to_markdown();")

    def cell_toggle_linenumbers(self):
        self.execute_script("IPython.notebook.cell_toggle_line_numbers();")

    def cell_set_code(self, code):
        script = "IPython.notebook.selected_cell().set_code('%s')" % code
        self.execute_script(script)

    def execute(self, all_cells=False):
        if not all_cells:
            self.execute_script("IPython.notebook.execute_selected_cell();")
        else:
            self.execute_script("IPython.notebook.execute_all_cells();")

    def show_keyboard_shortcuts(self):
        self.execute_script("IPython.notebook.toggle_keyboard_shortcuts();")
        


def UIAction(name, tooltip=None, stock_id=None, label=None, accelerator=""):
    args = locals()
    def decorator(func):
        func.ui_action = args
        return func
    return decorator

class ShellWindow(gtk.Window):

    ui_info = '''<ui>
      <menubar name='MenuBar'>
        <menu name='NotebookMenu' action='NotebookMenu'>
          <menuitem action='Rename'/>
          <menuitem action='NewNB'/>
          <menuitem action='FileOpen'/>
          <menuitem name='Save' action='Save' />
          <menuitem action='Download' />
          <menuitem action='DeleteNB'/>
          <separator/>
          <menuitem action='Quit'/>
        </menu>
        <menu action='CellMenu'>
          <menuitem action='CellDelete'/>
          <separator/>
          <menuitem action='CellInsAbove'/>
          <menuitem action='CellInsBelow'/>
          <separator/>
          <menuitem action='Cell2Code'/>
          <menuitem action='Cell2Markdown'/>
          <separator/>
          <menuitem action='CellMoveUp'/>
          <menuitem action='CellMoveDown'/>
          <separator/>
          <menuitem action='CellToggleLN'/>
        </menu>
        <menu action='ExecuteMenu'>
          <menuitem action='ExecuteCell'/>
          <menuitem action='ExecuteAll'/>
        </menu>
        <menu action='HelpMenu'>
          <menuitem action='HelpPython'/>
          <menuitem action='HelpNumPy'/>
          <menuitem action='HelpSciPy'/>
          <menuitem action='HelpMPL'/>
          <menuitem action='HelpSymPy'/>
          <separator/>
          <menuitem action='HelpShortcuts'/>
          <separator/>
          <menuitem action='About'/>
        </menu>
      </menubar>
      <toolbar name='ToolBar'>
        <toolitem name='Save' action='Save' />
        <toolitem name='New' action='NewNB' />
        <separator/>
        <toolitem name='Open' action='FileOpen' />
        <toolitem name='Save to disk' action='Download' />
        <separator/>
      </toolbar> </ui>'''

    @property
    def ui_actions(self):
        actions = [
          ( "NotebookMenu", None, "_Notebook" ),
          ( "CellMenu",     None, "_Cell" ),
          ( "ExecuteMenu",  None, "_Execute"),
          ( "HelpMenu",     None, "_Help" ),

          ( "VisitHP", None,
            "Visit Homepage", "",
            "Go to the Notizblock Homepage",
            self.activate_action ),

          ]

        for (key, val) in self.__class__.__dict__.iteritems():
            if hasattr(val, "ui_action"):
                a = val.ui_action
                action = (a['name'], a['stock_id'], a['label'],
                          a['accelerator'], a['tooltip'], getattr(self, key))
                actions.append(action)

        return actions


    def __init__(self):
        gtk.Window.__init__(self)

        nbc = NotebookConnection()

        nbc.start_service() # This will actually start the ipython session
        
        model = DashboardModel(nbc)
        view = DashboardView (model)
        notebook = Notebook(nbc)

        hpane = gtk.HPaned()
        hpane.add1 (view)
        hpane.add2 (notebook)

        ui_manager = gtk.UIManager()
        accel_group = ui_manager.get_accel_group()
        self.add_accel_group(accel_group)
        action_group = gtk.ActionGroup('ShellActions')

        action_group.add_actions(self.ui_actions)
        ui_manager.insert_action_group(action_group, 0)
        ui_manager.add_ui_from_string(self.ui_info)

        menubar = ui_manager.get_widget("/MenuBar")
        toolbar = ui_manager.get_widget("/ToolBar")
        toolbar.set_tooltips(True)

        # main table
        table = gtk.Table(1, 4, False)
        table.attach(menubar,
                     # X direction #          # Y direction
                     0, 1,                      0, 1,
                     gtk.EXPAND | gtk.FILL,     0,
                     0,                         0)


        table.attach(toolbar,
                     # X direction #       # Y direction
                     0, 1,                   1, 2,
                     gtk.EXPAND | gtk.FILL,  0,
                     0,                      0)

        table.attach (hpane,
                      # X direction           Y direction
                      0, 1,                   3, 4,
                      gtk.EXPAND | gtk.FILL,  gtk.EXPAND | gtk.FILL,
                      0,                      0)

        # window setup
        self.set_title('Notizblock - IPython Notebook Shell')
        self.connect('destroy', self.destroy_cb)
        self.set_default_size(1100, 600)
        self.add(table)

        self._view = view
        self._nb_handle = notebook
        self._model = model
        self._nbc = nbc

        self.show_all()
        view.unselect_all()
        notebook.grab_focus()
        view.on_selection_change += self.select_notebook
        notebook.on_load_finished += self.on_notebook_loaded

    @property
    def notebook(self):
        return self._nb_handle

    @property
    def remote_teaching_uri(self):
        return 'dav://localhost/teaching/'

    def visit_uri(self, uri, timestamp=None):
        if not timestamp:
            timestamp = gtk.get_current_event_time()
        gtk.show_uri(self.get_screen(), uri, timestamp)

    def on_notebook_loaded(self):
        self._model.update()
        print "Notebook loaded (%s, %s)" % (self.notebook.name, self.notebook.id)

    def select_notebook(self, notebookId):
        self.notebook.load(notebookId)

    # Action implementation
    def activate_action(self, action):
        print action

    @UIAction('NewNB', label='_New', stock_id=gtk.STOCK_NEW, accelerator='<control>N', tooltip='Create a new Notebook')
    def notebook_new(self, action):
        nbc = self._nbc
        newId = nbc.new_notebook()
        self._model.update()
        self.notebook.load(newId)
        self._view.select(newId)


    @UIAction('DeleteNB', label='_Delete', stock_id=gtk.STOCK_NEW, tooltip="Delete the notebook")
    def notebook_delete(self, action):
        nbc = self._nbc
        nid = self.notebook.id
        self.notebook.load(None)
        self.notebook.grab_focus()
        self._view.unselect_all()
        nbc.delete_notebook(nid)
        self._model.update()

    @UIAction('Download', label='Save to disk...', stock_id=gtk.STOCK_SAVE, tooltip='Download the current notebook')
    def notebook_download(self, action):
        chooser = gtk.FileChooserDialog(title="Save Notebook",
                                        action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        parent=self,
                                        buttons=(gtk.STOCK_SAVE, gtk.RESPONSE_OK,
                                                 gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        file_filter = gtk.FileFilter()
        file_filter.set_name("IPython Notebook (JSON)")
        file_filter.add_pattern("*.ipynb")
        chooser.add_filter(file_filter)
        
        chooser.set_current_name(self.notebook.name + '.ipynb')
        chooser.do_overwrite_confirmation = True
        
        chooser.connect("response", self.notebook_save_response)
        chooser.show()

    def notebook_save_response(self, chooser, response_id):
        if response_id != gtk.RESPONSE_OK:
            chooser.destroy()
            return

        nbc = self._nbc
        nid = self.notebook.id
        uri = chooser.get_uri()
        if not uri.lower().endswith('.ipynb'):
            uri += '.ipynb'
        nbc.download_notebook(nid, uri)
        chooser.destroy()

    @UIAction('FileOpen', label='_Open...', stock_id=gtk.STOCK_OPEN, tooltip='Open a notebook')
    def notebook_open(self, action):
        chooser = gtk.FileChooserDialog(title="Open Notebook",
                                        parent=self,
                                        buttons=(gtk.STOCK_OPEN, gtk.RESPONSE_OK,
                                                 gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        chooser.add_shortcut_folder_uri(self.remote_teaching_uri)
        chooser.connect("response", self.notebook_open_response)
        chooser.show()

    def notebook_open_response(self, chooser, response_id):
        if response_id != gtk.RESPONSE_OK:
            chooser.destroy()
            return

        uri = chooser.get_uri()
        newId = self._nbc.upload_notebook(uri)
        self._model.update()
        self.notebook.load(newId)
        self._view.select(newId)

        chooser.destroy()

    @UIAction('Save', label='_Save', stock_id=gtk.STOCK_SAVE, tooltip='Save the current notebook')
    def notebook_save(self, action):
        self.notebook.save()

    @UIAction("Rename", label='_Rename...', tooltip='Rename the notebook')
    def notebook_rename(self, action):
        dialog = gtk.Dialog(title="Rename Notebook",
                            parent=self,
                            flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                                     gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        
        entry = gtk.Entry(max=20)
        entry.set_text (self.notebook.name)

        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("New name:"))
        hbox.pack_start(entry)

        dialog.vbox.pack_start(hbox)

        dialog.connect("response", self.notebook_rename_response, entry)
        dialog.show_all()

    def notebook_rename_response(self, dialog, response_id, entry):
        if response_id != gtk.RESPONSE_ACCEPT:
            dialog.destroy()
            return
        print entry.get_text()
        self.notebook.name = entry.get_text()
        self.notebook.save()
        # self._model.update()
        # model.update() seems racy.
        selection = self._view.get_selection()
        model, tree_iter = selection.get_selected()
        model.set_value(tree_iter, 0, self.notebook.name);

        dialog.destroy()

    @UIAction('CellDelete', label='Delete cell', tooltip='Delete the current cell')
    def cell_delete(self, action):
        self.notebook.cell_delete()

    @UIAction('CellInsAbove', label='Insert above', tooltip='Insert a code cell above')
    def cell_insert_above(self, action):
        self.notebook.cell_insert_above()

    @UIAction('CellInsBelow', label='Insert below', tooltip='Insert a code cell below')
    def cell_insert_below(self, action):
        self.notebook.cell_insert_below()

    @UIAction('Cell2Code', label='Format as Code', tooltip='Format cell as code block')
    def cell_to_code(self, action):
        self.notebook.cell_2_code()

    @UIAction('Cell2Markdown', label='Format as Markdown', tooltip='Format cell as markdown block')
    def cell_to_markdown(self, action):
        self.notebook.cell_2_markdown()

    @UIAction('CellMoveUp', label='Move up', tooltip='Move the current cell up')
    def cell_move_up(self, action):
        self.notebook.cell_move_up()

    @UIAction('CellMoveDown', label='Move down', tooltip='Move the current cell down')
    def cell_move_down(self, action):
        self.notebook.cell_move_down()

    @UIAction('CellToggleLN', label='Toggle Line-numbers', tooltip='Toogle line numbering')
    def cell_toggle_linenumbers(self, action):
        self.notebook.cell_toggle_linenumbers()

    @UIAction('ExecuteAll', label='All cells', tooltip='Execute all cells')
    def execute_all(self, action):
        self.notebook.execute(all_cells=True)

    @UIAction('ExecuteCell', label='Selected cell', tooltip='Execute the selected cell')
    def execute_cell(self, action):
        self.notebook.execute()

    @UIAction('HelpShortcuts', label='Keyboard Shortcuts', tooltip='Display the available keyboard shortcuts')
    def help_shortcuts(self, action):
        self.notebook.show_keyboard_shortcuts()

    @UIAction('About', label='_About', stock_id=gtk.STOCK_ABOUT, tooltip='About')
    def show_about(self, action):
        #logo = self.render_icon("notizblock-logo", gtk.ICON_SIZE_DIALOG)
        
        dialog = gtk.AboutDialog()
        dialog.set_name("Notizblock")
        dialog.set_copyright("\302\251 Copyright 2011 Chrisitan Kellner")
        dialog.set_authors(["Christian Kellner <kellner@bio.lmu.de>"])
        dialog.set_website("http://www.g-node.org") # FIXME
        dialog.set_license (license_bsd)
        #dialog.set_logo(logo)

        dialog.set_transient_for(self)

        dialog.connect ("response", lambda d, r: d.destroy())
        dialog.show()

    @UIAction('Quit', label='_Quit', stock_id=gtk.STOCK_QUIT, accelerator='<control>Q', tooltip='Quit the application')
    def destroy_cb(self, arg):
        self._nbc.stop_service()
        gtk.main_quit()

    @UIAction('HelpPython', label='Python')
    def on_help_python(self, action):
        self.visit_uri('http://docs.python.org/')

    @UIAction('HelpNumPy', label='NumPy')
    def on_help_numpu(self, action):
        self.visit_uri('http://docs.scipy.org/doc/numpy/reference/')

    @UIAction('HelpSciPy', label='SciPy')
    def on_help_scipy(self, action):
        self.visit_uri('http://docs.scipy.org/doc/scipy/reference/')

    @UIAction('HelpMPL', label='matplotlib')
    def on_help_matplotlib(self, action):
        self.visit_uri('http://matplotlib.sourceforge.net/')

    @UIAction('HelpSymPy', label='SymPy')
    def on_help_sympy(self, action):
        self.visit_uri('http://docs.sympy.org')

def main(argv):
    try:
        from ctypes import cdll
        libc = cdll.LoadLibrary("libc.so.6")
        #define PR_SET_NAME 15
        libc.prctl (15, 'Notizblock', 0, 0, 0)
    except:
        pass

    wnd = ShellWindow()
    gtk.main()

if __name__ == '__main__':
    res = main(sys.argv[1:])
    sys.exit(res)


