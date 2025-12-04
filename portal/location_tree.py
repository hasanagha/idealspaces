"""Class to build a tree of locations and counts"""
import treelib

from portal.models import Location


class LocationTree:
    def __init__(self):
        self.tree = treelib.Tree()
        self.tree.create_node('root', 'root')

    def add_location_to_tree(self, location, count):
        self.tree.create_node(location.name, location.pk, location.parent.pk if location.parent else 'root', {
            'location': location,
            'count': count
        })

    def add_location(self, location, count=1):
        parents = []
        current_location = location.parent
        while current_location is not None:
            parents.append(current_location)
            current_location = current_location.parent

        parents.reverse()
        for parent in parents:
            if self.tree.contains(parent.pk):
                node = self.tree.get_node(parent.pk)
                node.data['count'] += count
            else:
                self.add_location_to_tree(parent, count)

        if self.tree.contains(location.pk):
            node = self.tree.get_node(location.pk)
            node.data['count'] += count
        else:
            self.add_location_to_tree(location, count)
