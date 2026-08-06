# UI-REC3 Design QA

> **归档，非当前权威。** 本文件保存已完成的 UI-REC3 桌面文档库视觉验收；当前设计和测试门禁见 `docs/design-spec.md` 与 `docs/testing-strategy.md`。

- Source: `docs/assets/ui-visual-baseline/figma-desktop-library-1440x900.png`
- Implementation: `output/playwright/ui-rec3-final-library-1440x900.png`
- Combined comparison: `output/playwright/ui-rec3-library-comparison-1440x900.png`
- Viewport: 1440×900, browser zoom 100%
- State: deterministic temporary SQLite fixture with PDF, Markdown and archived Markdown documents; first PDF row selected.

## Comparison history

1. Initial implementation retained a stacked Gradio upload/filter form, a detached list heading, an exposed detail dropdown and a fully red lifecycle panel. The document rows were presentation-only.
2. The final implementation consolidates the title and upload actions, search/filter toolbar, compact selectable rows, selected state and the real document inspector. The lifecycle panel is neutral except for the destructive action.
3. The reference and implementation now share the same primary hierarchy: application shell, space navigation, independent document workspace, compact document list and selected-document inspector.

## Accepted equivalent differences

- The existing product uses a two-step “select file → start indexing” workflow, so the implementation retains both real controls instead of presenting the reference’s single upload action as a false one-step operation.
- Full `document_id`, hash and locator values are shown because they are explicit product requirements; the reference uses shortened illustrative values.
- The right inspector remains slightly wider than the reference because UI-REC2’s approved desktop session geometry must not be changed during this single-page stage.

## Checks

- Page scroll width/height equals 1440×900.
- Sidebar, main workspace and inspector have no sibling overlap.
- First row selection is visible and keyboard reachable; selecting another row updates the real Gradio detail state and inspector.
- Browser console: 0 errors, 0 warnings.
- 1024×768 and 390×844 have no horizontal overflow; mobile document details remain accessible through the existing context bottom sheet.

Final result: passed
