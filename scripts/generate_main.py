#!/usr/bin/env python3
import os, re, ast, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
API_DIR = ROOT / "suri" / "api"
MAIN_PY = ROOT / "suri" / "main.py"

API_DIR.mkdir(parents=True, exist_ok=True)

def find_routers(py_path: pathlib.Path):
    """
    해당 파일에서 APIRouter 인스턴스 변수명들을 찾아 (var_name) 리스트로 반환
    """
    try:
        text = py_path.read_text(encoding="utf-8")
    except Exception:
        return []

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    routers = []
    for node in ast.walk(tree):
        # router = APIRouter(...), api_router = fastapi.APIRouter(...)
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            # 함수명(혹은 속성)의 끝 이름
            func = node.value.func
            func_name = None
            if isinstance(func, ast.Name):
                func_name = func.id
            elif isinstance(func, ast.Attribute):
                func_name = func.attr
            if func_name == "APIRouter":
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        routers.append(target.id)
    return routers

def module_path_from_file(file_path: pathlib.Path):
    # suri/api/foo/bar.py -> suri.api.foo.bar
    rel = file_path.relative_to(ROOT).with_suffix("")
    return ".".join(rel.parts)

def collect_all():
    found = []
    for py in API_DIR.rglob("*.py"):
        if py.name == "__init__.py":
            continue
        routers = find_routers(py)
        if not routers:
            # 힌트: 파일에 from fastapi import APIRouter 있고 router 변수가 있을 수도
            txt = py.read_text(encoding="utf-8", errors="ignore")
            if "APIRouter" in txt and re.search(r"\brouter\s*=", txt):
                routers = ["router"]
        if routers:
            found.append((py, routers))
    return found

def generate_main(found):
    lines = []
    lines.append("from fastapi import FastAPI\n")

    import_lines = []
    include_lines = []

    for fpath, vars_ in found:
        mod = module_path_from_file(fpath)  # e.g., suri.api.users
        base_name = fpath.stem
        for v in vars_:
            alias = f"{base_name}_{v}"
            import_lines.append(f"from {mod} import {v} as {alias}")
            include_lines.append(f"app.include_router({alias})")

    # 기본 라우터가 하나도 없을 때 대비
    if not include_lines:
        import_lines.append("from fastapi import APIRouter")
        import_lines.append("")
        include_lines.append("# default router (no API routers detected)")
        include_lines.append("fallback = APIRouter()")
        include_lines.append("@fallback.get('/health')\ndef _health():\n    return {'ok': True}")
        include_lines.append("app.include_router(fallback)")

    lines.extend(import_lines)
    lines.append("\n\napp = FastAPI()\n")
    lines.extend(include_lines)
    lines.append(
        "\n\n@app.get('/')\ndef root():\n    return {'message': 'Suri API Running'}\n"
    )
    lines.append(
        "\nif __name__ == '__main__':\n"
        "    import uvicorn\n"
        "    uvicorn.run('suri.main:app', host='0.0.0.0', port=8000, reload=True)\n"
    )
    MAIN_PY.write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    found = collect_all()
    generate_main(found)
    print(f"🧭 라우터 탐색 완료: {len(found)}개 파일에서 APIRouter 발견")
    for f, vs in found:
        print(" -", f.relative_to(ROOT), ":", ", ".join(vs))
    print(f"✍️  생성: {MAIN_PY.relative_to(ROOT)}")
