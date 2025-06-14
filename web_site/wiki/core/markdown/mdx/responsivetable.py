import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.util import etree


class ResponsiveTableExtension(markdown.Extension):
    """Wraps all tables with Bootstrap's table-responsive class"""

    def extendMarkdown(self, md):
        md.treeprocessors.add('responsivetable', ResponsiveTableTree(md), "_end")


class ResponsiveTableTree(Treeprocessor):
    def run(self, root):
        for table_wrapper in list(root.iter('table')):
            table_new = self.create_table_element()
            self.convert_to_wrapper(table_wrapper)
            self.move_children(table_wrapper, table_new)
            table_wrapper.append(table_new)
        return root

    def create_table_element(self):
        """Create table element with text and tail"""
        element = etree.Element('table')
        element.text = '\n'
        element.tail = '\n'
        return element

    def move_children(self, element1, element2):
        """Moves children from element1 to element2"""
        for child in list(element1):
            element2.append(child)
        # reversed is needed to safely remove items while iterating
        for child in reversed(list(element1)):
            element1.remove(child)

    def convert_to_wrapper(self, element):
        element.tag = 'div'
        element.set('class', 'table-responsive')


def makeExtension(*args, **kwargs):
    """Return an instance of the extension."""
    return ResponsiveTableExtension(*args, **kwargs)
