IPYTHON_NOTEBOOK_HTML="""
<!DOCTYPE HTML>
<html>
<head>
<meta charset="utf-8">
<title>IPython Notebook</title>
<script type='text/javascript' src='static/mathjax/MathJax.js?config=TeX-AMS_HTML' charset='utf-8'></script>
<link rel="stylesheet" href="static/jquery/css/themes/aristo/jquery-wijmo.css" type="text/css" />
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
<meta name="read_only" content="False"/>
</head>
<body
data-project=/ data-notebook-id=@NOTEBOOK_ID@ data-base-project-url=/ data-base-kernel-url=/ >
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

<script src="static/js/loginwidget.js" type="text/javascript" charset="utf-8"></script>
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
<h1>Welcome to Notizblock</h1>
<h3>The IPython Notebook Gtk+ Shell</h3>
<p>To start select one of the available notebooks (right panel); if the list is empty create a new one or open an
existing one from the Notebook menu.<br/>
</p>
<span id='notebook_id' style='dsiplay:none;'></span>
<input id='notebook_name' style='display:none;'/>
</body></html>
"""