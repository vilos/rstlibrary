from docutils import nodes, transforms

HIDDEN_FIELD_NAMES = ['private', 'hidden']
GENRE_FIELD_NAME = 'genre'

class SectionTransform(transforms.Transform):

    """
    transform section fields into classes
    """
    # should be placed before FilterTransform at priority 780
    default_priority = 777

    def apply(self):
        classes = set()
        for node in self.document.traverse(nodes.section):
            fl = node.next_node(nodes.field_list)
            if fl is None: 
                return
            for f in fl.traverse(nodes.field):
                name = f.next_node(nodes.field_name).astext()
                value = f.next_node(nodes.field_body)
                if value:
                    value = value.astext()
                    
                if name in HIDDEN_FIELD_NAMES:
                    #node.parent.remove(node)
                    classes.add('hidden')
                    
                elif name == GENRE_FIELD_NAME:
                    classes.add('_'.join([name, value]))
                    
            if classes:
                node['classes'] = list(set(node['classes']).union(classes))
                classes = set()