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

import json
import urllib2
import httplib as http
import sys
import gtk
import webkit
import gio
import os
from multiprocessing import Process

IPYTHON_NOTEBOOK_HTML="""
<!DOCTYPE HTML>
<html>
<head>
<meta charset="utf-8">
<title>IPython Notebook</title>
<link rel="stylesheet" href="static/jquery/css/themes/aristo/jquery-wijmo.css" type="text/css" />
<!-- <link rel="stylesheet" href="static/jquery/css/themes/rocket/jquery-wijmo.css" type="text/css" /> -->
<!-- <link rel="stylesheet" href="static/jquery/css/themes/smoothness/jquery-ui-1.8.14.custom.css" type="text/css" />-->
<!-- <script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML" charset="utf-8"></script> -->
<script type='text/javascript' src='static/mathjax/MathJax.js?config=TeX-AMS_HTML' charset='utf-8'></script>
<script type="text/javascript">
function CheckMathJax(){
var div=document.getElementById("MathJaxFetchingWarning")
if(window.MathJax){
document.body.removeChild(div)
}
else{
div.style.display = "block";
}
}
if (typeof MathJax == 'undefined') {
console.log("No local MathJax, loading from CDN");
document.write(unescape("%3Cscript type='text/javascript' src='http://cdn.mathjax.org/mathjax/latest/MathJax.js%3Fconfig=TeX-AMS_HTML' charset='utf-8'%3E%3C/script%3E"));
}else{
console.log("Using local MathJax");
}
</script>
<link rel="stylesheet" href="static/codemirror/lib/codemirror.css">
<link rel="stylesheet" href="static/codemirror/mode/markdown/markdown.css">
<link rel="stylesheet" href="static/codemirror/mode/rst/rst.css">
<link rel="stylesheet" href="static/codemirror/theme/ipython.css">
<link rel="stylesheet" href="static/codemirror/theme/default.css">
<link rel="stylesheet" href="static/prettify/prettify.css"/>
<link rel="stylesheet" href="static/css/boilerplate.css" type="text/css" />
<link rel="stylesheet" href="static/css/layout.css" type="text/css" />
<link rel="stylesheet" href="static/css/base.css" type="text/css" />
<link rel="stylesheet" href="static/css/notebook.css" type="text/css" />
<link rel="stylesheet" href="static/css/renderedhtml.css" type="text/css" />
</head>
<body onload='CheckMathJax();' data-project=/home/gicmo data-notebook-id=@NOTEBOOK_ID@ data-base-project-url=/ data-base-kernel-url=/>
<div id="header" style="display: none; height: 0px;">
<span id="save_widget" style="display: none;">
<input type="text" id="notebook_name" size="20" style="display: none;"></textarea>
<span id="notebook_id" style="display:none">@NOTEBOOK_ID@</span>
<button style="display: none; id="save_notebook"><u>S</u>ave</button>
</span>
<span id="kernel_status" style="display: none;">Idle</span>
</div>
<div id="MathJaxFetchingWarning"
style="width:80%; margin:auto;padding-top:20%;text-align: justify; display:none">
<p style="font-size:26px;">There was an issue trying to fetch MathJax.js
from the internet.</p>
<p style="padding:0.2em"> With a working internet connection, you can run
the following at a Python or IPython prompt, which will install a local
copy of MathJax:</p>
<pre style="background-color:lightblue;border:thin silver solid;padding:0.4em">
from IPython.external import mathjax; mathjax.install_mathjax()
</pre>
This will try to install MathJax into the directory where you installed
IPython. If you installed IPython to a location that requires
administrative privileges to write, you will need to make this call as
an administrator. On OSX/Linux/Unix, this can be done at the
command-line via:
<pre style="background-color:lightblue;border:thin silver solid;padding:0.4em">
sudo python -c "from IPython.external import mathjax; mathjax.install_mathjax()"
</pre>
</p>
</div>
<div id="main_app">

<div id="left_panel_splitter" style="display:none"></div>
<div id="notebook_panel">
<div id="notebook"></div>
<div id="pager_splitter"></div>
<div id="pager"></div>
</div>
</div>
<script src="static/jquery/js/jquery-1.6.2.min.js" type="text/javascript" charset="utf-8"></script>
<script src="static/jquery/js/jquery-ui-1.8.14.custom.min.js" type="text/javascript" charset="utf-8"></script>
<script src="static/jquery/js/jquery.autogrow.js" type="text/javascript" charset="utf-8"></script>
<script src="static/codemirror/lib/codemirror.js" charset="utf-8"></script>
<script src="static/codemirror/mode/python/python.js" charset="utf-8"></script>

<script src="static/codemirror/mode/htmlmixed/htmlmixed.js" charset="utf-8"></script>
<script src="static/codemirror/mode/xml/xml.js" charset="utf-8"></script>
<script src="static/codemirror/mode/javascript/javascript.js" charset="utf-8"></script>
<script src="static/codemirror/mode/css/css.js" charset="utf-8"></script>
<script src="static/codemirror/mode/rst/rst.js" charset="utf-8"></script>
<script src="static/codemirror/mode/markdown/markdown.js" charset="utf-8"></script>
<script src="static/pagedown/Markdown.Converter.js" charset="utf-8"></script>
<script src="static/prettify/prettify.js" charset="utf-8"></script>
<script src="static/js/namespace.js" type="text/javascript" charset="utf-8"></script>

<script src="static/js/utils.js" type="text/javascript" charset="utf-8"></script>
<script src="static/js/cell.js" type="text/javascript" charset="utf-8"></script>
<script src="static/js/codecell.js" type="text/javascript" charset="utf-8"></script>
<script src="static/js/textcell.js" type="text/javascript" charset="utf-8"></script>
<script src="static/js/kernel.js" type="text/javascript" charset="utf-8"></script>
<script src="static/js/kernelstatus.js" type="text/javascript" charset="utf-8"></script>
<script src="static/js/layout.js" type="text/javascript" charset="utf-8"></script>
<script src="static/js/savewidget.js" type="text/javascript" charset="utf-8"></script>
<script src="static/js/quickhelp.js" type="text/javascript" charset="utf-8"></script>

<script src="static/js/pager.js" type="text/javascript" charset="utf-8"></script>
<script src="static/js/panelsection.js" type="text/javascript" charset="utf-8"></script>
<script src="static/js/printwidget.js" type="text/javascript" charset="utf-8"></script>
<script src="static/js/leftpanel.js" type="text/javascript" charset="utf-8"></script>
<script src="static/js/notebook.js" type="text/javascript" charset="utf-8"></script>
<script src="static/js/notebookmain.js" type="text/javascript" charset="utf-8"></script>
</body>
</html>
"""


