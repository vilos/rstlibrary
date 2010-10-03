"""
package for restructured text customizations
"""
import os
from docutils import io, nodes
from docutils.core import publish_programmatically, publish_from_doctree, publish_parts
from docutils.utils import Reporter
from writer import HTMLWriter, TextWriter, TransformingWriter, is_hidden_section

    
class WarningStream(object):
    
    def __init__(self):
        self.content = []
        
    def write(self, msg):
        start = '<string>:'
        if msg.startswith(start):
            msg = msg[len(start):]
        self.content.append(msg)
        
    def getvalue(self):
        return ''.join(self.content)
    
    def max_level(self):
        res = 0
        for msg in self.content:
            for level in Reporter.levels:
                if level in msg:
                    res = max(Reporter.levels.index(level), res)
        return res 
    
def publish2doc(source):
    stream =  WarningStream()
    settings_overrides = dict(warning_stream=stream, report_level=Reporter.INFO_LEVEL)
    output, pub = publish_programmatically(source_class=io.StringInput, source=source, source_path=None,
                             destination_class=io.NullOutput, destination=None, destination_path=None,
                             reader=None, reader_name='standalone',
                             parser=None, parser_name='restructuredtext',
                             #writer=TransformingWriter(), writer_name=None,
                             writer=None, writer_name='null',
                             settings=None, settings_spec=None,
                             settings_overrides=settings_overrides, config_section=None,
                             enable_exit_status=None)
    # bind the stream to be pickled as well
    pub.document.stream = stream
    return pub.document

def publish(doctree, template = 'template.txt'):
    output_settings = dict(output_encoding='unicode',
                           template=os.path.join(os.path.dirname(__file__), template))
    contents = publish_from_doctree(
            doctree,
            writer = HTMLWriter(),
            settings_overrides=output_settings
            )
    return contents

def extract(doctree):
    return publish_from_doctree(
            doctree,
            writer = TextWriter(),
            )

def publish_source(source):
    return publish_parts(source, 
                         writer_name="html")['html_body']
#package

# monkey patch docutils for correct poemline

class poemline(nodes.Part, nodes.TextElement):
    pass

class poem(nodes.General, nodes.Element):
    pass

class stanza(nodes.General, nodes.Element):
    pass
    
nodes.poemline = poemline

from docutils.writers.html4css1 import HTMLTranslator

def visit_poemline(self, node):
    pass

def depart_poemline(self, node):
    self.body.append('<br />\n')

HTMLTranslator.visit_poemline = visit_poemline
HTMLTranslator.depart_poemline = depart_poemline

import directives
