# EMSE Manuscript

LaTeX sources for *Beyond Structural Validity* (Empirical Software Engineering).

| Path | Role |
|------|------|
| `main.tex` | Springer `sn-jnl` root document |
| `sections/` | Section stubs (01–09) |
| `tables/` | Auto-generated result tables |
| `figures/` | Publication figures |
| `references/` | Bibliography |
| `notes/` | Author working notes (not for submission) |
| `submission/` | Cover letter, declarations, supplementary templates |

**Status:** Skeleton only — no manuscript content yet.

Design authority: [docs/study_design.md](../docs/study_design.md)

## Local compilation

The Springer `sn-jnl.cls` class is bundled in `latex-class/` (not installed system-wide).

```bash
cd paper
./compile.sh
```

Or, if `sn-jnl.cls` is missing:

```bash
export TEXINPUTS="$PWD/latex-class//:$TEXINPUTS"
pdflatex main.tex
```

See `latex-class/README.md` for template provenance.
