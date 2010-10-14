from docutils import nodes
from transform import HIDDEN_FIELD_NAMES, TRUE_VALUES


def first_child(node, child_class):
    """  missing method in docutils """
    idx = node.first_child_matching_class(child_class)
    if idx is not None:
        return node[idx]
    return None

def get_info(node):
    result = {}
    fields = None
    if isinstance(node, nodes.document):
        fields = first_child(node, nodes.docinfo)
    elif isinstance(node, nodes.section):
        fields = first_child(node, nodes.field_list)
        
    if fields:
        for field in fields:
            if isinstance(field, nodes.field):
                key = first_child(field, nodes.field_name).astext()
                value = first_child(field, nodes.field_body).astext()
            else:
                key = field.tagname
                value = field.astext()
            result[key] = value
    return result

def is_hidden_section(node):
    
    info = get_info(node)
    for k in info:
        if k in HIDDEN_FIELD_NAMES and info[k] in TRUE_VALUES:
            return True
    return False
    
#    if not isinstance(node, nodes.section):
#        return None
#    fidx = node.first_child_matching_class(nodes.field_list)
#    if not fidx:
#        return False
#    for field in node[fidx].children:
#        if field[0].astext() in HIDDEN_FIELD_NAMES and field[1].astext() in TRUE_VALUES:
#            return True
#    return False