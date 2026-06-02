# Springer Nature LaTeX class files (sn-jnl)

Bundled for local compilation without a global TeX Live install of the Springer template.

| File | Purpose |
|------|---------|
| `sn-jnl.cls` | Document class (EMSE / Springer Nature journals) |
| `sn-mathphys-num.bst` | Numbered references (used by `main.tex`) |
| Other `sn-*.bst` | Alternative bibliography styles |

**Source:** [nikomatsakis/latex-paper](https://github.com/nikomatsakis/latex-paper) (mirrors official Springer Nature template v3.x, December 2023+).

For the latest official package, download from [Springer Nature LaTeX author support](https://www.springernature.com/gp/authors/campaigns/latex-author-support).

## Compile

From `paper/`:

```bash
./compile.sh
```

Or manually:

```bash
export TEXINPUTS="$PWD/latex-class//:$TEXINPUTS"
export BSTINPUTS="$PWD/latex-class//:$BSTINPUTS"
pdflatex main.tex
```
