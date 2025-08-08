# audit_templates.py
import os, re

BASE = os.path.dirname(__file__)
TPL_DIR = os.path.join(BASE, "templates")

# 1) Coletar templates referenciados no código
pattern = re.compile(r"render_template\(\s*['\"]([^'\"]+)['\"]")
referenced = set()

for root, _, files in os.walk(BASE):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
                for m in pattern.finditer(text):
                    referenced.add(m.group(1))
            except Exception:
                pass

# 2) Coletar templates existentes (html/htm/j2)
existing = set()
for root, _, files in os.walk(TPL_DIR):
    for f in files:
        if f.lower().endswith((".html", ".htm", ".j2")):
            rel = os.path.relpath(os.path.join(root, f), TPL_DIR).replace("\\", "/")
            existing.add(rel)

# 3) Verificar inconsistências .htm vs .html
#    Ex.: rota pede .html mas só existe .htm com mesmo nome base
def base_name(p): 
    n = os.path.splitext(p)[0]
    return n

existing_bases = {}
for rel in existing:
    existing_bases.setdefault(base_name(rel), set()).add(rel)

suspects = []
for r in referenced:
    if r not in existing:
        b = base_name(r)
        if b in existing_bases:
            suspects.append((r, sorted(existing_bases[b])))

missing = sorted(t for t in referenced if t not in existing and base_name(t) not in existing_bases)

print("=== TEMPLATES REFERENCIADOS:", len(referenced))
for t in sorted(referenced):
    print("  -", t)

print("\n=== TEMPLATES EXISTENTES:", len(existing))
# (omita listão se for enorme; descomente se quiser ver tudo)
# for t in sorted(existing): print("  -", t)

print("\n=== FALTANDO (não existe):", len(missing))
for t in missing:
    print("  -", t)

print("\n=== SUSPEITOS (.htm vs .html):", len(suspects))
for want, have in suspects:
    print("  - Rota pede:", want)
    print("    Existe(m):", ", ".join(have))