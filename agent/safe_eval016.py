"""Exec-free evaluator for the teaching fixtures' authorize(authorized, worker_healthy). Supports only: if/return, names, bool constants, not/and/or.
Replaces the exec() regression helper that Semgrep flagged (python.lang.security.audit.exec-detected) in agent011.py."""
import ast
from pathlib import Path
def _ev(n,env):
    if isinstance(n,ast.Constant) and isinstance(n.value,bool):return n.value
    if isinstance(n,ast.Name) and n.id in env:return env[n.id]
    if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.Not):return not _ev(n.operand,env)
    if isinstance(n,ast.BoolOp):
        vals=[_ev(v,env) for v in n.values];return all(vals) if isinstance(n.op,ast.And) else any(vals)
    raise ValueError("unsupported node "+type(n).__name__)
def _run(body,env):
    for st in body:
        if isinstance(st,ast.Return):return True,_ev(st.value,env)
        if isinstance(st,ast.If):
            if _ev(st.test,env):
                done,v=_run(st.body,env)
            else:done,v=_run(st.orelse,env)
            if done:return True,v
        elif isinstance(st,ast.Expr) and isinstance(st.value,ast.Constant):continue
        else:raise ValueError("unsupported statement "+type(st).__name__)
    return False,None
def authorize(path,authorized,worker_healthy):
    tree=ast.parse(Path(path).read_text());fn=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="authorize"]
    if len(fn)!=1:raise ValueError("expected one authorize()")
    done,v=_run(fn[0].body,{"authorized":authorized,"worker_healthy":worker_healthy})
    if not done:raise ValueError("no return")
    return v
def regress(path):
    return {"healthy_auth":authorize(path,True,True),"healthy_unauth":authorize(path,False,True),"unhealthy_auth":authorize(path,True,False),"unhealthy_unauth":authorize(path,False,False)}
