import ast
from pathlib import Path
import sys


class CallCollector(ast.NodeVisitor):
    __slots__ = ("names", "attributes", "root")

    def __init__(self, root):
        self.names = set()
        self.attributes = set()
        self.root = root

    def visit_FunctionDef(self, node):
        if node is self.root:
            for statement in node.body:
                self.visit(statement)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Lambda(self, node):
        return None

    def visit_Call(self, node):
        function = node.func
        if isinstance(function, ast.Name):
            self.names.add(function.id)
        elif isinstance(function, ast.Attribute):
            owner = function.value
            if isinstance(owner, ast.Name):
                self.attributes.add((owner.id, function.attr))
        self.generic_visit(node)


def definitions(tree, relative):
    result = []
    stack = [(tree, ())]
    while stack:
        node, scope = stack.pop()
        body = getattr(node, "body", ())
        for child in reversed(body):
            if isinstance(child, ast.ClassDef):
                stack.append((child, scope + (child.name,)))
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = relative + ":" + ".".join(scope + (child.name,))
                result.append((name, scope, isinstance(node, ast.ClassDef), child))
                stack.append((child, scope + (child.name,)))
    return result


def build_graph(root):
    functions = []
    for path in sorted(root.rglob("*.py")):
        relative = path.relative_to(root).as_posix()
        tree = ast.parse(path.read_text(), filename=str(path))
        functions.extend(definitions(tree, relative))
    graph = {name: set() for name, _, _, _ in functions}
    module_functions = {}
    class_methods = {}
    for name, scope, is_method, node in functions:
        relative, qualified = name.split(":", 1)
        if not scope:
            module_functions.setdefault((relative, node.name), []).append(name)
        elif is_method:
            class_methods[(relative, scope[-1], node.name)] = name
    for name, scope, is_method, node in functions:
        relative = name.split(":", 1)[0]
        calls = CallCollector(node)
        calls.visit(node)
        if not is_method and node.name in calls.names:
            graph[name].add(name)
        for called in calls.names:
            targets = module_functions.get((relative, called), ())
            graph[name].update(targets)
        if is_method:
            owner = scope[-1]
            for receiver, called in calls.attributes:
                if receiver == "self" or receiver == "cls" or receiver == owner:
                    target = class_methods.get((relative, owner, called))
                    if target is not None:
                        graph[name].add(target)
    return graph


def find_cycle(graph):
    state = {}
    for start in graph:
        if state.get(start, 0):
            continue
        state[start] = 1
        stack = [(start, iter(graph[start]))]
        position = {start: 0}
        path = [start]
        while stack:
            node, edges = stack[-1]
            try:
                target = next(edges)
            except StopIteration:
                state[node] = 2
                position.pop(node, None)
                path.pop()
                stack.pop()
                continue
            target_state = state.get(target, 0)
            if target_state == 1:
                index = position[target]
                return path[index:] + [target]
            if target_state == 0:
                state[target] = 1
                position[target] = len(path)
                path.append(target)
                stack.append((target, iter(graph[target])))
    return None


def main():
    root = Path(__file__).resolve().parents[1]
    graph = build_graph(root)
    cycle = find_cycle(graph)
    if cycle is not None:
        print("recursive call cycle:", " -> ".join(cycle))
        return 1
    print(f"{len(graph)} functions: no direct or mutual recursion detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
