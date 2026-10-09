"""AST-only evaluator for frozen authorization teaching fixtures.

Never imports or executes fixture source. Limited to boolean expressions and
if/return statements; unexpected syntax is rejected, not interpreted.
"""
import ast
from pathlib import Path


def _expr(node, env):
    if isinstance(node, ast.Constant) and type(node.value) is bool:
        return node.value
    if isinstance(node, ast.Name) and node.id in env:
        return env[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return not _expr(node.operand, env)
    if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
        values = [_expr(v, env) for v in node.values]
        return all(values) if isinstance(node.op, ast.And) else any(values)
    raise ValueError("unsupported policy expression: " + type(node).__name__)


def _block(statements, env):
    for statement in statements:
        if isinstance(statement, ast.Return):
            return True, _expr(statement.value, env)
        if isinstance(statement, ast.If):
            done, value = _block(
                statement.body if _expr(statement.test, env) else statement.orelse,
                env,
            )
            if done:
                return True, value
        elif (isinstance(statement, ast.Expr)
              and isinstance(statement.value, ast.Constant)
              and isinstance(statement.value.value, str)):
            continue  # Documentation strings have no behavior.
        else:
            raise ValueError("unsupported policy statement: " + type(statement).__name__)
    return False, None


def authorize_file(path, authorized, worker_healthy):
    if type(authorized) is not bool or type(worker_healthy) is not bool:
        raise ValueError("boolean inputs required")
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    if (len(functions) != 1 or functions[0].name != "authorize"
            or functions[0].decorator_list
            or [a.arg for a in functions[0].args.args]
            != ["authorized", "worker_healthy"]
            or functions[0].args.defaults or functions[0].args.kwonlyargs):
        raise ValueError("unexpected policy function signature")
    for node in tree.body:
        if node is functions[0]:
            continue
        if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)):
            continue
        raise ValueError("unexpected module-level policy statement")
    done, result = _block(
        functions[0].body,
        {"authorized": authorized, "worker_healthy": worker_healthy},
    )
    if not done:
        raise ValueError("policy did not return")
    return result
