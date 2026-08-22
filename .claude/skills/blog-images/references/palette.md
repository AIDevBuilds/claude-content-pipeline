# Diagram Palette

**The values here are documentation. The source of truth is `brand.diagram` in
`config.json` at the repo root.** Read that file before writing an SVG and use the
values it holds; they may have been customised. This page explains what each token
is *for*, which JSON cannot.

There is a second palette, `brand.thumbnail`, used by the `video-thumbnail` skill.
The two are deliberately different: diagrams are read calmly at ~700px inline in an
article, thumbnails have to survive at ~320px in a YouTube sidebar. Do not
cross-apply them.

## Tokens and their jobs

| Token | Job |
|---|---|
| `canvas` | The diagram background. Everything sits on this. |
| `surface` | Default box fill. |
| `surfaceAlt` | Secondary box fill, for a second tier in a stack or the other side of a split. |
| `stroke` | Every hairline and box border. One width, one colour. |
| `textPrimary` | Labels and headings inside the diagram. |
| `textMuted` | Secondary annotations. If it needs to be read to understand the diagram, it is not muted. |
| `accentA` | The primary structure, "this is the thing the diagram is about". |
| `accentB` | The other half of a comparison or contrast. |
| `accentDanger` | A hard stop: something blocking, failing, or refusing. |
| `accentSuccess` | Something allowed or passing. |

**Never more than two accents active in one diagram.** Three accents means the
diagram is carrying more than one idea and should be split.

## Light variant
`brand.diagram.light` exists only for platforms that force a white card. Note that
`accentA` is a different, higher-contrast hex there: the dark-mode cyan does not
meet AA contrast on white. The other accents hold up as-is.

## Type
Use `brand.diagram.fontStack`. It is a system-font stack on purpose: cairosvg
renders it consistently without embedding font files, and an embedded font is a
dependency that quietly breaks on someone else's machine.

Two weights maximum per diagram: regular for labels, 600 for the one thing being
emphasised.

## Diagram rules
- Flat fills only. No gradients, drop shadows, or 3D effects — they add bytes and
  visual noise without adding information.
- One hairline stroke width per diagram (1.5px on a 1600px canvas scales cleanly).
- One corner radius per diagram (6 or 8px), held on every box.
- Generous whitespace over dense packing.
- If a diagram needs a legend, it is trying to show too much. Label directly.
