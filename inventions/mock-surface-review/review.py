"""Offline, deliberately narrow direct-method surface comparison."""
import argparse
import ast
import json
import os
import stat

MAX_BYTES = 65536
MAX_METHODS = 256


def bounded_read(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    with os.fdopen(descriptor, 'rb') as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ValueError('input must be a regular file')
        data = handle.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError('input exceeds 65536 bytes')
    return data.decode('utf-8')


def review(source, manifest_text):
    for value in (source, manifest_text):
        if not isinstance(value, str) or len(value.encode('utf-8')) > MAX_BYTES:
            raise ValueError('each input must be UTF-8 text at most 65536 bytes')
    manifest = json.loads(manifest_text)
    if not isinstance(manifest, dict) or set(manifest) != {'class', 'methods'}:
        raise ValueError('manifest requires exactly class and methods')
    class_name, expected = manifest['class'], manifest['methods']
    if not isinstance(class_name, str) or not class_name.isidentifier():
        raise ValueError('invalid class name')
    if not isinstance(expected, list) or len(expected) > MAX_METHODS:
        raise ValueError('methods must be a list of at most 256 names')
    if any(not isinstance(n, str) or not n.isidentifier() for n in expected):
        raise ValueError('invalid method name')
    if len(set(expected)) != len(expected):
        raise ValueError('duplicate manifest method')
    tree = ast.parse(source)
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name]
    if len(classes) != 1:
        raise ValueError('expected exactly one matching top-level class')
    cls = classes[0]
    if cls.bases or cls.keywords or cls.decorator_list:
        raise ValueError('inheritance, metaclasses and class decorators are unsupported')
    methods = []
    for node in cls.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.decorator_list:
                raise ValueError('method decorators are unsupported')
            if node.name in ('__getattr__', '__getattribute__', '__setattr__'):
                raise ValueError('dynamic attribute hooks are unsupported')
            methods.append(node.name)
        elif isinstance(node, ast.Pass):
            continue
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue
        else:
            raise ValueError('class assignments and conditional/dynamic members are unsupported')
    if len(methods) > MAX_METHODS or len(set(methods)) != len(methods):
        raise ValueError('too many or duplicate direct methods')
    actual, allowed = set(methods), set(expected)
    return {'schema': 1, 'class': class_name,
            'extra_direct_methods': sorted(actual - allowed),
            'missing_direct_methods': sorted(allowed - actual),
            'shared_direct_methods': sorted(actual & allowed),
            'names_equal': actual == allowed,
            'scope': 'Direct method names only; manifest supplied by caller and not independently verified. No runtime, signature, behavior, export or security proof. Method bodies and other module statements are not analyzed or executed; runtime monkeypatching can change the surface.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('manifest')
    args = parser.parse_args()
    try:
        result = review(bounded_read(args.source), bounded_read(args.manifest))
    except (ValueError, SyntaxError, OSError, RecursionError) as error:
        parser.exit(2, f'Cannot review input: {type(error).__name__}\n')
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