ABOUT_PAGE = """
<html><head><title>IPython Notebook Gtk Shell</title></head><body>
<h1>Welcome to Lecture Title Excercise Class</h1>
<p>This is a cool intro Text that we need to come up with ...<br/>
</p>
<span id='notebook_id' style='dsiplay:none;'></span>
<input id='notebook_name' style='display:none;'/>
</body></html>
"""

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

def _ip_process_func(app):
    app.start()

class NotebookConnection(object):
    def __init__(self, port=8888):
        self._port = port
        self._host = '127.0.0.1'
        self._ip_process = None
        
    def getNotebooks(self):
        try:
            url = self.baseUrl + "notebooks"
            response = urllib2.urlopen (url)
            notebooks = json.load(response)
            return notebooks
        except:
            return None

    def new_notebook(self):
        con = http.HTTPConnection(self.host_port) #FIXME
        con.request('GET', '/new', "")
        resp = con.getresponse()
        data = resp.read()
        dni_start = data.index('data-notebook-id')
        eqsng = data.index('=', dni_start)
        id_end = data.index('\n', eqsng+1)
        return data[eqsng+1:id_end]

    def delete_notebook(self, notebookdId):
        path = '/notebooks/%s' % notebookdId
        con = http.HTTPConnection(self.host_port)
        con.request('DELETE', path, "")
        resp = con.getresponse()

    def download_notebook(self, nid, uri):
        nb_file, name, format = self.get_file_and_format_from_uri(uri)
        path = '/notebooks/%s?format=%s' % (nid, format)
        con = http.HTTPConnection(self.host_port)
        con.request('GET', path, "")
        resp = con.getresponse()
        data = resp.read()
        nb_file.replace_contents(data)

    def upload_notebook(self, uri, name=None):
        nb_file, name, format = self.get_file_and_format_from_uri(uri, name=name)
        data, nsize, etag = nb_file.load_contents()
        path = '/notebooks?name=%s&format=%s' % (name, format)
        con = http.HTTPConnection(self.host_port)
        con.request('POST', path, data)
        resp = con.getresponse()
        nid = resp.read()
        nid = nid.replace('"', ' ')
        nid = nid.strip(' ')
        return nid

    def get_file_and_format_from_uri(self, uri, name=None):
        nb_file = gio.File(uri)
        filename = nb_file.get_basename()
        fname, ext = os.path.splitext (filename)
        if not name:
            name = fname
        format = self.formatFromExt(ext)
        return nb_file, name, format

    @property
    def host_port(self):
        return '%s:%d' % (self._host, self._port)

    @property
    def baseUrl(self):
        return "http://%s/" % self.host_port

    def formatFromExt(self, ext):
        ext = ext.strip('.')
        ext_map = {'ipynb' : 'json',
                   'py'    : 'py'} # FIXME not sure about py -> py
        if not ext_map.has_key(ext):
            return None            # FIXME exception

        return ext_map[ext]

    def start_service(self):
        from IPython.frontend.html.notebook.notebookapp import NotebookApp
        app = NotebookApp()
        notebook_path = os.path.expanduser('~/.notizblock')
        if not os.path.exists(notebook_path):
            os.mkdir(notebook_path)
        nbdir = '--notebook-dir=%s' % notebook_path
        nb_argv = ['notebook', '--pylab=inline', '--no-browser', '--parent=True', nbdir]
        app.initialize(argv=nb_argv)
        self._host = app.ip
        self._port = app.port
        ip_process = Process(target=_ip_process_func, args=(app,))
        self._ip_process = ip_process
        ip_process.start()

    def stop_service(self):
        if not self._ip_process:
            return
        self._ip_process.terminate()


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
          <menuitem action='HelpShortcuts'/>
          <menuitem action='VisitHP'/>
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
          ( "FileOpen", gtk.STOCK_OPEN,
            "_Open...", None,
            "Open a File",
            self.notebook_open ),
          ( "Save", gtk.STOCK_SAVE,
            "_Save", None,
            "Save the current notebook",
            self.notebook_save ),
          ( "Download", gtk.STOCK_HARDDISK,
            "Save to disk...", None,
            "Download the current notebook",
            self.notebook_download ),
          ( "DeleteNB", gtk.STOCK_NEW,
            "_Delete", "",
            "Delete the notebook",
            self.notebook_delete ),
          ( "Quit", gtk.STOCK_QUIT,
            "_Quit", "<control>Q",
            "Quit",
            self.destroy_cb ),
          ( "HelpShortcuts", None,
            "Keyboard Shortcuts", "",
            "Display the keyboard shortcuts",
            self.help_shortcuts ),
          ( "About", None,
            "_About", "",
            "About",
            self.show_about ),
          ( "VisitHP", None,
            "Visit Homepage", "",
            "Go to the Notizblock Homepage",
            self.activate_action ),
           ( "CellDelete", None,
            "Delete Cell", "",
            "Delete the currently selected cell",
            self.cell_delete ),
          ( "CellInsAbove", None,
            "Insert above", "",
            "Insert a code cell above",
            self.cell_insert_above ),
          ( "CellInsBelow", None,
            "Insert below", "",
            "Insert a code cell below",
            self.cell_insert_below ),
          ( "Cell2Code", None,
            "Format as Code", "",
            "Format cell as code block",
            self.cell_to_code ),
          ( "Cell2Markdown", None,
            "Format as Markdown", "",
            "Format cell as markdown block",
            self.cell_to_markdown ),
          ( "CellMoveUp", None,
            "Move up", "",
            "Move cell up",
            self.cell_move_up ),
          ( "CellMoveDown", None,
            "Move down", "",
            "Move cell down",
            self.cell_move_down ),
          ( "CellToggleLN", None,
            "Toggle Linenumbers", "",
            "Toggle the line numbers",
            self.cell_toggle_linenumbers ),
          ( "ExecuteCell", None,
            "Selected cell", "",
            "Execute the currenlty selected cell",
            self.execute_cell ),
          ( "ExecuteAll", None,
            "All cells", "",
            "Execute all cells",
            self.execute_all ),
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
        self.set_title('IPython Notebook Shell')
        self.connect('destroy', self.destroy_cb)
        self.set_default_size(800, 600)
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

    def notebook_delete(self, action):
        nbc = self._nbc
        nid = self.notebook.id
        self.notebook.load(None)
        self.notebook.grab_focus()
        self._view.unselect_all()
        nbc.delete_notebook(nid)
        self._model.update()

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

    def notebook_open(self, action):
        chooser = gtk.FileChooserDialog(title="Open Notebook",
                                        parent=self,
                                        buttons=(gtk.STOCK_OPEN, gtk.RESPONSE_OK,
                                                 gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        chooser.connect("response", self.notebook_open_response)
        chooser.show()

    def notebook_open_response(self, chooser, response_id):
        if response_id != gtk.RESPONSE_OK:
            chooser.destroy()
            return

        uri = chooser.get_uri()
        print uri
        newId = self._nbc.upload_notebook(uri)
        self._model.update()
        self.notebook.load(newId)
        self._view.select(newId)

        chooser.destroy()

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
        
    def cell_delete(self, action):
        self.notebook.cell_delete()

    def cell_insert_above(self, action):
        self.notebook.cell_insert_above()

    def cell_insert_below(self, action):
        self.notebook.cell_insert_below()

    def cell_to_code(self, action):
        self.notebook.cell_2_code()

    def cell_to_markdown(self, action):
        self.notebook.cell_2_markdown()

    def cell_move_up(self, action):
        self.notebook.cell_move_up()
        
    def cell_move_down(self, action):
        self.notebook.cell_move_down()

    def cell_toggle_linenumbers(self, action):
        self.notebook.cell_toggle_linenumbers()

    def execute_all(self, action):
        self.notebook.execute(all_cells=True)

    def execute_cell(self, action):
        self.notebook.execute()

    def help_shortcuts(self, action):
        self.notebook.show_keyboard_shortcuts()

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

    def destroy_cb(self, arg):
        self._nbc.stop_service()
        gtk.main_quit()


def main(argv):
    try:
        from ctypes import cdll
        libc = cdll.LoadLibrary("libc.so.6")
        libc.prctl (15, 'IPython Shell', 0, 0, 0)
    except:
        pass

    wnd = ShellWindow()
    gtk.main()

if __name__ == '__main__':
    res = main(sys.argv[1:])
    sys.exit(res)


