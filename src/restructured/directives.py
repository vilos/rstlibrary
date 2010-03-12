
"""Custom directives and transformations."""

__docformat__ = 'reStructuredText'

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive
from docutils.transforms import misc, Transform

# list of css classes used in reST as directives

PARA_STYLES = [
    'centered',
    'bold'
]

class RemoveNext(Transform):
    """
    Remove the immediately following non-comment element.
    """

    default_priority = 777

    def apply(self):
        pending = self.startnode
        parent = pending.parent
        child = pending

        # Check for appropriate following siblings:
        for index in range(parent.index(child) + 1, len(parent)):
            element = parent[index]
            if (isinstance(element, nodes.Invisible) or
                isinstance(element, nodes.system_message)):
                continue

            parent.remove(pending)  # the directive itself
            parent.remove(element)  # next element
            if len(parent.children) == 0:
                parent.append(nodes.comment(text="hidden"))
            return

        error = self.document.reporter.error(
            'No suitable element following "%s" directive'
            % pending.details['directive'],
            nodes.literal_block(pending.rawsource, pending.rawsource),
            line=pending.line)
        pending.parent.replace(pending, error)

class BlockLines(Transform):
    """
    wrap all lines of the next paragraph into <p></p> element while preserving css class
    """

    default_priority = 777

    def apply(self):
        pending = self.startnode
        parent = pending.parent
        allpage = pending.details.get('allpage', False)
        cssclass = pending.details.get('class', [])
        added = False

        # Check for appropriate following siblings:
        current = parent.index(pending)
        for  element in parent[current + 1:]:
            # if error or next poem finish
            if (isinstance(element, nodes.system_message) or
                (isinstance(element, nodes.pending) and
                 element.transform == BlockLines )):
                break
            # skip non paragraphs
            if (not isinstance(element, nodes.paragraph)):
                continue
            paras = []
            for child in element.children:
                if isinstance(child, nodes.Text):
                    lines = child.astext().splitlines()
                    for line in lines[:-1]:
                        p = nodes.poemline(line, line)
                        paras.append(p)
                    #
                    if len(lines) > 0:
                        t = nodes.Text(lines[-1],lines[-1])
                        paras.append(t)
                else:
                    #  non-text without change
                    paras.append(child)

            if paras:
                added = True
                element.clear()
                element.extend(paras)

                if cssclass:
                    element['classes'].extend(cssclass)

            if not allpage:
                break
        if added:
            parent.remove(pending)  # the directive itself
        else:
            error = self.document.reporter.error(
                'No suitable element following "%s" directive'
                % pending.details['directive'],
                nodes.literal_block(pending.rawsource, pending.rawsource),
                line=pending.line)
            parent.replace(pending, error)
        return

class Hidden(Directive):

    """
    Skip the content or remove the next element.
    When applied to the next element, a "pending" element is inserted, and a
    transform does the work later.
    """

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    has_content = True

    def run(self):

        node_list = []
        if not self.content:
            pending = nodes.pending(RemoveNext, {'directive': self.name}, self.block_text)
            self.state_machine.document.note_pending(pending)
            node_list.append(pending)
        return node_list

directives.register_directive('hidden', Hidden)

class Stanza(Directive):
    """  apply blocquote transform  to next paragraph only
    """
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    has_content = False

    allpage = False

    def run(self):
        # css class is the same as the directive name
        classes = [self.name]
        if self.arguments:
            try:
                classes.extend(directives.class_option(self.arguments[0]))
            except ValueError:
                raise self.error(
                    'Invalid class attribute value for "%s" directive: "%s".'
                    % (self.name, self.arguments[0]))

        pending = nodes.pending(BlockLines, {'directive': self.name, 'class': classes, 'allpage': self.allpage}, self.block_text)
        self.state_machine.document.note_pending(pending)
        return [pending]

directives.register_directive('stanza', Stanza)

class Poem(Stanza):
    """ apply blocquote transform until the end
    """

    allpage = True

directives.register_directive('poem', Poem)

class GenericClass(Directive):
    """ set a class attribute on the next element using a pending element
    """
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    has_content = False

    def run(self):
        # css class is the same as the directive name
        pending = nodes.pending(misc.ClassAttribute, {'directive': self.name, 'class': [self.name]}, self.block_text)
        self.state_machine.document.note_pending(pending)
        return [pending]


def registerClassDirective(directive):
    
    directives.register_directive(directive, GenericClass)
    
# register all defined css styles with the generic directive
for s in PARA_STYLES:
    registerClassDirective(s)
