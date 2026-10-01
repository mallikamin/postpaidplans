"""check_generator_drift.py — prove every page generator reproduces the committed pages.

Run it BEFORE hand-editing a generated page and AFTER changing a generator:
    python check_generator_drift.py
Exit 0 = every generator is a no-op against HEAD (safe to rerun any of them).
Exit 1 = drift: a generated page and its generator disagree. Put the change in the
generator, regenerate, review the diff, commit both. Never hand-edit generated pages only.

Runs each generator, records what it changed, then restores the working tree.
Needs a clean tree for the generated paths (it refuses to run otherwise).
"""
import os, subprocess, sys

REPO = os.path.dirname(os.path.abspath(__file__))
GENS = ["generate_plan_pages.py", "generate_location_pages.py",
        "generate_faq_page.py", "generate_calling_pages.py"]


def git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True,
                          text=True, encoding="utf-8").stdout


def dirty_html():
    out = git("status", "--porcelain", "-uall")
    return {l[3:].strip('"') for l in out.splitlines() if l[3:].strip('"').endswith(".html")}


if dirty_html():
    sys.exit("refusing: uncommitted .html changes present: %s" % sorted(dirty_html())[:5])

drift = False
for g in GENS:
    r = subprocess.run([sys.executable, g], cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        print(f"FAIL {g}: exit {r.returncode}\n{r.stderr[-400:]}")
        drift = True
    changed = sorted(dirty_html())
    # line-ending-only rewrites show as modified but have no content diff
    real = [p for p in changed
            if subprocess.run(["git", "diff", "--ignore-cr-at-eol", "--quiet", "--", p], cwd=REPO).returncode]
    if real:
        drift = True
        print(f"DRIFT {g}: {len(real)} page(s) differ, e.g. {real[:4]}")
        print("   ", git("diff", "--ignore-cr-at-eol", "--shortstat", "--", *real).strip())
    else:
        print(f"ok    {g}")
    tracked = [p for p in changed if git("ls-files", "--", p).strip()]
    if tracked:
        git("checkout", "--", *tracked)
    for p in set(changed) - set(tracked):
        os.remove(os.path.join(REPO, p))
sys.exit(1 if drift else 0)
