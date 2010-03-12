from  docutils import nodes, writers
from  docutils.writers import html4css1, null
from transform import SectionTransform

class Translator(html4css1.HTMLTranslator):

    def visit_docinfo(self, node):
        raise nodes.SkipNode

    def visit_field_list(self, node):
        raise nodes.SkipNode

    def visit_section(self, node):
        #section_handler(self, node)
        html4css1.HTMLTranslator.visit_section(self, node)
        

class HTMLWriter(html4css1.Writer):

    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = Translator

    def get_transforms(self):
        return html4css1.Writer.get_transforms(self) + [SectionTransform]

class TextWriter(writers.Writer):
    supported = ('text',)
    settings_spec = ('No options here.', '', ())
    settings_defaults = {}

    output = None

    def __init__(self):
        writers.Writer.__init__(self)

    def get_transforms(self):
        return writers.Writer.get_transforms(self) + [SectionTransform]
    
    def translate(self):
        visitor = TextTranslator(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.output


class TextTranslator(nodes.SparseNodeVisitor):

    def __init__(self, document):
        nodes.SparseNodeVisitor.__init__(self, document)
        self.body = []

    @property
    def output(self):
        return ' '.join(self.body)

    def visit_docinfo(self, node):
        raise nodes.SkipNode

    def visit_field_list(self, node):
        raise nodes.SkipNode

    def visit_Text(self, node):
        self.body.append(node.astext())

    def visit_section(self, node):
        #section_handler(self, node)
        # to avoid duplicated text
        if isinstance(node.parent, nodes.section):
            raise nodes.SkipNode
        
    def visit_poemline(self, node):
        pass

    def depart_poemline(self, node):
        pass

class TransformingWriter(null.Writer):
    
    def get_transforms(self):
        return null.Writer.get_transforms(self) + [SectionTransform]
