from docutils import nodes, transforms

HIDDEN_FIELD_NAMES = [u'private', u'hidden']
GENRE_FIELD_NAME = u'genre'
TRUE_VALUES = u'1 y yes'.split()


class SectionTransform(transforms.Transform):

    """
    transform section fields into classes
    """
    # should be placed before FilterTransform at priority 780
    default_priority = 777

    def apply(self):
        for node in self.document.traverse(nodes.section):
            classes = set()
            fidx = node.first_child_matching_class(nodes.field_list)
            if not fidx:
                continue
            for field in node[fidx].children:
                name, value = field[0].astext(), field[1].astext()
                if name in HIDDEN_FIELD_NAMES and value in TRUE_VALUES:
                    classes.add('hidden')
                elif name == GENRE_FIELD_NAME:
                    classes.add('_'.join([name, value]))
                    
            if classes:
                classes = list(classes)
                #node['classes'].extend(classes)  #= node.get('classes', []).extend(classes) #
                node['classes'] = list(set(node['classes']).union(classes))
