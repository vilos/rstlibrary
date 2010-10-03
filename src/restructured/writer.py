from  docutils import nodes, writers
from  docutils.writers import html4css1, null
from transform import SectionTransform, HIDDEN_FIELD_NAMES, TRUE_VALUES

        
def is_hidden_section(node):
    if not isinstance(node, nodes.section):
        return None
    fidx = node.first_child_matching_class(nodes.field_list)
    if not fidx:
        return False
    for field in node[fidx].children:
        if field[0].astext() in HIDDEN_FIELD_NAMES and field[1].astext() in TRUE_VALUES:
            return True
    return False
        
class Translator(html4css1.HTMLTranslator):
    
    def __init__(self, document):
        self.hide = False
        html4css1.HTMLTranslator.__init__(self, document)
        
    def visit_docinfo(self, node):
        raise nodes.SkipNode

    def visit_field_list(self, node):
        raise nodes.SkipNode

    def visit_paragraph(self, node):
        if self.hide:
            raise nodes.SkipNode
        else:
            html4css1.HTMLTranslator.visit_paragraph(self, node)
            
    def visit_section(self, node):
        self.hide = is_hidden_section(node)
        if 'section' in node['classes']:
            classes = set(node['classes'])
            classes.remove('section')
            node['classes'] = list(classes)
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
        
        if is_hidden_section(node):
            raise nodes.SkipNode
        
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
