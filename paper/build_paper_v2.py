"""Build the V2 manuscript in LaTeX and DOCX.

Reads paper/MANUSCRIPT_SKILL_V2.md or its anonymised sibling and emits
paper/MANUSCRIPT_SKILL_V2[_ANON].tex/.docx. Existing V1 manuscripts and
artefacts are never touched. In addition to the V1 fences, this builder
accepts:

    ```figurewide
    fig_v2_design.pdf | fig:design | caption
    ```

which emits a two-column figure. The DOCX path substitutes the PNG sibling.

Re-run:
    uv run python paper/build_paper_v2.py
    uv run python paper/build_paper_v2.py --anon
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parent

# SANER 2027 reviews double-anon: non-compliance is desk-rejected without
# review. Build with --anon to emit a submission variant with the author
# block suppressed.
ANON = False
AUTHOR = "Hemadharsana S"
AUTHORS = [
    ("Hemadharsana S",
     "Dept. of Computer Science and Engineering (Cyber Security)",
     "hemadharsana@gmail.com"),
    ("Sanjeev Kumar", "Dept. of Computer Science and Engineering",
     "hello@sanjeevkumar.me"),
    ("Prajan SS", "Dept. of Artificial Intelligence & Data Science",
     "prajanss23@gmail.com"),
]
AFFILIATION = "Saveetha Engineering College, Chennai, Tamil Nadu, India"
AUTHOR_BLOCK = (
    r"\IEEEauthorblockN{Hemadharsana S\textsuperscript{1}, "
    r"Sanjeev Kumar\textsuperscript{2}, and Prajan SS\textsuperscript{3}}"
    "\n"
    r"\IEEEauthorblockA{\textsuperscript{1,2}Dept. of Computer Science and Engineering (\textsuperscript{1}Cyber Security), "
    r"\textsuperscript{3}Dept. of Artificial Intelligence \& Data Science\\"
    "\n"
    r"Saveetha Engineering College, Chennai, Tamil Nadu, India\\"
    "\n"
    r"hemadharsana@gmail.com, hello@sanjeevkumar.me, prajanss23@gmail.com}"
)

# Dropped from the header: submission metadata, not content.
VENUE_LINE_RE = re.compile(r"^\*\*Target Venue:\*\*.*$", re.M)

# ---------------------------------------------------------------- block parse
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
FENCE_RE = re.compile(r"^```(\w*)\s*$")
HR_RE = re.compile(r"^-{3,}$")
BULLET_RE = re.compile(r"^\s*[-*•]\s+(.*)$")
NUMBER_RE = re.compile(r"^\s*(\d+)\.\s+(.*)$")
TABLE_SEP_RE = re.compile(r"^\s*\|?[\s:\-|]+\|[\s:\-|]*$")


def is_table_row(line: str) -> bool:
    return line.lstrip().startswith("|") and line.rstrip().endswith("|")


def split_row(line: str) -> list[str]:
    inner = line.strip().strip("|")
    return [c.strip() for c in inner.split("|")]


def parse_blocks(text: str) -> list[tuple[str, object]]:
    """-> list of (kind, payload)."""
    blocks: list[tuple[str, object]] = []
    lines = text.split("\n")
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        m = FENCE_RE.match(line)
        if m:
            lang = m.group(1)
            i += 1
            buf = []
            while i < n and not FENCE_RE.match(lines[i]):
                buf.append(lines[i])
                i += 1
            i += 1
            blocks.append(("code", (lang, "\n".join(buf))))
            continue

        m = HEADING_RE.match(line)
        if m:
            blocks.append(("h", (len(m.group(1)), m.group(2).strip())))
            i += 1
            continue

        if HR_RE.match(line.strip()):
            blocks.append(("hr", None))
            i += 1
            continue

        # table: a pipe row followed by a separator row
        if is_table_row(line) and i + 1 < n and TABLE_SEP_RE.match(lines[i + 1]) \
                and is_table_row(lines[i + 1]):
            header = split_row(line)
            i += 2
            rows = []
            while i < n and is_table_row(lines[i]):
                rows.append(split_row(lines[i]))
                i += 1
            # An optional "Table: <label> | <caption>" line immediately after
            # the grid becomes its IEEE caption and label. Without it a table
            # cannot be cross-referenced, and \ref renders as "??".
            cap, key = "", ""
            j = i
            while j < n and not lines[j].strip():
                j += 1
            if j < n and lines[j].lstrip().startswith("Table:"):
                spec = lines[j].lstrip()[len("Table:"):].strip()
                key, _, cap = spec.partition("|")
                i = j + 1
            blocks.append(("table", (header, rows, key.strip(), cap.strip())))
            continue

        if line.lstrip().startswith(">"):
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(lines[i].lstrip().lstrip(">").strip())
                i += 1
            blocks.append(("quote", " ".join(x for x in buf if x)))
            continue

        if BULLET_RE.match(line) or NUMBER_RE.match(line):
            ordered = bool(NUMBER_RE.match(line))
            items = []
            while i < n:
                bm = (NUMBER_RE if ordered else BULLET_RE).match(lines[i])
                if not bm:
                    break
                items.append(bm.group(2) if ordered else bm.group(1))
                i += 1
                # Markdown authors commonly separate list items with a blank
                # line. Without consuming it here each item became its own
                # enumerate block and every entry rendered as "1)".
                while i < n and not lines[i].strip():
                    j = i
                    while j < n and not lines[j].strip():
                        j += 1
                    if j < n and (NUMBER_RE if ordered else BULLET_RE).match(lines[j]):
                        i = j
                    else:
                        break
            blocks.append(("ol" if ordered else "ul", items))
            continue

        # paragraph: consume until a blank line or a block opener
        buf = []
        while i < n and lines[i].strip():
            if (HEADING_RE.match(lines[i]) or FENCE_RE.match(lines[i])
                    or HR_RE.match(lines[i].strip())
                    or lines[i].lstrip().startswith(">")
                    or BULLET_RE.match(lines[i]) or NUMBER_RE.match(lines[i])
                    or is_table_row(lines[i])):
                break
            buf.append(lines[i].strip())
            i += 1
        if buf:
            blocks.append(("p", " ".join(buf)))
    return blocks


# ------------------------------------------------------------------ inline
DISPLAY_RE = re.compile(r"^\$\$\s*(.+?)\s*\$\$$", re.S)
MATH_RE = re.compile(r"\$([^$]+)\$")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
CODE_RE = re.compile(r"`([^`]+)`")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
EMPH_RE = re.compile(r"(?<![\*\w])\*([^*\n]+)\*(?!\*)")
ESCAPES = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
    "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


# Unicode that appears in prose (inside $...$ it is passed through untouched).
# lmroman has no glyphs for these, so they must be transliterated.
# Unicode appearing in prose (inside $...$ it is passed through untouched).
# lmroman has no glyphs for these.
#
# Split deliberately: math symbols become math-mode ($...$) because \sigma and
# friends are undefined outside math; text symbols map straight to ASCII.
UNICODE_MATH = {
    "\u03c3": "sigma", "\u03bc": "mu", "\u0394": "Delta", "\u03c1": "rho",
    "\u03c4": "tau", "\u03b8": "theta", "\u03b1": "alpha", "\u03b2": "beta",
    "\u03c6": "phi", "\u03bb": "lambda", "\u2248": "approx", "\u2265": "geq",
    "\u2264": "leq", "\u00d7": "times", "\u2192": "to", "\u00b7": "cdot",
    "\u00b1": "pm", "\u2260": "neq", "\u221a": "sqrt", "\u2026": "ldots",
    "\u2208": "in", "\u2282": "subset", "\u2205": "emptyset",
}
UNICODE_TEXT = {
    "\u2212": "-", "\u2013": "--", "\u2014": "---", "\u2032": "'",
    "\u2018": "`", "\u2019": "'", "\u201c": "``", "\u201d": "''",
    "\u00a0": " ", "\u2500": "-", "\u2502": "|", "\u00b0": "$^\\circ$",
}

def tex_escape(text: str) -> str:
    out = []
    for ch in text:
        if ch in UNICODE_MATH:
            out.append("$%s$" % UNICODE_MATH[ch])
        elif ch in UNICODE_TEXT:
            out.append(UNICODE_TEXT[ch])
        else:
            out.append(ESCAPES.get(ch, ch))
    return "".join(out)


def tex_inline(text: str) -> str:
    """Markdown inline -> LaTeX, preserving $math$ verbatim.

    Formatting commands are lifted out into placeholders *before* escaping, so
    that escaping cannot mangle the backslashes this function itself emits.
    """
    stash: list[str] = []

    def hold(tex: str) -> str:
        stash.append(tex)
        return f"\x01{len(stash) - 1}\x01"

    # Math is stashed first, rather than split into separate parts. Splitting
    # meant a `**bold $x$**` span was cut in half before BOLD_RE ever ran, so
    # the opening `**` saw no closing marker and the asterisks printed
    # literally. Stashing keeps the span whole, and the math restores inside
    # the \textbf{} where it belongs.
    s = MATH_RE.sub(lambda m: hold(f"${m.group(1)}$"), text)

    def _link(m):
        label, url = m.group(1), m.group(2)
        # \href{url}{url} cannot break across lines, which overflows the
        # column when two repository links sit side by side. \url can.
        if label.strip() == url.strip():
            return hold(r"\url{%s}" % url)
        return hold(r"\href{%s}{%s}" % (url, tex_escape(label)))

    s = TEXCMD_RE.sub(lambda m: hold(m.group(0)), s)
    s = LINK_RE.sub(_link, s)
    s = CODE_RE.sub(lambda m: hold(r"\texttt{%s}" % tex_escape(m.group(1))), s)
    s = BOLD_RE.sub(lambda m: hold(r"\textbf{%s}" % tex_escape(m.group(1))), s)
    s = EMPH_RE.sub(lambda m: hold(r"\emph{%s}" % tex_escape(m.group(1))), s)
    joined = tex_escape(s)
    # Formatting can nest (e.g. **bold with `code` inside**), so a placeholder
    # emitted by one rule can sit inside another rule's stash entry. re.sub does
    # not rescan its own replacements, so restore until the text stops changing.
    previous = None
    while previous != joined:
        previous = joined
        joined = re.sub("\x01(\\d+)\x01",
                        lambda m: stash[int(m.group(1))], joined)
    return joined


def docx_inline(text: str) -> list[tuple[str, str]]:
    """Markdown inline -> [(style, text)]; math becomes italic, markers dropped.

    Scanned left-to-right as one token stream rather than split on math first.
    Splitting cut `**bold $x$**` in half, so the emphasis was lost and the
    asterisks survived into the document. Emphasis spans recurse, so a code
    span nested inside bold gets its own run instead of leaking backticks.
    """
    styles: list[tuple[str, str]] = []

    def emit(style: str, raw: str) -> None:
        if not raw:
            return
        styles.append((style, "".join(
            UNICODE_MATH.get(c, UNICODE_TEXT.get(c, c)) for c in raw)))

    def scan(src: str, carry: str = "") -> None:
        pos = 0
        while pos < len(src):
            best = None
            for pattern, style in ((MATH_RE, "i"), (CODE_RE, "c"),
                                   (BOLD_RE, "b"), (EMPH_RE, "i")):
                m = pattern.search(src, pos)
                if m and (best is None or m.start() < best[0].start()):
                    best = (m, style)
            if best is None:
                emit(carry, src[pos:])
                return
            m, style = best
            emit(carry, src[pos:m.start()])
            body = m.group(1)
            if style == "c" or m.re is MATH_RE:
                emit(style if m.re is MATH_RE else "c", body)
            else:
                scan(body, "b" if style == "b" else carry)
            pos = m.end()

    scan(text)
    return styles or [("t", text)]

# --------------------------------------------------------------------- LaTeX
PREAMBLE = r"""\documentclass[conference]{IEEEtran}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{array}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{tikz}
\usetikzlibrary{positioning,arrows.meta,calc}
\usepackage{multirow}
\usepackage{textcomp}
\usepackage{url}
\usepackage{fvextra}
\usepackage{adjustbox}
\usepackage[hidelinks]{hyperref}

