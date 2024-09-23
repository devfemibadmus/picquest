import importlib.util
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

wsgi_spec = importlib.util.spec_from_file_location('wsgi', 'tasks/wsgi.py')
wsgi = importlib.util.module_from_spec(wsgi_spec)
wsgi_spec.loader.exec_module(wsgi)

application = wsgi.application
