import os
from multiprocessing import Process
import json
import urllib2
import httplib as http

def _ip_process_func(app):
    app.start()

class NotebookManager(object):
    def __init__(self):
        self._port = 0
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