\newenvironment{quoteblock}{\begin{quote}\small}{\end{quote}}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\setlength{\textfloatsep}{8pt plus 2pt minus 2pt}
\setlength{\floatsep}{6pt plus 2pt minus 2pt}
\setlength{\intextsep}{6pt plus 2pt minus 2pt}
\setlength{\dbltextfloatsep}{8pt plus 2pt minus 2pt}
\setlength{\dblfloatsep}{6pt plus 2pt minus 2pt}

\begin{document}
"""

END = r"\end{document}"


VERBATIM_FOLD = {
    "\u2190": "<-", "\u2192": "->", "\u2208": "in", "\u00a7": "S",
    "\u2500": "-", "\u2502": "|", "\u250c": "+", "\u2510": "+",
    "\u2514": "+", "\u2518": "+", "\u251c": "+", "\u2524": "+",
    "\u253c": "+", "\u2571": "/", "\u256d": "+", "\u256e": "+",
    "\u2570": "+", "\u256f": "+", "\u2212": "-", "\u2013": "-",
    "\u2014": "--", "\u00b7": "*", "\u2022": "*", "\u2264": "<=",
    "\u2265": ">=", "\u00d7": "x",
    "\u252c": "-", "\u2534": "-", "\u25bc": "|", "\u25b2": "|",
    "\u25ba": ">", "\u25c4": "<", "\u25aa": "*", "\u25cf": "*",
    "\u25cb": "o", "\u255e": "+", "\u2561": "+",
}


def fold_ascii(body: str) -> str:
    """Fold box-drawing and arrows to ASCII so the font can render them."""
    return "".join(VERBATIM_FOLD.get(ch, ch) for ch in body)


TEXCMD_RE = re.compile(r"\\(?:ref|eqref|label|autoref)\{[^}]*\}")

MANUAL_NUM_RE = re.compile(r"^\s*\d+(?:\.\d+)*\.?\s+")


def strip_manual_number(text: str) -> str:
    """Drop a leading "1." / "5.2" from a heading.

    IEEEtran generates Roman-numeral section numbers, so a heading that already
    carries a manual number prints as "I. 1. Introduction".
    """
    return MANUAL_NUM_RE.sub("", text)


def emit_tex(blocks: list[tuple[str, object]], title: str) -> str:
    out = [PREAMBLE]
    out.append(r"\title{%s}" % tex_inline(title))
    if ANON:
        out.append(
            r"\author{\IEEEauthorblockN{Anonymous submission}%s"
            r"\IEEEauthorblockA{Author and affiliation omitted for"
            r" double-anonymous review}}" % ("\n")
        )
    else:
        out.append(r"\author{" + AUTHOR_BLOCK + "}")
    out.append(r"\maketitle")

    in_abstract = False
    in_refs = False
    ref_i = 0
    prev_heading = 0

    for kind, payload in blocks:
        if kind == "h":
            level, text = payload
            text_t = tex_inline(text)
            heading = strip_manual_number(text_t).strip()
            heading_l = heading.lower()
            if level == 1:
                continue                      # title consumed above
            if level == 2 and text.lower().strip() == "abstract":
                out.append(r"\begin{abstract}")
                in_abstract = True
                continue
            if in_abstract and text.lower().strip().startswith("keywords"):
                out.append(r"\end{abstract}")
                in_abstract = False
                kw = text.split(":", 1)[1].strip() if ":" in text else ""
                out.append(r"\noindent\textbf{Index Terms---} %s" % tex_inline(kw))
                continue
            if in_refs:
                out.append(r"\end{thebibliography}")
                in_refs = False
            if heading_l in ("acknowledgment", "acknowledgments",
                             "acknowledgement", "acknowledgements"):
                out.append(r"\section*{%s}" % heading)
                prev_heading = level
                continue
            if heading_l == "references":
                # IEEEtran's thebibliography prints the unnumbered REFERENCES
                # heading and [n] labels; a numbered \section would render as
                # "XI. References" with "1)" items.
                out.append(r"\begin{thebibliography}{99}\footnotesize"
                           r"\setlength{\itemsep}{-0.5pt}"
                           r"\setlength{\parsep}{0pt}")
                in_refs = True
                continue
            cmd = {2: "section", 3: "subsection",
                   4: "subsubsection"}.get(level, "paragraph")
            # IEEEtran numbers sections itself ("I. Introduction"); a manual
            # "1." prefix from the markdown would print as "I. 1. Introduction".
            out.append(r"\%s{%s}" % (cmd, heading))
            prev_heading = level
            continue

        if kind == "p":
            if in_abstract:
                km = re.match(r"^\*\*Keywords?\s*:?\*\*\s*:?\s*(.*)$",
                              payload, re.I)
                if km:
                    out.append(r"\end{abstract}")
                    in_abstract = False
                    out.append(r"\noindent\textbf{Index Terms---} %s"
                               % tex_inline(km.group(1).strip()))
                    continue
            dm = DISPLAY_RE.match(payload)
            if dm:
                out.append(r"\begin{equation}%s\end{equation}" % dm.group(1))
            else:
                out.append(tex_inline(payload) + "\n")
            continue

        if kind == "hr":
            continue

        if kind == "quote":
            out.append(r"\begin{quoteblock} %s \end{quoteblock}"
                       % tex_inline(payload))
            continue

        if kind == "code":
            lang, body = payload

            # A tikz fence renders as a real block diagram rather than ASCII
            # art. ASCII in a monospace box cannot be centred, cannot be
            # referenced from the text, and wraps unpredictably.
            # A tikz fence renders a real block diagram. An optional leading
            # directive supplies the caption and label:
            #   %% LABEL | caption text
            # followed by the tikzpicture body.
            if lang == "tikz":
                label, cap, code = "", "", body
                first, _, rest = body.partition(chr(10))
                if first.startswith("%%"):
                    lab, _, c = first[2:].partition("|")
                    label, cap, code = lab.strip(), c.strip(), rest
                # A block diagram is wider than a single column and becomes
                # illegible when shrunk to fit one, so it spans both.
                out.append(r"\begin{figure*}[!t]\centering"
                           r"\begin{adjustbox}{max width=0.85\textwidth, max totalheight=42mm}"
                           + chr(10) + code.strip() + chr(10)
                           + r"\end{adjustbox}" + chr(10)
                           + (r"\caption{%s}" % tex_inline(cap) if cap else "")
                           + chr(10)
                           + (r"\label{%s}" % label if label else "")
                           + chr(10) + r"\end{figure*}")
                continue

            # A figure fence names a PDF, a label key, and a caption:
            #   ```figure
            #   fig_arms.pdf | fig:arms | Per-arm mean rubric scores ...
            if lang == "figure":
                src, _, rest = body.strip().partition("|")
                key, _, cap = rest.partition("|")
                out.append(r"\begin{figure}[!t]\centering"
                           + r"\includegraphics[width=\columnwidth]{%s}"
                           % src.strip()
                           + chr(10) + r"\caption{%s}" % tex_inline(cap.strip())
                           + chr(10) + r"\label{%s}" % key.strip()
                           + chr(10) + r"\end{figure}")
                continue

            if lang == "figurewide":
                src, _, rest = body.strip().partition("|")
                key, _, cap = rest.partition("|")
                out.append(r"\begin{figure*}[!t]\centering"
                           + r"\includegraphics[width=0.40\textwidth]{%s}"
                           % src.strip()
                           + chr(10) + r"\caption{%s}" % tex_inline(cap.strip())
                           + chr(10) + r"\label{%s}" % key.strip()
                           + chr(10) + r"\end{figure*}")
                continue

            safe = fold_ascii(body)
            widest = max((len(l) for l in safe.splitlines()), default=0)
            if widest > 52:
                # A wide listing is code, not a figure. Let it wrap so it
                # cannot overflow the margin.
                out.append("\\begin{Verbatim}[fontsize=\\scriptsize,"
                           "breaklines=true,breakanywhere=true,"
                           "breaksymbolleft={},breaksymbolright={}]"
                           + chr(10) + safe + chr(10) + "\\end{Verbatim}")
            else:
                # A narrow block is a figure. Wrapping any of its lines
                # destroys the column alignment the reader is there for, and a
                # Verbatim may break across a page, which cuts the figure in
                # half. A minipage forbids both.
                out.append(r"\noindent\begin{minipage}{\dimexpr\columnwidth-3pt\relax}" + chr(10)
                           + "\\begin{Verbatim}[fontsize=\\scriptsize,"
                           "breaklines=false,breakanywhere=false,"
                           "breaksymbolleft={},breaksymbolright={}]"
                           + chr(10) + safe + chr(10) + "\\end{Verbatim}" + chr(10)
                           + r"\end{minipage}" + chr(10) + r"\par\medskip")
            continue

        if kind == "ul":
            out.append(r"\begin{itemize}\tightlist")
            for it in payload:
                out.append(r"  \item %s" % tex_inline(it))
            out.append(r"\end{itemize}")
            continue

        if kind == "ol":
            if in_refs:
                for it in payload:
                    ref_i += 1
                    out.append(r"\bibitem{ref%d} %s" % (ref_i, tex_inline(it)))
                continue
            out.append(r"\begin{enumerate}\tightlist")
            for it in payload:
                out.append(r"  \item %s" % tex_inline(it))
            out.append(r"\end{enumerate}")
            continue

        if kind == "table":
            header, rows = payload[0], payload[1]
            tkey, tcap = (payload[2], payload[3]) if len(payload) > 2 else ("", "")
            ncol = max([len(header)] + [len(r) for r in rows]) or 1
            env = "table*" if ncol > 4 else "table"
            width = r"\textwidth" if env == "table*" else r"\columnwidth"
            out.append(r"\begin{%s}[!t]\centering\footnotesize" % env)
            # max width shrinks an over-wide table but never enlarges a small
            # one; plain \resizebox would blow narrow tables up to full width.
            out.append(r"\begin{adjustbox}{max width=%s}" % width)
            out.append(r"\begin{tabular}{%s}" % ("l" * ncol))
            out.append(r"\toprule")
            out.append(" & ".join(tex_inline(h) for h in header) + r" \\")
            out.append(r"\midrule")
            for r in rows:
                cells = list(r) + [""] * (ncol - len(r))
                out.append(" & ".join(tex_inline(c) for c in cells) + r" \\")
            out.append(r"\bottomrule")
            out.append(r"\end{tabular}")
            out.append(r"\end{adjustbox}" + chr(10))
            if tcap:
                out.append(r"  \caption{%s}" % tex_inline(tcap) + chr(10))
            if tkey:
                out.append(r"  \label{%s}" % tkey + chr(10))
            out.append(r"\end{%s}" % env)
            continue

    if in_refs:
        out.append(r"\end{thebibliography}")
    if in_abstract:
        out.append(r"\end{abstract}")
    out.append(END)
    return "\n".join(out)


# ---------------------------------------------------------------------- DOCX
def emit_docx(blocks: list[tuple[str, object]], title: str, path: Path) -> None:
    import docx
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt, RGBColor

    doc = docx.Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(10)

    def add_rich(par, text, base_bold=False):
        for kind, val in docx_inline(text):
            if not val:
                continue
            run = par.add_run(val)
            run.italic = kind == "i"
            run.bold = base_bold or kind == "b"
            if kind == "c":
                run.font.name = "Courier New"
        return par

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(title)
    r.bold = True
    r.font.size = Pt(16)

    if ANON:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run("Anonymous submission")
        r.font.size = Pt(11)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run("Author and affiliation omitted for double-anonymous review")
        r.font.size = Pt(10)
    else:
        for name, dept, email in AUTHORS:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(name)
            r.bold = True
            r.font.size = Pt(11)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(f"{dept}\n{AFFILIATION}\n{email}")
            r.font.size = Pt(9.5)

    for kind, payload in blocks:
        if kind == "h":
            level, text = payload
            if level == 1:
                continue
            sizes = {2: 13, 3: 11.5, 4: 10.5}
            par = doc.add_paragraph()
            par.paragraph_format.space_before = Pt(10)
            par.paragraph_format.space_after = Pt(3)
            r = par.add_run(text)
            r.bold = True
            r.font.size = Pt(sizes.get(level, 10.5))
            continue

        if kind == "p":
            par = doc.add_paragraph()
            par.paragraph_format.space_after = Pt(6)
            add_rich(par, payload)
            continue

        if kind == "hr":
            continue

        if kind == "quote":
            par = doc.add_paragraph()
            par.paragraph_format.left_indent = Pt(24)
            par.paragraph_format.right_indent = Pt(24)
            add_rich(par, payload)
            for run in par.runs:
                run.italic = True
                run.font.size = Pt(9.5)
            continue

        if kind == "code":
            lang, body = payload
            if lang in ("figure", "figurewide"):
                src, _, rest = body.strip().partition("|")
                key, _, cap = rest.partition("|")
                img_path = PAPER / src.strip()
                if img_path.suffix.lower() == ".pdf":
                    png_cand = img_path.with_suffix(".png")
                    if png_cand.exists():
                        img_path = png_cand
                if img_path.exists():
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.space_before = Pt(6)
                    p.paragraph_format.space_after = Pt(2)
                    r = p.add_run()
                    width = 6.5 if lang == "figurewide" else 6.0
                    r.add_picture(str(img_path), width=Inches(width))
                    if cap.strip():
                        cap_p = doc.add_paragraph()
                        cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        cap_p.paragraph_format.space_after = Pt(6)
                        cap_r = cap_p.add_run(cap.strip())
                        cap_r.font.size = Pt(9.0)
                        cap_r.italic = True
                continue

            if lang == "tikz":
                cap = ""
                first, _, _ = body.partition(chr(10))
                if first.startswith("%%"):
                    _, _, c = first[2:].partition("|")
                    cap = c.strip()
                # Check for rendered architecture diagram PNG/image
                img_path = PAPER / "fig_architecture.png"
                if img_path.exists():
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.space_before = Pt(6)
                    p.paragraph_format.space_after = Pt(2)
                    r = p.add_run()
                    r.add_picture(str(img_path), width=Inches(6.0))
                    if cap:
                        cap_p = doc.add_paragraph()
                        cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        cap_p.paragraph_format.space_after = Pt(6)
                        cap_r = cap_p.add_run(cap)
                        cap_r.font.size = Pt(9.0)
                        cap_r.italic = True
                    continue

            for line in body.split("\n"):
                par = doc.add_paragraph()
                par.paragraph_format.space_after = Pt(0)
                r = par.add_run(line)
                r.font.name = "Consolas"
                r.font.size = Pt(8.5)
            continue

        if kind in ("ul", "ol"):
            style_name = "List Bullet" if kind == "ul" else "List Number"
            for it in payload:
                par = doc.add_paragraph(style=style_name)
                par.paragraph_format.space_after = Pt(2)
                add_rich(par, it)
            continue

        if kind == "table":
            header, rows = payload[0], payload[1]
            ncol = max([len(header)] + [len(r) for r in rows]) or 1
            tbl = doc.add_table(rows=len(rows) + 1, cols=ncol)
            tbl.style = "Table Grid"
            for c, h in enumerate(header):
                cell = tbl.cell(0, c)
                cell.text = ""
                # Table cells carry markdown too, so they go through the same
                # inline renderer as body text; otherwise ** markers survive
                # into the document.
                for kind_i, val_i in docx_inline(h):
                    run = cell.paragraphs[0].add_run(val_i)
                    run.bold = True
                    run.italic = kind_i == "i"
                    run.font.size = Pt(8.5)
            for ri, row in enumerate(rows, start=1):
                for c in range(ncol):
                    val = row[c] if c < len(row) else ""
                    cell = tbl.cell(ri, c)
                    cell.text = ""
                    for kind_i, val_i in docx_inline(val):
                        run = cell.paragraphs[0].add_run(val_i)
                        run.bold = kind_i == "b"
                        run.italic = kind_i == "i"
                        run.font.size = Pt(8.5)
            doc.add_paragraph()
            continue

    doc.save(path)


def build_one(stem: str) -> None:
    """Build <stem>.md -> <stem>.tex and <stem>.docx."""
    src = PAPER / f"{stem}.md"
    raw = src.read_text(encoding="utf-8")
    # The byline under the title is authored by hand in the markdown for the
    # benefit of anyone reading the source, but AUTHOR/AFFILIATION above are the
    # single source of truth for the rendered author block. Emitting both
    # printed the name twice, so the byline is dropped here.
    raw = re.sub(r"^\*.*(?:Hemadharsana|Sanjeev|Prajan).*\*\s*$", "", raw,
                 flags=re.MULTILINE)
    neutral = VENUE_LINE_RE.sub("", raw)
    neutral = re.sub(r"\n{3,}", "\n\n", neutral)

    blocks = parse_blocks(neutral)
    title = next((pl[1] for k, pl in blocks if k == "h" and pl[0] == 1),
                 "Untitled")
    title = re.sub(r"\*\*", "", title)

    suffix = "_ANON" if ANON else ""
    tex_out = PAPER / f"{stem}{suffix}.tex"
    docx_out = PAPER / f"{stem}{suffix}.docx"
    tex_out.write_text(emit_tex(blocks, title), encoding="utf-8")
    emit_docx(blocks, title, docx_out)

    print(f"  {stem}")
    print(f"    blocks : {len(blocks)}")
    print(f"    title  : {title[:64]}")
    print(f"    tex    : {tex_out.name} ({tex_out.stat().st_size:,} B)")
    print(f"    docx   : {docx_out.name} ({docx_out.stat().st_size:,} B)")


def main() -> None:
    global ANON
    if "--anon" in sys.argv:
        ANON = True
        sys.argv.remove("--anon")
    stems = [s.strip() for s in sys.argv[1:] if s.strip()] or [
        "MANUSCRIPT_SKILL_V2",
    ]
    for stem in stems:
        build_one(stem)


if __name__ == "__main__":
    main()
