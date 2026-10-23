---
name: markitdown
description: Convert heterogeneous documents and selected URIs to Markdown with Microsoft MarkItDown for text analysis, search, and LLM/RAG ingestion. Covers safe local conversion, streams, Office/PDF/data formats, batch workflows, plugins, vision OCR, Azure extraction, and the official MCP server.
license: MIT
compatibility: Python 3.10+ and uv. Examples target MarkItDown 0.1.6. Core local conversion can run offline; URL, YouTube, audio transcription, LLM, Azure, and MCP workflows may use network or external services.
metadata:
  version: "2.1"
  skill-author: K-Dense Inc.
---

[ENGINEERING IMPLEMENTATION STANDARDS & ARCHITECTURAL CONSTRAINTS]

## Choose the Right Path
| Need | Recommended path |
|---|---|
| Trusted local PDF, Office, HTML, CSV, EPUB, or ZIP | Built-in converter with `convert_local()` |
| Uploaded bytes or an already-open file | `convert_stream()` with `StreamInfo` hints |
| Remote HTTP(S) input | Validate and fetch it yourself, then call `convert_response()` |
| Scanned PDF or text inside embedded images | Official `markitdown-ocr` vision plugin, Azure Document Intelligence, or Azure Content Understanding |
| Video, structured fields, or custom multimodal extraction | Azure Content Understanding |
| Local agent integration | Official `markitdown-mcp` server over STDIO or localhost |
| Bounding boxes, page coordinates, or screenshots | Use a layout-aware parser such as LiteParse instead |
| PDF merge/split/forms/watermarks | Use the `pdf` skill instead |
### Command line
```bash
# Convert a trusted local file
markitdown report.pdf -o report.md

# Write Markdown to stdout
markitdown manuscript.docx > manuscript.md

# Supply type information when reading bytes from stdin
markitdown < report.pdf -x .pdf -m application/pdf -o report.md
```

```bash
markitdown --list-plugins
markitdown --use-plugins document.pdf -o document.md
markitdown image.bin -x .png -m image/png -o image.md
markitdown page.html --keep-data-uris -o page.md
```

### Python: trusted local file
```python
from pathlib import Path

from markitdown import MarkItDown

source = Path("report.pdf")
destination = Path("report.md")

converter = MarkItDown()
result = converter.convert_local(source)
destination.write_text(result.markdown, encoding="utf-8")
```

### Python: binary stream
```python
from markitdown import MarkItDown, StreamInfo
converter = MarkItDown()
with open("report.pdf", "rb") as stream:
    result = converter.convert_stream(
        stream,
        stream_info=StreamInfo(
            extension=".pdf",
            mimetype="application/pdf",
            filename="report.pdf",
        ),
    )
print(result.markdown)
```

### 1. Use the narrowest conversion method
- `convert_local()` for local paths
- `convert_stream()` for controlled bytes
- `convert_response()` after an application-controlled HTTP fetch
- `convert_uri()` only for a trusted, validated `file:`, `data:`, `http:`, or `https:` URI
- `convert()` only when polymorphic dispatch is genuinely useful and the source is trusted
### 3. Separate local and external processing
- HTTP(S), Wikipedia, RSS, Bing, and YouTube conversion
- Built-in audio transcription, which uses Google Web Speech through `SpeechRecognition`
- LLM image descriptions and the `markitdown-ocr` plugin
- Azure Document Intelligence and Azure Content Understanding
### Batch-convert a directory
```bash
python scripts/batch_convert.py documents/ markdown/ \
  --recursive \
  --extensions .pdf .docx .pptx .xlsx \
  --manifest markdown/manifest.json
```

### Convert a literature collection
```bash
python scripts/convert_literature.py papers/ literature-markdown/ \
  --recursive \
  --create-index
```

## OCR and Cloud Extraction
- **`markitdown-ocr==0.1.0`**: official plugin using a vision-capable, OpenAI-compatible client for PDF/DOCX/PPTX/XLSX images and scanned-PDF fallback.
- **Azure Document Intelligence**: cloud layout/OCR for documents and images.
- **Azure Content Understanding**: cloud multimodal analysis, structured fields in YAML front matter, custom analyzers, audio, and video.
## MCP Server
```bash
uv pip install "markitdown==0.1.6" "markitdown-mcp==0.0.1a4"
markitdown-mcp
```

## Quality Checks
- Confirm the output is non-empty and UTF-8.
- Compare headings, lists, links, tables, equations, notes, and sheet boundaries with the source.
- Visually inspect figures, charts, scanned pages, and multi-column layouts.
- Record the source path/URI, package version, conversion mode, plugin/cloud service, and failures.
- Keep the original document as the authoritative artifact.
## Troubleshooting
| Problem | Likely fix |
|---|---|
| `MissingDependencyException` | Install the matching pinned extra, or `[all]` |
| `UnsupportedFormatException` | Add `StreamInfo`/CLI hints, install the needed extra, or use a plugin/another parser |
| Empty image output | Install ExifTool for metadata or configure an approved vision client |
| Scanned PDF has little text | Use `markitdown-ocr`, Document Intelligence, or Content Understanding |
| `text_content` warning or old example | Replace it with `result.markdown` |
| Plugin is not used | Confirm `markitdown --list-plugins`, then enable plugins explicitly |
| Large memory usage | Avoid huge `data:` URIs and non-seekable streams; split inputs or use bounded preprocessing |
| Remote URI risk | Validate scheme, destination, redirects, size, and timeout before `convert_response()` |
| Windows console character loss | Prefer `-o output.md`, which writes UTF-8 |
## Reference Files
| File | Read when |
|---|---|
| `references/api_reference.md` | Python classes, result object, conversion methods, CLI flags, exceptions |
| `references/file_formats.md` | Exact built-in formats, extras, behavior, and limitations |
| `references/cloud_and_ocr.md` | Vision descriptions, OCR plugin, Azure services, credentials, and data flow |
| `references/mcp_and_plugins.md` | MCP transports/security and custom plugin authoring |
| `references/security.md` | Trust boundaries, URI/SSRF controls, archives, plugins, prompt injection |
| `references/workflows.md` | Batch, literature, RAG, streams, and validation recipes |
| `references/migration.md` | Changes from 0.0.x through 0.1.6 and stale-pattern replacements |
## Authoritative Sources
- Project and current user guide: https://github.com/microsoft/markitdown
- Release 0.1.6: https://github.com/microsoft/markitdown/releases/tag/v0.1.6
- PyPI: https://pypi.org/project/markitdown/
- Official OCR plugin: https://github.com/microsoft/markitdown/tree/v0.1.6/packages/markitdown-ocr
- Official MCP server: https://github.com/microsoft/markitdown/tree/v0.1.6/packages/markitdown-mcp
- Official sample plugin: https://github.com/microsoft/markitdown/tree/v0.1.6/packages/markitdown-sample-plugin
