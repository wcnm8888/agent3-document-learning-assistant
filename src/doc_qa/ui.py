from __future__ import annotations

import os
import re
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import gradio as gr

from .config import Settings
from .deepseek import DeepSeekChatProvider
from .document_catalog import DocumentCatalogService
from .document_scope import DocumentScopeState
from .embedding import DashScopeEmbeddingProvider
from .ingestion import DocumentIngestionService
from .learning import LearningService
from .lifecycle import DocumentLifecycleService
from .memory_store import SQLiteMemoryStore
from .models import IndexReport
from .qdrant_index import QdrantIndexer
from .qa import QuestionAnswerService


SUPPORTED_DOCUMENT_SUFFIXES = {".pdf", ".md", ".markdown"}

APP_CSS = """
:root {
  --docqa-bg: #000000;
  --docqa-surface: #18181b;
  --docqa-surface-raised: #202023;
  --docqa-surface-float: #27282a;
  --docqa-border: #3f3f46;
  --docqa-border-subtle: #27282a;
  --docqa-ink: #ffffff;
  --docqa-muted: #a1a1a9;
  --docqa-faint: #717179;
  --docqa-accent: #2f80ed;
  --docqa-accent-hover: #2563eb;
  --docqa-success: #22c55e;
  --docqa-danger: #ef4444;
  --docqa-warn: #f59e0b;
  --docqa-radius-panel: 10px;
  --docqa-radius-control: 8px;
}

* { box-sizing: border-box; }
body, .gradio-container {
  background: var(--docqa-bg) !important;
  color: var(--docqa-ink) !important;
  font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif !important;
}
footer { display: none !important; }
main.app { max-width: none !important; padding: 0 !important; }
.gradio-container { max-width: none !important; padding: 0 !important; }
#docqa-shell {
  width: 100%; max-width: 1600px; margin: 0 auto; padding: 0 24px 24px;
  color: var(--docqa-ink);
}
#docqa-shell .docqa-topbar {
  min-height: 76px; align-items: center; gap: 20px;
  padding: 0 4px; border-bottom: 1px solid var(--docqa-border-subtle);
  margin-bottom: 20px;
}
#docqa-shell .docqa-brand {
  align-items: center; gap: 12px;
}
#docqa-shell .docqa-brand-mark {
  width: 30px !important; min-width: 30px !important; flex: 0 0 30px !important;
  height: 30px; display: flex; align-items: center; justify-content: center;
  border-radius: 8px; background: var(--docqa-accent); color: #ffffff;
  font-size: 16px; font-weight: 700;
}
#docqa-shell .docqa-brand-mark p { color: #ffffff !important; text-align: center; }
#docqa-shell .docqa-brand-copy { gap: 2px; }
#docqa-shell .docqa-topbar-meta {
  align-items: center; justify-content: end; gap: 12px;
}
#docqa-shell .docqa-space-label {
  color: var(--docqa-muted); font-size: 12px; line-height: 18px;
}
#docqa-shell .docqa-topbar-divider {
  width: 1px; min-height: 24px; background: var(--docqa-border-subtle);
}
#docqa-shell .docqa-title {
  margin: 0; color: var(--docqa-ink); font-size: 20px; line-height: 28px; font-weight: 700;
}
#docqa-shell .docqa-kicker {
  color: var(--docqa-faint); font-size: 12px; line-height: 18px; letter-spacing: .01em;
}
#docqa-shell .docqa-header-meta {
  color: var(--docqa-muted); font-size: 12px; text-align: right; line-height: 18px;
}
#docqa-shell h1,
#docqa-shell h2,
#docqa-shell h3,
#docqa-shell h4,
#docqa-shell p,
#docqa-shell .prose,
#docqa-shell .prose p,
#docqa-shell .prose h1,
#docqa-shell .prose h2,
#docqa-shell .prose h3,
#docqa-shell .prose h4 { color: var(--docqa-ink) !important; }
#docqa-shell .docqa-title .prose p {
  margin: 0 !important; font-size: 20px !important; line-height: 28px !important; font-weight: 700 !important;
}
#docqa-shell .docqa-kicker .prose p,
#docqa-shell .docqa-header-meta .prose p,
#docqa-shell .docqa-space-label .prose p,
#docqa-shell .docqa-session-meta .prose p,
#docqa-shell .docqa-library-count .prose p {
  margin: 0 !important; font-size: 12px !important; line-height: 18px !important; font-weight: 400 !important;
  color: var(--docqa-muted) !important;
}
#docqa-shell .docqa-section-kicker .prose p,
#docqa-shell .docqa-mobile-note .prose p {
  margin: 0 !important; font-size: 11px !important; line-height: 17px !important; font-weight: 500 !important;
  color: var(--docqa-faint) !important;
}
#docqa-shell .docqa-status .prose p {
  margin: 0 !important; font-size: 12px !important; line-height: 18px !important; font-weight: 400 !important;
  color: var(--docqa-muted) !important;
}
#docqa-shell .docqa-kicker p,
#docqa-shell .docqa-header-meta p,
#docqa-shell .docqa-space-label p,
#docqa-shell .docqa-section-kicker p,
#docqa-shell .docqa-status p,
#docqa-shell .docqa-mobile-note p,
#docqa-shell .docqa-session-meta p,
#docqa-shell .docqa-library-count p,
#docqa-shell .docqa-source-summary p { color: inherit; }
#docqa-shell .docqa-kicker p,
#docqa-shell .docqa-header-meta p,
#docqa-shell .docqa-space-label p,
#docqa-shell .docqa-session-meta p,
#docqa-shell .docqa-library-count p { color: var(--docqa-muted); }
#docqa-shell .docqa-section-kicker p,
#docqa-shell .docqa-mobile-note p { color: var(--docqa-faint); }
#docqa-shell .docqa-status p { color: var(--docqa-muted); }
#docqa-workspace {
  display: grid !important;
  grid-template-columns: 292px minmax(0, 1fr) 340px;
  gap: 16px; align-items: start;
}
#docqa-workspace > .gr-column { min-width: 0 !important; }
#docqa-shell .docqa-sidebar,
#docqa-shell .docqa-main-panel,
#docqa-shell .docqa-inspector {
  min-width: 0; padding: 16px; background: var(--docqa-surface);
  border: 1px solid var(--docqa-border-subtle); border-radius: var(--docqa-radius-panel);
  box-shadow: 0 14px 30px rgba(0, 0, 0, .18);
}
#docqa-shell .docqa-sidebar {
  background: #0f0f11; padding: 12px;
}
#docqa-shell .docqa-main-panel {
  min-height: 720px; padding: 18px;
}
#docqa-shell .docqa-inspector {
  padding: 0; overflow: hidden;
}
#docqa-shell .docqa-panel-title {
  align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 12px;
}
#docqa-shell .docqa-panel-title h3,
#docqa-shell .docqa-panel-title h4 { margin: 0; }
#docqa-shell .docqa-panel h3 {
  color: var(--docqa-ink); font-size: 16px; line-height: 24px; font-weight: 650;
}
#docqa-shell .docqa-panel h4 {
  color: var(--docqa-muted); font-size: 12px; line-height: 18px; font-weight: 600;
}
#docqa-shell .docqa-section-kicker {
  margin: 2px 0 8px; color: var(--docqa-faint); font-size: 10px;
  letter-spacing: .12em; text-transform: uppercase;
}
#docqa-shell .docqa-nav {
  gap: 4px; padding-bottom: 14px; margin-bottom: 14px;
  border-bottom: 1px solid var(--docqa-border-subtle);
}
#docqa-shell .docqa-nav-item {
  min-height: 36px; justify-content: start; padding: 0 10px;
  background: transparent !important; border: 1px solid transparent !important;
  color: var(--docqa-muted) !important; text-align: left;
}
#docqa-shell .docqa-nav-item:first-child {
  background: rgba(47, 128, 237, .14) !important;
  border-color: rgba(47, 128, 237, .32) !important;
  color: var(--docqa-ink) !important;
}
#docqa-shell .docqa-library-head {
  align-items: center; justify-content: space-between; margin-bottom: 10px;
}
#docqa-shell .docqa-library-head h3 { font-size: 14px; }
#docqa-shell .docqa-library-count {
  color: var(--docqa-faint); font-size: 11px; line-height: 16px;
}
#docqa-shell .docqa-status {
  min-height: 40px; padding: 9px 11px; background: var(--docqa-surface-raised);
  border: 1px solid var(--docqa-border-subtle); border-radius: var(--docqa-radius-control);
  color: var(--docqa-muted); font-size: 12px; line-height: 18px;
}
#docqa-shell .docqa-scope {
  border-left: 3px solid var(--docqa-accent); color: var(--docqa-ink);
}
#docqa-shell .docqa-mobile-note {
  color: var(--docqa-faint); font-size: 11px; line-height: 17px;
}
#docqa-shell .docqa-source-summary { font-size: 13px; line-height: 20px; }
#docqa-shell .docqa-source-summary code {
  white-space: normal; overflow-wrap: anywhere; color: var(--docqa-muted);
}
#docqa-shell .docqa-sidebar .gr-box,
#docqa-shell .docqa-sidebar .gr-input,
#docqa-shell .docqa-sidebar .gr-form,
#docqa-shell .docqa-sidebar .gr-panel,
#docqa-shell .docqa-main-panel textarea,
#docqa-shell .docqa-main-panel input,
#docqa-shell .docqa-inspector textarea,
#docqa-shell .docqa-inspector input,
#docqa-shell button:not(.primary):not(.stop) {
  background: var(--docqa-surface-raised) !important;
  border-color: var(--docqa-border) !important;
  color: var(--docqa-ink) !important;
}
#docqa-shell textarea::placeholder,
#docqa-shell input::placeholder { color: var(--docqa-faint) !important; }
#docqa-shell button {
  min-height: 38px; border-radius: var(--docqa-radius-control) !important;
  font-size: 13px !important; font-weight: 600 !important;
}
#docqa-shell button.primary,
#docqa-shell .gr-button-primary {
  background: var(--docqa-accent) !important; border-color: var(--docqa-accent) !important;
  color: #ffffff !important;
}
#docqa-shell button.primary:hover,
#docqa-shell .gr-button-primary:hover {
  background: var(--docqa-accent-hover) !important; border-color: var(--docqa-accent-hover) !important;
}
#docqa-shell button.stop,
#docqa-shell .gr-button-stop {
  background: rgba(239, 68, 68, .12) !important; border-color: rgba(239, 68, 68, .5) !important;
  color: #fca5a5 !important;
}
#docqa-shell button:focus-visible,
#docqa-shell input:focus-visible,
#docqa-shell textarea:focus-visible,
#docqa-shell select:focus-visible,
#docqa-shell [role="combobox"]:focus-visible {
  outline: 2px solid var(--docqa-accent) !important; outline-offset: 2px;
}
#docqa-shell button:disabled,
#docqa-shell input:disabled,
#docqa-shell textarea:disabled,
#docqa-shell select:disabled,
#docqa-shell [aria-disabled="true"] {
  opacity: .55 !important; cursor: not-allowed !important;
}
#docqa-shell .label,
#docqa-shell label { color: var(--docqa-muted) !important; }
#docqa-shell textarea, #docqa-shell input { font-size: 14px !important; }
#docqa-shell .gr-chatbot {
  min-height: 470px; border: 1px solid var(--docqa-border-subtle) !important;
  border-radius: var(--docqa-radius-panel) !important;
}
#docqa-shell .docqa-composer {
  margin-top: 12px; padding: 10px; background: var(--docqa-surface-raised);
  border: 1px solid var(--docqa-border); border-radius: var(--docqa-radius-panel);
}
#docqa-shell .docqa-composer textarea { background: transparent !important; border: 0 !important; }
#docqa-shell .docqa-composer-actions { align-items: center; gap: 8px; }
#docqa-shell .docqa-composer-actions button { min-height: 36px; }
#docqa-shell .docqa-session-head { align-items: center; margin-bottom: 14px; }
#docqa-shell .docqa-session-head h3 { margin: 0; }
#docqa-shell .docqa-session-meta { color: var(--docqa-faint); font-size: 11px; }
#docqa-shell .docqa-inspector-head {
  padding: 14px 16px 0; border-bottom: 1px solid var(--docqa-border-subtle);
}
#docqa-shell .docqa-inspector-head h3 { margin: 0 0 12px; }
#docqa-shell .docqa-inspector .tabs { background: var(--docqa-surface) !important; }
#docqa-shell .docqa-inspector .tab-nav { padding: 0 16px; border-bottom: 1px solid var(--docqa-border-subtle); }
#docqa-shell .docqa-inspector .tab-nav button { min-height: 38px; color: var(--docqa-muted) !important; }
#docqa-shell .docqa-inspector .tab-nav button.selected {
  color: var(--docqa-ink) !important; border-bottom-color: var(--docqa-accent) !important;
}
#docqa-shell .docqa-inspector .tabitem { padding: 14px 16px 16px; }
#docqa-shell .docqa-accordion {
  margin-top: 12px; background: var(--docqa-surface-raised) !important;
  border: 1px solid var(--docqa-border-subtle) !important; border-radius: var(--docqa-radius-control) !important;
}
#docqa-shell .docqa-document-table { min-width: 0; }
#docqa-shell .docqa-document-table .table-wrap {
  overflow: hidden !important; border: 1px solid var(--docqa-border-subtle);
  border-radius: var(--docqa-radius-control);
}
#docqa-shell .docqa-document-table table { width: 100% !important; table-layout: fixed; }
#docqa-shell .docqa-document-table th,
#docqa-shell .docqa-document-table td {
  color: var(--docqa-ink) !important; border-color: var(--docqa-border-subtle) !important;
  overflow-wrap: anywhere; word-break: normal; vertical-align: top;
}
#docqa-shell .docqa-document-table th { background: var(--docqa-surface-float) !important; color: var(--docqa-muted) !important; }
#docqa-shell .docqa-panel .table-container,
#docqa-shell .docqa-panel .table-wrap,
#docqa-shell .docqa-panel table { background: var(--docqa-surface) !important; }
#docqa-shell .docqa-panel table thead tr,
#docqa-shell .docqa-panel table thead th { background: var(--docqa-surface-float) !important; }
#docqa-shell .docqa-panel table tbody tr { background: var(--docqa-surface) !important; }
#docqa-shell .docqa-panel table tbody tr:nth-child(odd) { background: var(--docqa-surface-raised) !important; }
#docqa-shell .docqa-panel table tbody td { background: transparent !important; }
#docqa-shell .docqa-document-detail { max-height: 300px; overflow: auto; }
#docqa-shell .docqa-document-detail pre,
#docqa-shell .docqa-document-detail code { white-space: pre-wrap; overflow-wrap: anywhere; }
#docqa-shell .docqa-actions-row { gap: 8px; flex-wrap: wrap; }
#docqa-shell .docqa-filter-row { gap: 8px; align-items: end; }
#docqa-shell .docqa-sidebar .gr-accordion,
#docqa-shell .docqa-inspector .gr-json,
#docqa-shell .docqa-sidebar .gr-json {
  background: var(--docqa-surface-raised) !important; border-color: var(--docqa-border) !important;
  color: var(--docqa-ink) !important;
}
#docqa-shell .docqa-sidebar .block,
#docqa-shell .docqa-sidebar .block > .wrap,
#docqa-shell .docqa-main-panel .block,
#docqa-shell .docqa-main-panel .block > .wrap,
#docqa-shell .docqa-inspector .block,
#docqa-shell .docqa-inspector .block > .wrap {
  background: var(--docqa-surface) !important; color: var(--docqa-ink) !important;
  border-color: var(--docqa-border-subtle) !important;
}

@media (max-width: 1100px) {
  #docqa-shell { padding: 0 16px 16px; }
  #docqa-workspace { grid-template-columns: 200px minmax(0, 1fr) 280px; gap: 12px; }
  #docqa-shell .docqa-sidebar,
  #docqa-shell .docqa-main-panel,
  #docqa-shell .docqa-inspector { padding: 12px; }
  #docqa-shell .gr-chatbot { min-height: 390px; }
  #docqa-shell .docqa-title { font-size: 18px; }
}
@media (max-width: 760px) {
  #docqa-shell { width: 100% !important; max-width: none !important; margin: 0 !important; padding: 0 10px 12px; }
  #docqa-shell .docqa-topbar { min-height: 64px; align-items: start; padding-top: 12px; margin-bottom: 12px; }
  #docqa-shell .docqa-topbar-meta { display: none !important; }
  #docqa-shell .docqa-header-meta { text-align: left; }
  #docqa-workspace { display: flex !important; flex-direction: column; gap: 12px; }
  #docqa-workspace > .gr-column { width: 100% !important; margin-bottom: 0; }
  #docqa-shell .docqa-sidebar,
  #docqa-shell .docqa-main-panel,
  #docqa-shell .docqa-inspector { padding: 12px; }
  #docqa-shell .docqa-sidebar { order: 1; }
  #docqa-shell .docqa-main-panel { order: 2; min-height: 0; }
  #docqa-shell .docqa-inspector { order: 3; }
  #docqa-shell .gr-chatbot { min-height: 330px; }
  #docqa-shell .docqa-document-table .table-wrap { overflow-x: hidden !important; }
  #docqa-shell .docqa-document-table table { min-width: 0 !important; }
  #docqa-shell .docqa-filter-row { display: grid !important; grid-template-columns: 1fr 1fr; }
  #docqa-shell .docqa-filter-row > *:first-child { grid-column: 1 / -1; }
  #docqa-shell .docqa-actions-row { display: grid !important; grid-template-columns: 1fr 1fr; }
  #docqa-shell .docqa-actions-row > * { width: 100% !important; }
  #docqa-shell .docqa-title { font-size: 20px; }
  #docqa-shell .docqa-mobile-note { margin-top: 4px; }
}

/* HF-R1 layout authority: one workbench owns the desktop geometry and breakpoints. */
#docqa-shell {
  max-width: 1440px;
  padding: 0 24px 48px;
}
#docqa-shell .docqa-topbar {
  min-height: 76px;
  padding: 0;
  margin-bottom: 16px;
}
#docqa-workspace {
  grid-template-columns: 216px minmax(0, 760px) 368px !important;
  justify-content: center;
  column-gap: 24px !important;
  row-gap: 24px !important;
  align-items: start !important;
}
#docqa-shell .docqa-sidebar,
#docqa-shell .docqa-main-panel,
#docqa-shell .docqa-inspector,
#docqa-shell .docqa-library-view,
#docqa-shell .docqa-session-view {
  border-radius: 16px;
}
#docqa-shell .docqa-sidebar {
  min-height: 760px;
  padding: 14px 10px;
  background: #101012;
  border-color: #222226;
}
#docqa-shell .docqa-main-region {
  min-width: 0;
  display: flex;
  flex-direction: column;
}
#docqa-shell .docqa-library-view > .styler,
#docqa-shell .docqa-session-view > .styler,
#docqa-shell .docqa-inspector > .styler,
#docqa-shell .docqa-library-view .form,
#docqa-shell .docqa-session-view .form,
#docqa-shell .docqa-inspector .form {
  background: transparent !important;
}
#docqa-shell .docqa-library-view .block,
#docqa-shell .docqa-session-view .block,
#docqa-shell .docqa-inspector .block {
  background: transparent !important;
  border-color: transparent !important;
}
#docqa-shell .docqa-library-view .gr-box,
#docqa-shell .docqa-session-view .gr-box,
#docqa-shell .docqa-inspector .gr-box {
  background: #18181b !important;
  border-color: #2c2c31 !important;
}
#docqa-shell .docqa-library-view .gr-input,
#docqa-shell .docqa-session-view .gr-input,
#docqa-shell .docqa-inspector .gr-input,
#docqa-shell .docqa-library-view .input-container,
#docqa-shell .docqa-session-view .input-container,
#docqa-shell .docqa-inspector .input-container {
  background: #18181b !important;
  color: #ffffff !important;
}
#docqa-shell .docqa-library-view textarea,
#docqa-shell .docqa-library-view input,
#docqa-shell .docqa-session-scope textarea,
#docqa-shell .docqa-session-scope input,
#docqa-shell .docqa-inspector textarea,
#docqa-shell .docqa-inspector input {
  background: #18181b !important;
  color: #ffffff !important;
}
#docqa-shell .docqa-library-view .docqa-library-upload,
#docqa-shell .docqa-session-view .docqa-session-scope,
#docqa-shell .docqa-session-view .docqa-composer,
#docqa-shell .docqa-inspector .docqa-notes-card {
  background: #18181b !important;
}
#docqa-shell .docqa-library-view .docqa-library-upload .block,
#docqa-shell .docqa-session-view .docqa-session-scope .block,
#docqa-shell .docqa-session-view .docqa-composer .block,
#docqa-shell .docqa-inspector .docqa-notes-card .block {
  background: transparent !important;
}
#docqa-shell .docqa-library-view,
#docqa-shell .docqa-session-view {
  min-width: 0;
  min-height: 760px;
  padding: 18px;
  background: #0f0f11;
  border: 1px solid #222226;
  box-shadow: 0 16px 40px rgba(0, 0, 0, .2);
}
#docqa-shell .docqa-inspector {
  min-height: 760px;
  background: #101012;
  border-color: #222226;
  flex-flow: column nowrap !important;
}
#docqa-shell .docqa-space-nav {
  gap: 4px;
  padding: 8px 0 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid #252529;
}
#docqa-shell .docqa-nav-item {
  min-height: 40px;
  border-radius: 12px !important;
  text-align: left;
  justify-content: flex-start;
  padding: 0 12px;
}
#docqa-shell .docqa-nav-item:first-child {
  background: #242429 !important;
  border-color: #3f3f46 !important;
}
#docqa-shell .docqa-recent-title {
  margin: 0 6px 8px;
  color: #a1a1a9;
  font-size: 12px;
  letter-spacing: .01em;
}
#docqa-shell .docqa-recent-table {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}
#docqa-shell .docqa-recent-table thead {
  display: none !important;
}
#docqa-shell .docqa-recent-table tbody tr {
  background: transparent !important;
  border: 0 !important;
}
#docqa-shell .docqa-recent-table td {
  padding: 8px 6px !important;
  color: #717179 !important;
  font-size: 11px !important;
  border: 0 !important;
}
#docqa-shell .docqa-recent-table td:first-child {
  color: #a1a1a9 !important;
  max-width: 160px;
  overflow-wrap: anywhere;
}
#docqa-shell .docqa-library-header,
#docqa-shell .docqa-session-header,
#docqa-shell .docqa-inspector-header {
  align-items: flex-start;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid #252529;
}
#docqa-shell .docqa-eyebrow {
  margin-bottom: 6px;
  color: #717179;
  font-size: 10px;
  letter-spacing: .12em;
  text-transform: uppercase;
}
#docqa-shell .docqa-hero-title {
  margin: 0;
  color: #ffffff;
  font-size: 24px;
  line-height: 32px;
  font-weight: 700;
}
#docqa-shell .docqa-hero-copy {
  margin-top: 4px;
  color: #a1a1a9;
  font-size: 12px;
  line-height: 18px;
}
#docqa-shell .docqa-chip-row {
  align-items: center;
  gap: 6px;
  margin-top: 12px;
}
#docqa-shell .docqa-chip {
  min-height: 24px;
  padding: 3px 9px;
  border: 1px solid #3f3f46;
  border-radius: 999px;
  background: #18181b;
  color: #a1a1a9;
  font-size: 11px;
}
#docqa-shell .docqa-chip-success {
  border-color: rgba(34, 197, 94, .45);
  background: rgba(34, 197, 94, .12);
  color: #86efac;
}
#docqa-shell .docqa-header-action {
  min-width: 96px;
  margin-left: auto;
  background: #2f80ed !important;
  color: #ffffff !important;
}
#docqa-shell .docqa-library-toolbar {
  align-items: end;
  gap: 8px;
  margin: 16px 0 12px;
}
#docqa-shell .docqa-library-toolbar > * {
  min-width: 0 !important;
}
#docqa-shell .docqa-library-search { flex: 2 1 250px; }
#docqa-shell .docqa-library-filter { flex: 1 1 130px; }
#docqa-shell .docqa-library-upload {
  margin: 14px 0;
  padding: 12px;
  border: 1px solid #2c2c31;
  border-radius: 12px;
  background: #18181b;
}
#docqa-shell .docqa-library-upload .docqa-status {
  margin-top: 8px;
}
#docqa-shell .docqa-document-table {
  margin-top: 12px;
  border: 1px solid #2c2c31 !important;
  border-radius: 12px !important;
  overflow: hidden;
  background: #18181b !important;
}
#docqa-shell .docqa-document-table thead th {
  background: #27272a !important;
  color: #a1a1a9 !important;
  font-size: 11px !important;
  font-weight: 600 !important;
}
#docqa-shell .docqa-document-table tbody td {
  background: #18181b !important;
  color: #e4e4e7 !important;
  font-size: 12px !important;
  border-color: #2c2c31 !important;
  vertical-align: top;
}
#docqa-shell .docqa-document-table tbody tr:hover td {
  background: #202023 !important;
}
#docqa-shell .docqa-empty-library {
  margin-top: 12px;
  padding: 32px 20px;
  border: 1px dashed #3f3f46;
  border-radius: 12px;
  color: #a1a1a9;
  text-align: center;
}
#docqa-shell .docqa-session-header {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) 158px;
  grid-template-areas:
    "intro action"
    "status action";
  gap: 12px 18px;
  align-items: start !important;
  height: auto !important;
  min-height: 0 !important;
  padding-bottom: 16px;
}
#docqa-shell .docqa-session-header > .column:first-child {
  grid-area: intro;
  min-width: 0 !important;
  width: auto !important;
}
#docqa-shell .docqa-session-status {
  grid-area: status;
  width: auto !important;
  max-width: 100% !important;
  min-width: 0 !important;
  margin-left: 0 !important;
  align-self: start;
  overflow: hidden;
}
#docqa-shell .docqa-session-header > .docqa-header-action {
  grid-area: action;
  width: 158px !important;
  min-width: 0 !important;
  margin: 0 !important;
  align-self: start;
}
#docqa-shell .docqa-session-scope {
  margin: 14px 0;
  padding: 10px 12px;
  border: 1px solid #2c2c31;
  border-radius: 12px;
  background: #18181b;
}
#docqa-shell .docqa-session-workspace {
  display: flex !important;
  flex: 1 1 auto;
  flex-direction: column;
  min-height: 0 !important;
}
#docqa-shell .docqa-session-workspace > .styler,
#docqa-shell .docqa-session-workspace > .form {
  display: flex !important;
  flex: 1 1 auto;
  flex-direction: column;
  min-height: 0 !important;
}
#docqa-shell .docqa-session-view {
  display: flex !important;
  flex-direction: column;
  height: auto !important;
}
#docqa-shell .docqa-session-workspace .docqa-chatbot {
  flex: 1 1 auto;
}
#docqa-shell .docqa-session-scope .gr-dropdown,
#docqa-shell .docqa-session-scope .gr-form {
  border: 0 !important;
  background: transparent !important;
}
#docqa-shell .docqa-chatbot {
  min-height: 490px !important;
  height: auto !important;
  margin: 12px 0 16px;
  border: 0 !important;
  background: #0f0f11 !important;
}
#docqa-shell .docqa-chatbot .message {
  max-width: 88%;
  margin: 10px 0;
  padding: 12px 14px;
  border: 1px solid #2c2c31;
  border-radius: 16px;
  color: #e4e4e7;
  line-height: 1.6;
}
#docqa-shell .docqa-chatbot .message.user,
#docqa-shell .docqa-chatbot [data-testid="user"] {
  margin-left: auto;
  border-color: #2f80ed;
  background: #2f80ed;
  color: #ffffff;
}
#docqa-shell .docqa-chatbot .message.bot,
#docqa-shell .docqa-chatbot [data-testid="bot"] {
  background: #27282a;
}
#docqa-shell .docqa-composer {
  padding: 12px;
  border: 1px solid #3f3f46;
  border-radius: 16px;
  background: rgba(24, 24, 27, .92);
  box-shadow: 0 -12px 30px rgba(0, 0, 0, .18);
  position: relative;
  z-index: 1;
  clear: both;
  margin-top: 0 !important;
}
#docqa-shell .docqa-composer textarea {
  min-height: 70px !important;
  border: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  font-size: 14px !important;
}
#docqa-shell .docqa-composer-actions {
  align-items: center;
  gap: 8px;
}
#docqa-shell .docqa-composer-actions .docqa-composer-hint {
  margin-right: auto;
}
#docqa-shell .docqa-composer-actions .primary {
  min-width: 110px;
  border-radius: 999px !important;
}
#docqa-shell .docqa-inspector-header {
  padding: 18px 16px 14px;
  flex: 0 0 auto !important;
  height: auto !important;
}
#docqa-shell .docqa-context-tabs .tab-container.visually-hidden {
  display: none !important;
}
#docqa-shell .docqa-context-tabs .tab-container[role="tablist"] {
  display: flex !important;
  width: 100% !important;
  max-width: 100% !important;
  min-width: 0 !important;
}
#docqa-shell .docqa-context-tabs .tab-container[role="tablist"] button {
  flex: 0 0 auto;
  min-width: 72px;
}
#docqa-shell .docqa-inspector-body {
  padding: 0 16px 16px;
  flex: 0 0 auto !important;
  height: auto !important;
}
#docqa-shell .docqa-session-scope .wrap,
#docqa-shell .docqa-library-toolbar .wrap {
  background: #18181b !important;
  border-color: #3f3f46 !important;
  color: #ffffff !important;
}
#docqa-shell .docqa-session-scope .wrap input,
#docqa-shell .docqa-library-toolbar .wrap input {
  color: #ffffff !important;
}
#docqa-shell .docqa-chatbot > label {
  background: transparent !important;
  color: #717179 !important;
  border: 0 !important;
}
#docqa-shell .docqa-context-tabs {
  margin-top: 12px;
}
#docqa-shell .docqa-context-tabs .tab-nav {
  border-bottom: 1px solid #3f3f46;
}
#docqa-shell .docqa-context-tabs .tab-nav button {
  min-height: 34px;
  border-radius: 8px 8px 0 0 !important;
  color: #a1a1a9 !important;
}
#docqa-shell .docqa-context-tabs .tab-nav button.selected {
  color: #ffffff !important;
  border-bottom: 2px solid #2f80ed !important;
}
#docqa-shell .docqa-source-summary {
  padding: 4px 0;
}
#docqa-shell .docqa-source-summary ul {
  display: grid;
  gap: 8px;
  padding-left: 0;
  list-style: none;
}
#docqa-shell .docqa-source-summary li {
  padding: 11px 12px;
  border: 1px solid #2c2c31;
  border-radius: 12px;
  background: #202023;
  color: #d4d4d8;
  font-size: 12px;
  line-height: 18px;
}
#docqa-shell .docqa-source-summary code {
  display: block;
  margin-top: 4px;
  color: #a1a1a9;
}
#docqa-shell .docqa-raw-source {
  margin-top: 10px;
}
#docqa-shell .docqa-notes-card {
  padding: 12px;
  border: 1px solid #2c2c31;
  border-radius: 12px;
  background: #202023;
}
#docqa-shell .docqa-detail-card {
  margin-top: 12px;
  border-top: 1px solid #252529;
  padding-top: 12px;
}
#docqa-shell .docqa-danger-zone {
  margin-top: 12px;
  padding: 10px;
  border: 1px solid rgba(239, 68, 68, .35);
  border-radius: 12px;
  background: rgba(239, 68, 68, .06);
}
#docqa-shell .docqa-danger-zone .stop {
  color: #fca5a5 !important;
}
#docqa-shell .docqa-stats {
  max-width: 1040px;
  margin: 12px auto 0;
  border-color: #2c2c31 !important;
  background: #101012 !important;
}
@media (max-width: 1180px) {
  #docqa-shell { padding: 0 16px 20px; }
  #docqa-workspace { grid-template-columns: 190px minmax(0, 1fr) 286px !important; }
  #docqa-shell .docqa-library-view,
  #docqa-shell .docqa-session-view,
  #docqa-shell .docqa-sidebar,
  #docqa-shell .docqa-inspector { min-height: 760px; }
  #docqa-shell .docqa-hero-title { font-size: 21px; }
}
@media (max-width: 760px) {
  #docqa-shell { padding: 0 10px 14px; }
  #docqa-workspace { display: flex !important; flex-direction: column; gap: 10px !important; }
  #docqa-shell .docqa-sidebar,
  #docqa-shell .docqa-library-view,
  #docqa-shell .docqa-session-view,
  #docqa-shell .docqa-inspector { min-height: 0; width: 100% !important; }
  #docqa-shell .docqa-sidebar { order: 1; }
  #docqa-shell .docqa-main-region { order: 2; }
  #docqa-shell .docqa-inspector { order: 3; }
  #docqa-shell .docqa-topbar { min-height: 64px; }
  #docqa-shell .docqa-topbar-meta { display: none !important; }
  #docqa-shell .docqa-session-header,
  #docqa-shell .docqa-library-header { display: block !important; }
  #docqa-shell .docqa-session-status { min-width: 0; margin: 10px 0 0; }
  #docqa-shell .docqa-header-action { margin: 10px 0 0; width: 100%; }
  #docqa-shell .docqa-library-toolbar { display: grid !important; grid-template-columns: 1fr 1fr; }
  #docqa-shell .docqa-library-search { grid-column: 1 / -1; }
  #docqa-shell .docqa-library-upload { display: block !important; }
  #docqa-shell .docqa-document-table .table-wrap { overflow-x: hidden !important; }
  #docqa-shell .docqa-document-table table { min-width: 0 !important; table-layout: fixed; }
  #docqa-shell .docqa-document-table th,
  #docqa-shell .docqa-document-table td { white-space: normal !important; overflow-wrap: anywhere; }
  #docqa-shell .docqa-chatbot { min-height: 340px !important; }
  #docqa-shell .docqa-chatbot .message { max-width: 94%; }
  #docqa-shell .docqa-composer-actions { display: grid !important; grid-template-columns: 1fr 1fr; }
  #docqa-shell .docqa-composer-hint { grid-column: 1 / -1; }
  #docqa-shell .docqa-composer-actions .primary,
  #docqa-shell .docqa-composer-actions button { width: 100% !important; }
}

/* UI-R5: make document detail and source cards explicit without changing data semantics. */
#docqa-shell .docqa-library-detail-row {
  margin-top: 14px;
  padding: 10px 12px;
  border: 1px solid #2c2c31;
  border-radius: 12px;
  background: #18181b;
}
#docqa-shell .docqa-detail-selector .wrap {
  border: 0 !important;
  background: transparent !important;
}
#docqa-shell .docqa-detail-selector label span {
  color: #a1a1a9 !important;
}
#docqa-shell .docqa-detail-summary {
  margin-bottom: 10px;
  padding: 12px;
  border: 1px solid #2c2c31;
  border-radius: 12px;
  background: #18181b;
}
#docqa-shell .docqa-detail-summary h3 {
  margin: 0 0 6px;
  font-size: 16px;
  line-height: 22px;
}
#docqa-shell .docqa-detail-summary code {
  color: #93c5fd;
  overflow-wrap: anywhere;
}
#docqa-shell .docqa-detail-summary p {
  margin: 5px 0 !important;
  color: #a1a1a9 !important;
  font-size: 12px !important;
  line-height: 18px !important;
}
#docqa-shell .docqa-danger-copy {
  margin: 0 0 8px;
  color: #fca5a5;
  font-size: 12px;
  line-height: 18px;
}
#docqa-shell .docqa-danger-copy p { color: inherit !important; }
#docqa-shell .docqa-source-summary h3 {
  margin: 12px 0 4px;
  color: #ffffff !important;
  font-size: 13px !important;
  line-height: 20px !important;
}
#docqa-shell .docqa-source-summary blockquote {
  margin: 8px 0 0;
  padding: 8px 10px;
  border-left: 2px solid #2f80ed;
  background: #18181b;
  color: #d4d4d8;
  font-size: 12px;
  line-height: 18px;
}
#docqa-shell .docqa-source-summary p { margin: 4px 0 !important; }
#docqa-shell .docqa-source-summary h3 + p { color: #93c5fd !important; }
#docqa-shell .docqa-inspector .docqa-detail-card button,
#docqa-shell .docqa-inspector .docqa-danger-zone button {
  min-height: 38px;
}
@media (max-width: 760px) {
  #docqa-shell .docqa-inspector {
    position: relative;
    border-radius: 18px 18px 0 0;
    box-shadow: 0 -12px 30px rgba(0, 0, 0, .22);
  }
  #docqa-shell .docqa-inspector::before {
    content: "";
    display: block;
    width: 44px;
    height: 4px;
    margin: 8px auto 0;
    border-radius: 999px;
    background: #52525b;
  }
  #docqa-shell .docqa-library-detail-row { margin-top: 10px; }
  #docqa-shell .docqa-detail-summary { padding: 10px; }
}

/* HF-R1 space navigation: keep navigation and its helper copy in normal flow. */
#docqa-shell .docqa-topbar {
  padding: 0 18px;
  margin-bottom: 16px;
}
#docqa-shell .docqa-topbar-meta {
  gap: 8px;
}
#docqa-shell .docqa-topbar-meta > .block,
#docqa-shell .docqa-topbar-meta > .styler {
  width: auto !important;
  min-width: 0 !important;
  flex: 0 0 auto !important;
}
#docqa-shell .docqa-topbar-chip {
  min-height: 30px;
  padding: 6px 12px;
  border: 1px solid #27272a;
  border-radius: 999px;
  background: #18181b;
  color: #a1a1a9 !important;
  font-size: 11px;
  line-height: 16px;
  white-space: nowrap;
}
#docqa-shell .docqa-topbar-chip p { color: inherit !important; }
#docqa-shell .docqa-topbar-chip.docqa-topbar-scope {
  border-color: #3f3f46;
  color: #d4d4d8 !important;
}
#docqa-shell .docqa-topbar-chip.docqa-topbar-runtime {
  border-color: rgba(34, 197, 94, .55);
  background: rgba(34, 197, 94, .1);
  color: #86efac !important;
}
#docqa-shell .docqa-topbar-chip.docqa-topbar-language {
  width: 30px;
  min-width: 30px;
  padding: 6px 0;
  text-align: center;
  background: #27272a;
  color: #f4f4f5 !important;
}
#docqa-shell .docqa-sidebar {
  display: flex;
  flex-direction: column;
  min-height: 820px;
  padding: 16px 12px 14px;
}
#docqa-shell .docqa-sidebar .docqa-section-kicker {
  margin: 0 8px 8px;
  letter-spacing: .08em;
}
#docqa-shell .docqa-space-nav {
  flex: 0 0 auto !important;
  height: auto !important;
  min-height: 0 !important;
  gap: 6px;
  padding: 0;
  margin-bottom: 10px;
  border-bottom: 0;
}
#docqa-shell .docqa-nav-item {
  min-height: 42px;
  border-radius: 16px !important;
  padding: 0 12px;
  border-color: transparent !important;
  font-size: 13px !important;
}
#docqa-shell .docqa-sidebar .docqa-nav-item.primary {
  background: #27272a !important;
  border-color: #3f3f46 !important;
  color: #f4f4f5 !important;
  box-shadow: inset 3px 0 0 #2f80ed;
}
#docqa-shell .docqa-sidebar .docqa-nav-item.secondary {
  background: transparent !important;
  color: #a1a1a9 !important;
}
#docqa-shell .docqa-sidebar .docqa-nav-item.secondary:hover {
  background: #202023 !important;
  color: #f4f4f5 !important;
}
#docqa-shell .docqa-sidebar .docqa-nav-item:disabled {
  opacity: .72 !important;
}
#docqa-shell .docqa-nav-note {
  margin: 0 10px 16px;
  max-width: 100%;
  overflow-wrap: anywhere;
  word-break: break-word;
  color: #71717a;
  font-size: 11px;
  line-height: 17px;
}
#docqa-shell .docqa-recent-title {
  margin: 0 8px 8px;
  color: #a1a1a9;
  font-size: 12px;
}
#docqa-shell .docqa-recent-list {
  display: grid;
  gap: 6px;
  min-width: 0;
  margin: 0 0 18px;
}
#docqa-shell .docqa-recent-block {
  min-width: 0;
  margin: 0 0 18px;
}
#docqa-shell .docqa-recent-block > .html-container {
  width: 100%;
  min-width: 0;
}
#docqa-shell .docqa-recent-block .docqa-recent-list {
  width: 100%;
  grid-template-columns: 1fr;
}
#docqa-shell .docqa-recent-item {
  min-width: 0;
  padding: 10px 10px 9px;
  border: 1px solid transparent;
  border-radius: 12px;
  background: transparent;
}
#docqa-shell .docqa-recent-item:first-child {
  background: #202023;
  border-color: #27272a;
}
#docqa-shell .docqa-recent-name,
#docqa-shell .docqa-recent-meta {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
#docqa-shell .docqa-recent-name {
  color: #d4d4d8;
  font-size: 12px;
  line-height: 18px;
}
#docqa-shell .docqa-recent-meta {
  margin-top: 2px;
  color: #71717a;
  font-size: 10px;
  line-height: 16px;
}
#docqa-shell .docqa-recent-empty {
  padding: 12px 10px;
  border: 1px dashed #3f3f46;
  border-radius: 12px;
  color: #71717a;
  font-size: 11px;
  line-height: 17px;
}
#docqa-shell .docqa-sidebar-footer {
  margin-top: auto;
  padding: 12px 8px 0;
  border-top: 1px solid #252529;
  color: #71717a;
  font-size: 10px;
  line-height: 16px;
}
#docqa-shell .docqa-sidebar-footer p { color: inherit !important; }
#docqa-shell .docqa-sidebar-footer strong { color: #a1a1a9; font-weight: 500; }
#docqa-shell .docqa-main-region {
  min-width: 0;
}
#docqa-shell .docqa-main-region > .gr-group {
  min-width: 0;
}
#docqa-shell .docqa-main-region .docqa-library-view,
#docqa-shell .docqa-main-region .docqa-session-view {
  box-shadow: 0 18px 42px rgba(0, 0, 0, .24);
}
@media (max-width: 1180px) {
  #docqa-shell .docqa-topbar { padding: 0 10px; }
  #docqa-shell .docqa-sidebar { min-height: 760px; }
  #docqa-shell .docqa-topbar-chip.docqa-topbar-language { display: none; }
  #docqa-shell .docqa-session-header {
    grid-template-columns: minmax(0, 1fr) 146px;
  }
  #docqa-shell .docqa-session-header > .column:first-child {
    grid-area: intro;
  }
  #docqa-shell .docqa-session-status {
    grid-area: status;
    width: 100% !important;
  }
  #docqa-shell .docqa-session-header > .docqa-header-action {
    grid-area: action;
    width: 146px !important;
  }
}
@media (max-width: 760px) {
  #docqa-shell .docqa-topbar { padding: 0 4px; }
  #docqa-shell .docqa-topbar-meta { display: flex !important; margin-left: auto; }
  #docqa-shell .docqa-topbar-chip.docqa-topbar-scope { display: none; }
  #docqa-shell .docqa-topbar-chip.docqa-topbar-runtime { padding: 6px 9px; }
  #docqa-shell .docqa-sidebar { min-height: 0; padding: 12px; }
  #docqa-shell .docqa-space-nav { display: grid !important; grid-template-columns: 1fr 1fr; }
  #docqa-shell .docqa-nav-item { min-height: 44px; }
  #docqa-shell .docqa-nav-note { grid-column: 1 / -1; margin: -2px 8px 0; }
  #docqa-shell .docqa-recent-block .docqa-recent-list { grid-template-columns: 1fr; }
  #docqa-shell .docqa-sidebar-footer { display: none; }
}

/* UI-HF2: the library is a scannable workspace, not a native data table. */
#docqa-shell .docqa-library-toolbar {
  align-items: stretch;
  padding: 10px;
  border: 1px solid #27272a;
  border-radius: 12px;
  background: #111113;
}
#docqa-shell .docqa-library-toolbar .docqa-library-search { flex: 1 1 280px; min-width: 220px; }
#docqa-shell .docqa-library-toolbar .docqa-library-filter { flex: 0 1 150px; min-width: 120px; }
#docqa-shell .docqa-library-count {
  align-self: center;
  min-width: 76px;
  margin-left: auto;
  text-align: right;
}
/* Gradio gives Markdown blocks an inline overflow:auto wrapper.  In the
   compact library header that produced a horizontal scrollbar for simple
   metadata chips, so the header owns the sizing instead. */
#docqa-shell .docqa-library-header-meta {
  display: flex !important;
  flex: 0 0 auto !important;
  width: auto !important;
  min-width: 0 !important;
  gap: 4px;
  justify-content: flex-end;
  align-items: center;
}
#docqa-shell .docqa-library-header-meta > .block {
  flex: 0 0 auto !important;
  width: auto !important;
  min-width: 0 !important;
  overflow: visible !important;
  border-width: 0 !important;
  padding: 0 !important;
}
#docqa-shell .docqa-library-header-meta > .block > .svelte-vuh1yp,
#docqa-shell .docqa-library-header-meta .docqa-chip {
  width: auto !important;
  min-width: 0 !important;
  max-width: none !important;
}
#docqa-shell .docqa-library-header-meta .docqa-chip {
  flex: 0 0 auto !important;
  margin: 0 !important;
  padding: 3px 7px;
  font-size: 10px;
  line-height: 16px;
  white-space: nowrap;
  overflow: hidden !important;
}
#docqa-shell .docqa-library-search textarea {
  overflow: hidden !important;
  resize: none !important;
}
#docqa-shell .docqa-document-list {
  display: grid;
  gap: 8px;
  padding: 12px;
  border: 1px solid #27272a;
  border-radius: 14px;
  background: #101012;
}
#docqa-shell .docqa-document-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 92px 112px 150px;
  align-items: center;
  gap: 14px;
  min-width: 0;
  min-height: 68px;
  padding: 12px 14px;
  border: 1px solid #27272a;
  border-radius: 10px;
  background: #18181b;
  transition: border-color .15s ease, background .15s ease;
}
#docqa-shell .docqa-document-row:hover {
  border-color: #3f3f46;
  background: #202023;
}
#docqa-shell .docqa-document-main { min-width: 0; }
#docqa-shell .docqa-document-name,
#docqa-shell .docqa-document-meta,
#docqa-shell .docqa-document-time {
  display: block;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}
#docqa-shell .docqa-document-name {
  color: #f4f4f5;
  font-size: 13px;
  line-height: 20px;
  overflow-wrap: anywhere;
}
#docqa-shell .docqa-document-meta {
  margin-top: 3px;
  color: #71717a;
  font-size: 11px;
  line-height: 16px;
  white-space: nowrap;
}
#docqa-shell .docqa-document-format,
#docqa-shell .docqa-document-time {
  color: #a1a1a9;
  font-size: 11px;
  line-height: 18px;
}
#docqa-shell .docqa-document-time { text-align: right; }
#docqa-shell .docqa-status-pill {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  min-height: 24px;
  padding: 3px 9px;
  border: 1px solid #3f3f46;
  border-radius: 999px;
  color: #d4d4d8;
  font-size: 11px;
  line-height: 16px;
  white-space: nowrap;
}
#docqa-shell .docqa-status-indexed .docqa-status-pill {
  border-color: rgba(34, 197, 94, .55);
  background: rgba(34, 197, 94, .1);
  color: #86efac;
}
#docqa-shell .docqa-status-failed .docqa-status-pill {
  border-color: rgba(239, 68, 68, .65);
  background: rgba(239, 68, 68, .1);
  color: #fca5a5;
}
#docqa-shell .docqa-status-archived .docqa-status-pill {
  background: #27272a;
  color: #a1a1a9;
}
#docqa-shell .docqa-document-error {
  display: block;
  margin-top: 2px;
  overflow: hidden;
  color: #fca5a5;
  text-overflow: ellipsis;
  white-space: nowrap;
}
#docqa-shell .docqa-library-empty {
  display: grid;
  gap: 5px;
  min-height: 170px;
  align-content: center;
  justify-items: center;
  padding: 24px;
  border: 1px dashed #3f3f46;
  border-radius: 14px;
  color: #a1a1a9;
  text-align: center;
}
#docqa-shell .docqa-library-empty strong { color: #f4f4f5; font-size: 14px; }
#docqa-shell .docqa-library-empty span { color: #71717a; font-size: 12px; }
#docqa-shell .docqa-document-inspector {
  min-width: 0;
  padding: 18px;
  background: #18181b;
}
#docqa-shell .docqa-document-inspector .docqa-inspector-heading {
  margin-bottom: 12px;
  padding-bottom: 14px;
  border-bottom: 1px solid #27272a;
}
#docqa-shell .docqa-document-inspector .docqa-detail-summary {
  margin: 0 0 14px;
  background: #111113;
}
#docqa-shell .docqa-detail-badge,
#docqa-shell .docqa-detail-status {
  display: inline-block;
  padding: 3px 7px;
  border-radius: 999px;
  background: #27272a;
  color: #d4d4d8;
  font-size: 11px;
  line-height: 16px;
}
#docqa-shell .docqa-detail-status { color: #86efac; background: rgba(34, 197, 94, .1); }
#docqa-shell .docqa-detail-summary code { overflow-wrap: anywhere; }
#docqa-shell .docqa-detail-error {
  padding: 8px 10px;
  border-left: 2px solid #ef4444;
  background: rgba(239, 68, 68, .08);
  color: #fca5a5;
  overflow-wrap: anywhere;
}
#docqa-shell .docqa-document-inspector .docqa-danger-zone {
  margin-top: 12px;
  padding: 12px;
  border: 1px solid rgba(239, 68, 68, .35);
  border-radius: 12px;
  background: rgba(127, 29, 29, .12);
}
#docqa-shell .docqa-document-inspector .gr-json,
#docqa-shell .docqa-document-inspector > .styler,
#docqa-shell .docqa-document-inspector .block,
#docqa-shell .docqa-document-inspector .docqa-document-detail .wrap,
#docqa-shell .docqa-document-inspector .gr-json .json-holder,
#docqa-shell .docqa-document-inspector .gr-json .table-wrap,
#docqa-shell .docqa-document-inspector .gr-json pre,
#docqa-shell .docqa-document-inspector .json-holder {
  background: #111113 !important;
  color: #d4d4d8 !important;
  border-color: #27272a !important;
}
#docqa-shell .docqa-document-inspector .gr-json button,
#docqa-shell .docqa-document-inspector .gr-json span,
#docqa-shell .docqa-document-inspector .gr-json code { color: #d4d4d8 !important; }
@media (max-width: 1180px) {
  #docqa-shell .docqa-document-row { grid-template-columns: minmax(0, 1fr) 78px 102px 124px; gap: 10px; }
  #docqa-shell .docqa-library-toolbar { flex-wrap: wrap; }
  #docqa-shell .docqa-library-toolbar .docqa-library-filter { flex: 1 1 120px; }
}
@media (max-width: 760px) {
  #docqa-shell .docqa-library-toolbar { display: grid !important; grid-template-columns: 1fr 1fr; gap: 8px; }
  #docqa-shell .docqa-library-toolbar .docqa-library-search { grid-column: 1 / -1; min-width: 0; }
  #docqa-shell .docqa-library-count { grid-column: 1 / -1; margin: 0; text-align: left; }
  #docqa-shell .docqa-document-list { padding: 8px; }
  #docqa-shell .docqa-document-row {
    grid-template-columns: minmax(0, 1fr) 78px 82px;
    gap: 6px 8px;
    min-height: 82px;
    padding: 10px;
  }
  #docqa-shell .docqa-document-main { grid-column: 1 / -1; }
  #docqa-shell .docqa-document-format,
  #docqa-shell .docqa-document-status,
  #docqa-shell .docqa-document-time { align-self: center; }
  #docqa-shell .docqa-document-time { text-align: right; }
  #docqa-shell .docqa-document-meta { white-space: normal; }
  #docqa-shell .docqa-document-inspector { padding: 12px; }
}

/* HF-R2 session workspace: a controlled presentation layer backed by real chat state. */
#docqa-shell .docqa-session-view {
  height: auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
#docqa-shell .docqa-session-view > .docqa-session-header {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) 158px;
  grid-template-areas:
    "intro action"
    "chips action";
  align-items: start;
  gap: 10px 18px;
  flex: 0 0 auto;
  margin: 0;
  padding: 0 0 18px;
  border-bottom: 1px solid #27272a;
}
#docqa-shell .docqa-session-intro { grid-area: intro; min-width: 0; }
#docqa-shell .docqa-session-header > .docqa-header-action {
  grid-area: action;
  align-self: center;
  width: 158px;
  min-height: 42px;
  margin: 0 !important;
  border: 0 !important;
  border-radius: 10px !important;
  background: #1687f8 !important;
  color: #ffffff !important;
  font-weight: 700;
}
#docqa-shell .docqa-session-header > .docqa-header-action:hover { background: #2f97ff !important; }
#docqa-shell .docqa-session-chip-row {
  grid-area: chips;
  display: flex !important;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  min-width: 0;
}
#docqa-shell .docqa-session-chip-row > * { width: auto !important; min-width: 0; }
#docqa-shell .docqa-session-chip-row .docqa-status {
  width: auto !important;
  min-width: 0;
  max-width: min(100%, 300px);
  margin: 0 !important;
  padding: 6px 10px;
  overflow: hidden;
  border: 1px solid rgba(34, 197, 94, .55);
  border-radius: 999px;
  background: rgba(5, 95, 47, .22);
  color: #bbf7d0;
  line-height: 18px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
#docqa-shell .docqa-session-chip-row .docqa-status p {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
#docqa-shell .docqa-session-workspace {
  display: flex;
  min-height: 0;
  flex: 1 1 auto;
  flex-direction: column;
  gap: 14px;
  padding-top: 14px;
}
#docqa-shell .docqa-session-scope {
  flex: 0 0 auto !important;
  min-height: 0 !important;
  height: auto !important;
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
}
#docqa-shell .docqa-scope-heading,
#docqa-shell .docqa-timeline-heading,
#docqa-shell .docqa-composer-heading {
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 7px;
}
#docqa-shell .docqa-scope-heading .docqa-eyebrow,
#docqa-shell .docqa-timeline-heading .docqa-eyebrow,
#docqa-shell .docqa-composer-heading .docqa-eyebrow { margin: 0; }
#docqa-shell .docqa-scope-heading { display: none !important; }
#docqa-shell .docqa-session-scope .block { padding: 0 !important; }
#docqa-shell .docqa-session-filter {
  width: 180px;
  min-width: 0;
}
#docqa-shell .docqa-session-filter > label { display: none !important; }
#docqa-shell .docqa-session-filter .wrap,
#docqa-shell .docqa-session-filter .secondary-wrap {
  min-height: 36px !important;
  border: 1px solid #3f3f46 !important;
  border-radius: 999px !important;
  background: #18181b !important;
}
#docqa-shell .docqa-session-filter input,
#docqa-shell .docqa-session-filter span { font-size: 12px !important; }
#docqa-shell .docqa-session-scope .docqa-status { display: none !important; }
#docqa-shell .docqa-timeline-panel {
  display: flex;
  min-height: 0;
  flex: 0 0 auto;
  flex-direction: column;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
}
#docqa-shell .docqa-timeline-heading {
  display: flex !important;
  min-height: 26px;
  margin: 0;
  padding: 0 0 10px;
  border-bottom: 1px solid #27272a;
}
#docqa-shell .docqa-timeline-render { width: 100%; }
#docqa-shell .docqa-timeline-render > .html-container { padding: 0 !important; }
#docqa-shell .docqa-timeline {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 180px;
  padding: 14px 0 8px;
}
#docqa-shell .docqa-timeline-separator {
  padding: 5px 12px;
  border-radius: 999px;
  background: #202023;
  color: #71717a;
  font-size: 11px;
  text-align: center;
}
#docqa-shell .docqa-timeline-empty {
  display: grid;
  place-content: center;
  gap: 7px;
  min-height: 164px;
  padding: 24px;
  border: 1px dashed #3f3f46;
  border-radius: 14px;
  color: #a1a1aa;
  text-align: center;
}
#docqa-shell .docqa-timeline-empty strong { color: #e4e4e7; font-size: 14px; }
#docqa-shell .docqa-timeline-empty span { font-size: 12px; line-height: 18px; }
#docqa-shell .docqa-timeline-message {
  display: grid;
  gap: 7px;
  max-width: 78%;
  padding: 13px 15px;
  border: 1px solid #3f3f46;
  border-radius: 14px;
  color: #f4f4f5;
  font-size: 13px;
  line-height: 1.7;
}
#docqa-shell .docqa-timeline-user {
  align-self: end;
  margin-left: auto;
  border-color: #1687f8;
  border-radius: 14px 14px 4px 14px;
  background: #1687f8;
  color: #ffffff;
}
#docqa-shell .docqa-timeline-assistant {
  align-self: start;
  margin-right: auto;
  border-radius: 14px 14px 14px 4px;
  background: #27272a;
}
#docqa-shell .docqa-timeline-role {
  color: #a1a1aa;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .04em;
}
#docqa-shell .docqa-timeline-user .docqa-timeline-role { color: #dbeafe; }
#docqa-shell .docqa-timeline-content { overflow-wrap: anywhere; }
#docqa-shell .docqa-timeline-meta { display: flex; flex-wrap: wrap; gap: 7px; }
#docqa-shell .docqa-timeline-meta span {
  padding: 3px 8px;
  border: 1px solid rgba(34, 197, 94, .55);
  border-radius: 999px;
  background: rgba(5, 95, 47, .22);
  color: #bbf7d0;
  font-size: 11px;
}
#docqa-shell .docqa-timeline-state {
  color: #a1a1aa;
  font-size: 12px;
  line-height: 18px;
}
#docqa-shell .docqa-chatbot,
#docqa-shell .docqa-answer-status { display: none !important; }
#docqa-shell .docqa-composer {
  flex: 0 0 auto !important;
  min-height: 0 !important;
  height: auto !important;
  margin-top: 0;
  padding: 9px 12px 8px;
  border: 1px solid #3f3f46;
  border-radius: 14px;
  background: #09090b;
  box-shadow: 0 10px 28px rgba(0, 0, 0, .24);
}
#docqa-shell .docqa-composer-heading { display: none !important; }
#docqa-shell .docqa-composer-input { width: 100%; }
#docqa-shell .docqa-composer-input .wrap,
#docqa-shell .docqa-composer-input .block { border: 0 !important; background: transparent !important; }
#docqa-shell .docqa-composer-input textarea {
  min-height: 30px !important;
  max-height: 72px;
  padding: 6px 0 !important;
  color: #f4f4f5 !important;
  font-size: 14px !important;
  line-height: 20px !important;
}
#docqa-shell .docqa-composer-input textarea::placeholder { color: #71717a !important; }
#docqa-shell .docqa-composer-actions {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) 42px auto;
  align-items: center;
  min-height: 30px;
  gap: 8px;
}
#docqa-shell .docqa-composer-actions .docqa-composer-hint { margin: 0; color: #71717a; font-size: 10px; }
#docqa-shell .docqa-composer-actions button { min-width: 42px; min-height: 34px; margin: 0; }
#docqa-shell .docqa-composer-send {
  width: 36px !important;
  min-width: 36px !important;
  height: 36px !important;
  min-height: 36px !important;
  padding: 0 !important;
  border: 0 !important;
  border-radius: 50% !important;
  background: #f4f4f5 !important;
  color: #09090b !important;
  font-size: 17px !important;
  font-weight: 800 !important;
}
#docqa-shell .docqa-composer-send:hover { background: #ffffff !important; }
#docqa-shell .docqa-composer-clear {
  min-width: 48px !important;
  padding: 0 8px !important;
  border: 0 !important;
  background: transparent !important;
  color: #a1a1aa !important;
  font-size: 12px !important;
}
#docqa-shell .docqa-composer button:disabled,
#docqa-shell .docqa-composer textarea:disabled { opacity: .55 !important; }
@media (max-width: 1180px) {
  #docqa-shell .docqa-session-view > .docqa-session-header { grid-template-columns: minmax(0, 1fr) 142px; }
  #docqa-shell .docqa-session-header > .docqa-header-action { width: 142px; }
  #docqa-shell .docqa-timeline-message { max-width: 88%; }
}
@media (max-width: 760px) {
  #docqa-shell .docqa-session-view > .docqa-session-header {
    grid-template-columns: 1fr;
    grid-template-areas: "intro" "chips" "action";
    gap: 10px;
  }
  #docqa-shell .docqa-session-header > .docqa-header-action { width: 100%; }
  #docqa-shell .docqa-session-filter { width: 100%; }
  #docqa-shell .docqa-session-chip-row { align-items: stretch; }
  #docqa-shell .docqa-session-chip-row .docqa-status { max-width: 100%; }
  #docqa-shell .docqa-timeline { min-height: 240px; padding-top: 12px; }
  #docqa-shell .docqa-timeline-empty { min-height: 210px; }
  #docqa-shell .docqa-timeline-message { max-width: 94%; }
  #docqa-shell .docqa-composer { padding: 9px 10px 8px; }
  #docqa-shell .docqa-composer-actions { grid-template-columns: minmax(0, 1fr) 42px 44px; }
}

/* HF-R3 owns the document-library workbench.  The catalog remains backed by
   UIController; this block only replaces the native-form visual structure. */
#docqa-shell .docqa-library-view {
  display: flex;
  min-height: 0;
  flex-direction: column;
  gap: 16px;
  padding: 26px 28px 22px;
  background: #09090b;
}
#docqa-shell .docqa-library-view > .docqa-library-header {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) 196px;
  align-items: end;
  gap: 24px;
  margin: 0;
  padding: 0;
}
#docqa-shell .docqa-library-header .docqa-hero-title { margin: 0 0 6px; }
#docqa-shell .docqa-library-header .docqa-hero-copy { max-width: 520px; margin: 0; }
#docqa-shell .docqa-library-header-actions {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) 80px;
  align-items: center;
  gap: 8px;
  min-width: 0;
}
#docqa-shell .docqa-library-header-actions .docqa-upload-trigger {
  min-width: 0;
  margin: 0;
}
#docqa-shell .docqa-library-header-actions .docqa-upload-trigger > label,
#docqa-shell .docqa-library-header-actions .docqa-upload-trigger .label-wrap { display: none !important; }
#docqa-shell .docqa-library-header-actions .docqa-upload-trigger .wrap,
#docqa-shell .docqa-library-header-actions .docqa-upload-trigger .file-preview,
#docqa-shell .docqa-library-header-actions .docqa-upload-trigger .upload-container {
  min-height: 42px !important;
  border: 0 !important;
  border-radius: 10px !important;
  background: #1687f8 !important;
  color: #ffffff !important;
}
#docqa-shell .docqa-library-header-actions .docqa-upload-trigger > button {
  min-height: 42px !important;
  height: 42px !important;
  padding: 0 12px !important;
  border: 0 !important;
  border-radius: 10px !important;
  background: #1687f8 !important;
}
#docqa-shell .docqa-library-header-actions .docqa-upload-trigger > button .wrap {
  display: block !important;
  font-size: 0 !important;
}
#docqa-shell .docqa-library-header-actions .docqa-upload-trigger > button .icon-wrap,
#docqa-shell .docqa-library-header-actions .docqa-upload-trigger > button .or { display: none !important; }
#docqa-shell .docqa-library-header-actions .docqa-upload-trigger > button .wrap::after {
  content: "↑ 上传文档";
  color: #ffffff;
  font-size: 13px;
  font-weight: 700;
}
#docqa-shell .docqa-library-header-actions .docqa-upload-trigger button,
#docqa-shell .docqa-library-header-actions .docqa-upload-trigger span,
#docqa-shell .docqa-library-header-actions .docqa-upload-trigger label {
  color: #ffffff !important;
  font-size: 13px !important;
  font-weight: 700 !important;
}
#docqa-shell .docqa-library-index {
  min-width: 80px !important;
  min-height: 42px !important;
  margin: 0 !important;
  border: 1px solid #3f3f46 !important;
  border-radius: 10px !important;
  background: #18181b !important;
  color: #e4e4e7 !important;
  font-size: 12px !important;
}
#docqa-shell .docqa-library-status {
  grid-column: 1 / -1;
  min-height: 0;
  margin: -2px 0 0 !important;
  color: #71717a;
  font-size: 10px;
  line-height: 14px;
}
#docqa-shell .docqa-library-toolbar {
  display: grid !important;
  flex: 0 0 auto !important;
  grid-template-columns: minmax(0, 1fr);
  gap: 10px;
  margin: 0;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
}
#docqa-shell .docqa-library-toolbar > .form {
  display: block !important;
  height: auto !important;
  min-height: 0 !important;
}
#docqa-shell .docqa-library-search-field { width: 100%; min-width: 0 !important; }
#docqa-shell .docqa-library-search-field .wrap,
#docqa-shell .docqa-library-search-field .input-container {
  min-height: 46px !important;
  border: 1px solid #3f3f46 !important;
  border-radius: 10px !important;
  background: #18181b !important;
}
#docqa-shell .docqa-library-search-field textarea,
#docqa-shell .docqa-library-search-field input { padding: 11px 13px !important; font-size: 13px !important; }
#docqa-shell .docqa-library-filter-bar {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 8px;
  margin: 0;
  padding: 6px 8px;
  border: 1px solid #27272a;
  border-radius: 10px;
  background: #18181b;
}
#docqa-shell .docqa-library-filter-bar > .form {
  display: grid !important;
  grid-template-columns: 126px 126px 132px;
  align-items: center;
  gap: 8px;
  min-width: 0 !important;
  height: auto !important;
}
#docqa-shell .docqa-library-filter-control { min-width: 0 !important; }
#docqa-shell .docqa-library-filter-control [data-testid="block-info"] { display: none !important; }
#docqa-shell .docqa-library-filter-control .container { min-height: 28px !important; }
#docqa-shell .docqa-library-filter-control .wrap,
#docqa-shell .docqa-library-filter-control .secondary-wrap {
  min-height: 28px !important;
  border: 1px solid #3f3f46 !important;
  border-radius: 999px !important;
  background: #202023 !important;
}
#docqa-shell .docqa-library-filter-control span,
#docqa-shell .docqa-library-filter-control input { font-size: 11px !important; }
#docqa-shell .docqa-library-count {
  justify-self: end;
  min-width: 0;
  margin: 0 !important;
  color: #71717a;
  font-size: 11px;
  white-space: nowrap;
}
#docqa-shell .docqa-library-list-heading { display: none !important; }
#docqa-shell .docqa-document-library {
  flex: 1 1 auto;
  min-height: 0;
  margin: 0;
}
#docqa-shell .docqa-document-library > .html-container { height: 100%; padding: 0 !important; }
#docqa-shell .docqa-document-list {
  display: grid;
  align-content: start;
  gap: 0;
  min-height: 100%;
  padding: 12px;
  border: 1px solid #27272a;
  border-radius: 14px;
  background: #111113;
}
#docqa-shell .docqa-document-list-columns,
#docqa-shell .docqa-document-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 84px 94px 108px;
  align-items: center;
  gap: 14px;
  min-width: 0;
}
#docqa-shell .docqa-document-list-columns {
  min-height: 30px;
  padding: 0 12px 8px;
  border-bottom: 1px solid #27272a;
  color: #71717a;
  font-size: 10px;
  line-height: 14px;
}
#docqa-shell .docqa-document-list-columns span:last-child { text-align: right; }
#docqa-shell .docqa-document-row {
  min-height: 76px;
  padding: 12px;
  border: 0;
  border-bottom: 1px solid #27272a;
  border-radius: 0;
  background: transparent;
}
#docqa-shell .docqa-document-row:last-child { border-bottom: 0; }
#docqa-shell .docqa-document-row:hover {
  border-color: #27272a;
  border-radius: 10px;
  background: #202023;
}
#docqa-shell .docqa-document-main { min-width: 0; }
#docqa-shell .docqa-document-name {
  display: -webkit-box;
  overflow: hidden;
  color: #f4f4f5;
  font-size: 13px;
  font-weight: 700;
  line-height: 19px;
  overflow-wrap: anywhere;
  text-overflow: ellipsis;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
#docqa-shell .docqa-document-meta { margin-top: 3px; color: #71717a; font-size: 10px; line-height: 15px; }
#docqa-shell .docqa-document-format,
#docqa-shell .docqa-document-time { color: #a1a1aa; font-size: 11px; }
#docqa-shell .docqa-document-time { text-align: right; white-space: nowrap; }
#docqa-shell .docqa-status-pill { min-height: 22px; padding: 2px 8px; font-size: 10px; }
#docqa-shell .docqa-library-empty { min-height: 240px; border-color: #3f3f46; background: #18181b; }
#docqa-shell .docqa-document-inspector {
  display: flex;
  min-height: 0;
  flex-direction: column;
  gap: 14px;
  padding: 0 !important;
  background: transparent !important;
}
#docqa-shell .docqa-document-inspector .docqa-inspector-body { display: grid; gap: 12px; }
#docqa-shell .docqa-detail-selector-controlled { margin: 0; }
#docqa-shell .docqa-detail-selector-controlled .wrap,
#docqa-shell .docqa-detail-selector-controlled .secondary-wrap {
  min-height: 38px !important;
  border: 1px solid #3f3f46 !important;
  border-radius: 9px !important;
  background: #18181b !important;
}
#docqa-shell .docqa-detail-selector-controlled label { color: #a1a1aa !important; font-size: 11px !important; }
#docqa-shell .docqa-document-inspector-markup > .html-container { padding: 0 !important; }
#docqa-shell .docqa-document-inspector-card {
  display: grid;
  gap: 10px;
  padding: 2px 0 0;
}
#docqa-shell .docqa-inspector-eyebrow { color: #71717a; font-size: 10px; letter-spacing: .04em; }
#docqa-shell .docqa-document-inspector-card h2 {
  margin: 0;
  overflow-wrap: anywhere;
  color: #f4f4f5;
  font-size: 17px;
  line-height: 24px;
}
#docqa-shell .docqa-inspector-badges { display: flex; flex-wrap: wrap; gap: 6px; }
#docqa-shell .docqa-inspector-metadata { display: grid; gap: 10px; margin: 2px 0 0; }
#docqa-shell .docqa-inspector-metadata > div { display: grid; gap: 3px; min-width: 0; }
#docqa-shell .docqa-inspector-metadata dt { color: #71717a; font-size: 10px; }
#docqa-shell .docqa-inspector-metadata dd { margin: 0; color: #d4d4d8; font-size: 11px; line-height: 17px; overflow-wrap: anywhere; }
#docqa-shell .docqa-inspector-metadata code { display: inline-block; max-width: 100%; overflow-wrap: anywhere; color: #60a5fa; font-size: 10px; }
#docqa-shell .docqa-inspector-location-note { margin: 0; color: #71717a; font-size: 10px; line-height: 16px; }
#docqa-shell .docqa-inspector-error-detail { padding: 9px; border: 1px solid rgba(239, 68, 68, .35); border-radius: 8px; background: rgba(127, 29, 29, .14); color: #fca5a5; font-size: 11px; overflow-wrap: anywhere; }
#docqa-shell .docqa-inspector-error-detail p { margin: 4px 0 0; }
#docqa-shell .docqa-inspector-empty { display: grid; gap: 6px; min-height: 160px; place-content: center; padding: 18px; border: 1px dashed #3f3f46; border-radius: 12px; color: #a1a1aa; text-align: center; }
#docqa-shell .docqa-inspector-empty strong { color: #e4e4e7; font-size: 13px; }
#docqa-shell .docqa-inspector-empty span { font-size: 11px; line-height: 17px; }
#docqa-shell .docqa-inspector-error { border-color: rgba(239, 68, 68, .5); color: #fca5a5; }
#docqa-shell .docqa-document-inspector .docqa-danger-zone { margin: 0; padding: 12px; border-color: rgba(239, 68, 68, .35); background: rgba(127, 29, 29, .12); }
@media (max-width: 1180px) {
  #docqa-shell .docqa-library-view { padding: 22px; }
  #docqa-shell .docqa-library-view > .docqa-library-header { grid-template-columns: minmax(0, 1fr) 172px; gap: 16px; }
  #docqa-shell .docqa-library-header-actions { grid-template-columns: minmax(0, 1fr); }
  #docqa-shell .docqa-library-index { width: 100%; }
  #docqa-shell .docqa-library-filter-bar { grid-template-columns: minmax(0, 1fr) auto; }
  #docqa-shell .docqa-library-filter-bar > .form { grid-template-columns: 1fr 1fr 1fr; }
  #docqa-shell .docqa-library-count { justify-self: end; }
  #docqa-shell .docqa-document-list-columns,
  #docqa-shell .docqa-document-row { grid-template-columns: minmax(0, 1fr) 72px 90px 92px; gap: 10px; }
}
@media (max-width: 760px) {
  #docqa-shell .docqa-library-view { padding: 16px 14px; gap: 14px; }
  #docqa-shell .docqa-library-view > .docqa-library-header { grid-template-columns: 1fr; }
  #docqa-shell .docqa-library-header-actions { grid-template-columns: minmax(0, 1fr) 86px; }
  #docqa-shell .docqa-library-filter-bar { grid-template-columns: 1fr; }
  #docqa-shell .docqa-library-filter-bar > .form { grid-template-columns: 1fr 1fr; }
  #docqa-shell .docqa-library-filter-bar > .form > :last-child { grid-column: 1 / -1; }
  #docqa-shell .docqa-library-count { justify-self: start; }
  #docqa-shell .docqa-document-list { padding: 8px; }
  #docqa-shell .docqa-document-list-columns { display: none; }
  #docqa-shell .docqa-document-row { grid-template-columns: minmax(0, 1fr) auto; gap: 7px 10px; min-height: 86px; padding: 12px 8px; }
  #docqa-shell .docqa-document-main { grid-column: 1 / -1; }
  #docqa-shell .docqa-document-format { display: none; }
  #docqa-shell .docqa-document-status { justify-self: start; }
  #docqa-shell .docqa-document-time { justify-self: end; font-size: 10px; }
}

/* HF-R1 session shell retained below only as a historical marker. */
/*
#docqa-shell .docqa-session-scope .docqa-status {
  padding: 5px 9px;
  line-height: 18px;
}
#docqa-shell .docqa-timeline-panel {
  display: flex;
  min-height: 260px;
  flex: 0 0 auto;
  flex-direction: column;
  padding: 14px;
  border: 1px solid #27272a;
  border-radius: 14px;
  background: #0f0f11;
}
#docqa-shell .docqa-timeline-heading { flex: 0 0 auto; }
#docqa-shell .docqa-chatbot {
  min-height: 180px !important;
  flex: 0 0 auto;
  margin: 0;
  border: 0 !important;
  background: transparent !important;
}
#docqa-shell .docqa-chatbot > .wrap,
#docqa-shell .docqa-chatbot .bubble-wrap,
#docqa-shell .docqa-chatbot .chatbot {
  min-height: 0 !important;
  background: transparent !important;
}
#docqa-shell .docqa-chatbot .message {
  max-width: 82%;
  margin: 12px 0;
  padding: 13px 15px;
  border-radius: 14px;
  font-size: 13px;
  line-height: 1.65;
}
#docqa-shell .docqa-chatbot .message.user,
#docqa-shell .docqa-chatbot [data-testid="user"] {
  margin-left: auto;
  border-color: #2f80ed;
  border-radius: 14px 14px 4px 14px;
  background: #2f80ed;
  color: #ffffff;
}
#docqa-shell .docqa-chatbot .message.bot,
#docqa-shell .docqa-chatbot [data-testid="bot"] {
  margin-right: auto;
  border-color: #3f3f46;
  border-radius: 14px 14px 14px 4px;
  background: #27282a;
  color: #f4f4f5;
}
#docqa-shell .docqa-chatbot .message.bot::before,
#docqa-shell .docqa-chatbot [data-testid="bot"]::before {
  content: "回答";
  display: block;
  margin-bottom: 5px;
  color: #a1a1a9;
  font-size: 10px;
  line-height: 14px;
}
#docqa-shell .docqa-answer-status {
  flex: 0 0 auto;
  min-height: 28px;
  margin-top: 8px;
  padding: 6px 9px;
  border-top: 1px solid #27272a;
  color: #a1a1a9;
}
#docqa-shell .docqa-answer-status p { margin: 0 !important; }
#docqa-shell .docqa-composer {
  flex: 0 0 auto !important;
  min-height: 0 !important;
  height: auto !important;
  margin-top: 0;
  padding: 12px 14px 10px;
  border-color: #52525b;
  border-radius: 16px;
  background: #111113;
  box-shadow: 0 -10px 24px rgba(0, 0, 0, .22);
}
#docqa-shell .docqa-composer-heading { margin-bottom: 4px; }
#docqa-shell .docqa-composer textarea {
  min-height: 66px !important;
  padding: 8px 0 !important;
  color: #f4f4f5 !important;
  font-size: 14px !important;
  line-height: 22px !important;
}
#docqa-shell .docqa-composer textarea::placeholder { color: #71717a !important; }
#docqa-shell .docqa-composer-actions { min-height: 34px; }
#docqa-shell .docqa-composer-actions .docqa-composer-hint { margin-right: auto; }
#docqa-shell .docqa-composer-actions button {
  min-width: 88px;
  min-height: 36px;
  border-radius: 10px !important;
}
#docqa-shell .docqa-composer-actions .primary {
  min-width: 104px;
  background: #2f80ed !important;
}
#docqa-shell .docqa-composer-actions button:not(.primary) {
  border-color: #3f3f46 !important;
  background: #202023 !important;
  color: #d4d4d8 !important;
}
#docqa-shell .docqa-composer button:disabled,
#docqa-shell .docqa-composer textarea:disabled { opacity: .55 !important; }
@media (max-width: 1180px) {
  #docqa-shell .docqa-session-view {
    height: auto;
    min-height: 0;
  }
  #docqa-shell .docqa-chatbot .message { max-width: 88%; }
}
@media (max-width: 760px) {
  #docqa-shell .docqa-session-view { height: auto; min-height: 0; }
  #docqa-shell .docqa-session-workspace { gap: 10px; }
  #docqa-shell .docqa-timeline-panel { min-height: 380px; padding: 10px; }
  #docqa-shell .docqa-chatbot { min-height: 310px !important; }
  #docqa-shell .docqa-chatbot .message { max-width: 94%; margin: 9px 0; }
  #docqa-shell .docqa-composer { padding: 11px 12px 9px; }
  #docqa-shell .docqa-composer-actions {
    display: grid !important;
    grid-template-columns: 1fr 1fr;
  }
  #docqa-shell .docqa-composer-hint { grid-column: 1 / -1; }
#docqa-shell .docqa-composer-actions button { width: 100% !important; }
}
*/

/* UI-HF4: source cards and note workspace for the context inspector. */
#docqa-shell .docqa-context-view,
#docqa-shell .docqa-context-view > .styler,
#docqa-shell .docqa-context-view .tabitem,
#docqa-shell .docqa-context-view .tabitem > .column {
  background: #18181b !important;
  border-color: #2c2c31 !important;
  color: #f4f4f5 !important;
}
#docqa-shell .docqa-context-view .tabitem .block,
#docqa-shell .docqa-context-view .tabitem .wrap,
#docqa-shell .docqa-context-view .tabitem .gr-box {
  background: transparent !important;
  border-color: #2c2c31 !important;
  color: #f4f4f5 !important;
}
#docqa-shell .docqa-source-cards {
  display: grid;
  gap: 10px;
  margin-top: 12px;
}
#docqa-shell .docqa-source-card {
  display: grid;
  gap: 8px;
  padding: 12px;
  border: 1px solid #2c2c31;
  border-radius: 12px;
  background: #202023;
  color: #d4d4d8;
}
#docqa-shell .docqa-source-card:hover {
  border-color: #3f3f46;
  background: #242429;
}
#docqa-shell .docqa-source-card-head,
#docqa-shell .docqa-source-card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}
#docqa-shell .docqa-source-card-head { justify-content: space-between; }
#docqa-shell .docqa-source-card-name {
  min-width: 0;
  overflow-wrap: anywhere;
  color: #f4f4f5;
  font-size: 12px;
  font-weight: 650;
}
#docqa-shell .docqa-source-badge {
  flex: 0 0 auto;
  padding: 3px 7px;
  border-radius: 999px;
  color: #ffffff;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .04em;
}
#docqa-shell .docqa-source-badge-pdf { background: #7c3aed; }
#docqa-shell .docqa-source-badge-markdown { background: #0891b2; }
#docqa-shell .docqa-source-location {
  color: #93c5fd;
  font-size: 11px;
  line-height: 17px;
}
#docqa-shell .docqa-source-score {
  margin-left: auto;
  color: #71717a;
  font-size: 10px;
  white-space: nowrap;
}
#docqa-shell .docqa-source-excerpt {
  margin: 0;
  color: #d4d4d8;
  font-size: 12px;
  line-height: 19px;
  overflow-wrap: anywhere;
}
#docqa-shell .docqa-source-locator {
  margin: 0;
  padding-top: 7px;
  border-top: 1px solid #2c2c31;
  color: #71717a;
  font-size: 10px;
  line-height: 16px;
  overflow-wrap: anywhere;
}
#docqa-shell .docqa-source-locator code {
  color: #a1a1aa;
  white-space: normal;
  overflow-wrap: anywhere;
}
#docqa-shell .docqa-source-empty {
  display: grid;
  gap: 5px;
  margin-top: 12px;
  padding: 20px 14px;
  border: 1px dashed #3f3f46;
  border-radius: 12px;
  background: #18181b;
  text-align: center;
}
#docqa-shell .docqa-source-empty strong { color: #f4f4f5; font-size: 13px; }
#docqa-shell .docqa-source-empty span { color: #71717a; font-size: 11px; line-height: 17px; }
#docqa-shell .docqa-notes-card {
  display: grid;
  gap: 10px;
  padding: 14px;
  border-color: #3f3f46;
  background: #202023;
}
#docqa-shell .docqa-note-editor textarea { min-height: 116px; }
#docqa-shell .docqa-note-status { margin: 0; }
#docqa-shell .docqa-note-list {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #2c2c31;
}
#docqa-shell .docqa-notes-table .table-wrap {
  overflow-x: auto !important;
  border: 1px solid #2c2c31;
  border-radius: 10px;
}
#docqa-shell .docqa-notes-table table { min-width: 420px; }
#docqa-shell .docqa-notes-table th {
  background: #27272a !important;
  color: #a1a1aa !important;
  font-size: 10px !important;
}
#docqa-shell .docqa-notes-table td {
  background: #18181b !important;
  color: #d4d4d8 !important;
  font-size: 11px !important;
  overflow-wrap: anywhere;
}
#docqa-shell .docqa-note-selector { margin-top: 2px; }
@media (max-width: 760px) {
  #docqa-shell .docqa-source-card { padding: 11px; }
  #docqa-shell .docqa-source-card-head { align-items: flex-start; }
  #docqa-shell .docqa-source-score { display: none; }
  #docqa-shell .docqa-notes-table table { min-width: 360px; }
}

/* UI-HF5: responsive navigation and a real mobile context bottom sheet. */
#docqa-shell .docqa-mobile-actions,
#docqa-shell .docqa-mobile-nav-toggle,
#docqa-shell .docqa-mobile-context-toggle {
  display: none !important;
}

@media (min-width: 761px) and (max-width: 1180px) {
  #docqa-shell {
    padding-left: 14px;
    padding-right: 14px;
  }
  #docqa-workspace {
    grid-template-columns: 176px minmax(0, 1fr) !important;
    gap: 10px !important;
  }
  #docqa-shell .docqa-sidebar,
  #docqa-shell .docqa-library-view,
  #docqa-shell .docqa-session-view,
  #docqa-shell .docqa-inspector {
    min-height: 0;
  }
  #docqa-shell .docqa-sidebar { padding: 14px 10px; }
  #docqa-shell .docqa-library-view,
  #docqa-shell .docqa-session-view { padding: 14px; }
  #docqa-shell .docqa-inspector {
    grid-column: 2;
    padding: 0;
  }
  #docqa-shell .docqa-document-row {
    grid-template-columns: minmax(0, 1fr) 76px 92px 112px;
    gap: 8px;
  }
  #docqa-shell .docqa-hero-title { font-size: 20px; }
}

@media (max-width: 760px) {
  #docqa-shell {
    position: relative;
    padding: 0 10px 18px;
  }
  #docqa-shell .docqa-topbar {
    position: relative;
    z-index: 130;
    min-height: 64px;
    padding: 8px 2px;
    margin-bottom: 10px;
  }
  #docqa-shell .docqa-topbar-meta { display: none !important; }
  #docqa-shell .docqa-brand { min-width: 0; gap: 8px; }
  #docqa-shell .docqa-brand-copy { min-width: 0; }
  #docqa-shell .docqa-title .prose p { font-size: 17px !important; line-height: 24px !important; }
  #docqa-shell .docqa-kicker .prose p { font-size: 10px !important; line-height: 15px !important; }
  #docqa-shell .docqa-topbar-meta { gap: 5px; }
  #docqa-shell .docqa-topbar-chip.docqa-topbar-runtime { font-size: 10px; padding: 5px 7px; }
  #docqa-shell .docqa-mobile-actions {
    position: absolute;
    top: 10px;
    right: 12px;
    z-index: 130;
    display: flex !important;
    width: auto !important;
    min-width: 0 !important;
    height: 44px !important;
    flex: 0 0 auto;
    gap: 6px;
    align-items: center;
    background: transparent !important;
    border: 0 !important;
  }
  #docqa-shell .docqa-mobile-actions > .block,
  #docqa-shell .docqa-mobile-actions > .block > .wrap,
  #docqa-shell .docqa-mobile-actions .form,
  #docqa-shell .docqa-mobile-actions .styler {
    width: auto !important;
    min-width: 0 !important;
    height: 44px !important;
    min-height: 44px !important;
    padding: 0 !important;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
  }
  #docqa-shell .docqa-mobile-nav-toggle,
  #docqa-shell .docqa-mobile-context-toggle {
    display: block !important;
    width: 60px !important;
    max-width: 60px !important;
    min-width: 60px !important;
    flex: 0 0 auto;
    min-height: 44px;
    margin: 0 !important;
    padding: 0 !important;
    overflow: visible !important;
    background: transparent !important;
    border: 0 !important;
  }
  #docqa-shell .docqa-mobile-nav-toggle .wrap,
  #docqa-shell .docqa-mobile-context-toggle .wrap {
    min-height: 44px;
    border: 1px solid #3f3f46 !important;
    border-radius: 12px !important;
    background: #18181b !important;
  }
  #docqa-shell .docqa-mobile-nav-toggle label,
  #docqa-shell .docqa-mobile-context-toggle label {
    display: flex;
    min-height: 44px;
    align-items: center;
    justify-content: center;
    padding: 0 8px;
    color: #d4d4d8 !important;
    font-size: 11px !important;
    white-space: nowrap;
  }
  #docqa-shell .docqa-mobile-nav-toggle input,
  #docqa-shell .docqa-mobile-context-toggle input {
    accent-color: #2f80ed;
    position: absolute;
    width: 1px;
    height: 1px;
    opacity: 0;
  }
  #docqa-workspace {
    display: flex !important;
    flex-direction: column;
    gap: 10px !important;
  }
  #docqa-shell .docqa-sidebar {
    display: none !important;
    position: fixed !important;
    z-index: 120;
    top: 74px;
    left: 10px;
    width: min(292px, calc(100vw - 20px)) !important;
    max-height: calc(100vh - 88px);
    min-height: 0;
    overflow-y: auto;
    padding: 14px 12px;
    border: 1px solid #3f3f46;
    border-radius: 16px;
    background: #101012 !important;
    box-shadow: 0 20px 48px rgba(0, 0, 0, .55);
  }
  #docqa-shell:has(#docqa-mobile-nav-toggle input:checked)::after,
  #docqa-shell:has(#docqa-mobile-context-toggle input:checked)::after {
    content: "";
    position: fixed;
    z-index: 100;
    inset: 0;
    background: rgba(0, 0, 0, .62);
    pointer-events: none;
  }
  #docqa-shell:has(#docqa-mobile-nav-toggle input:checked) .docqa-sidebar {
    display: flex !important;
  }
  #docqa-shell .docqa-main-region {
    order: 1;
    width: 100% !important;
  }
  #docqa-shell .docqa-library-view,
  #docqa-shell .docqa-session-view {
    width: 100% !important;
    min-height: 0;
    padding: 12px;
  }
  #docqa-shell .docqa-session-view { height: auto; }
  #docqa-shell .docqa-library-header,
  #docqa-shell .docqa-session-header { display: block !important; }
  #docqa-shell .docqa-header-action { width: 100%; margin-top: 10px; }
  #docqa-shell .docqa-library-toolbar {
    display: grid !important;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
  #docqa-shell .docqa-library-toolbar .docqa-library-search {
    grid-column: 1 / -1;
    min-width: 0;
  }
  #docqa-shell .docqa-library-toolbar .docqa-library-filter { min-width: 0; }
  #docqa-shell .docqa-library-upload { display: block !important; }
  #docqa-shell .docqa-library-upload > .row { display: grid !important; gap: 8px; }
  #docqa-shell .docqa-library-upload .docqa-upload,
  #docqa-shell .docqa-library-upload .docqa-header-action { width: 100% !important; }
  #docqa-shell .docqa-document-row {
    grid-template-columns: minmax(0, 1fr) 74px 78px;
    gap: 6px 8px;
    min-height: 84px;
    padding: 10px;
  }
  #docqa-shell .docqa-document-main { grid-column: 1 / -1; }
  #docqa-shell .docqa-document-format,
  #docqa-shell .docqa-document-status,
  #docqa-shell .docqa-document-time { align-self: center; }
  #docqa-shell .docqa-document-time { text-align: right; }
  #docqa-shell .docqa-document-meta { white-space: normal; }
  #docqa-shell .docqa-timeline-panel { min-height: 360px; padding: 10px; }
  #docqa-shell .docqa-chatbot { min-height: 300px !important; }
  #docqa-shell .docqa-composer { padding: 10px 11px 9px; }
  #docqa-shell .docqa-composer-actions {
    display: grid !important;
    grid-template-columns: 1fr 1fr;
  }
  #docqa-shell .docqa-composer-hint { grid-column: 1 / -1; }
  #docqa-shell .docqa-composer-actions button { width: 100% !important; min-height: 44px; }
  #docqa-shell .docqa-inspector {
    display: none !important;
    position: fixed !important;
    z-index: 120;
    right: 0;
    bottom: 0;
    left: 0;
    width: 100% !important;
    max-height: 78vh;
    min-height: 0 !important;
    overflow-x: hidden;
    overflow-y: auto;
    border: 1px solid #3f3f46;
    border-radius: 18px 18px 0 0;
    background: #101012 !important;
    box-shadow: 0 -20px 48px rgba(0, 0, 0, .55);
  }
  #docqa-shell:has(#docqa-mobile-context-toggle input:checked) #sources-panel {
    display: flex !important;
  }
  #docqa-shell .docqa-inspector::before {
    content: "";
    display: block;
    width: 44px;
    height: 4px;
    margin: 8px auto 0;
    border-radius: 999px;
    background: #52525b;
  }
  #docqa-shell .docqa-inspector-header { padding: 12px 14px 0; }
  #docqa-shell .docqa-inspector-body { padding-bottom: 18px; }
  #docqa-shell #sources-panel .table-wrap,
  #docqa-shell #sources-panel .json-holder,
  #docqa-shell #sources-panel .gr-json {
    max-width: 100%;
    overflow-x: auto;
  }
  /* Gradio renders a hidden tab navigation alongside the accessible tablist.
     Keep only the accessible navigation visible and constrain it to the sheet. */
  #docqa-shell .docqa-context-tabs .tab-container.visually-hidden {
    display: none !important;
  }
  #docqa-shell .docqa-context-tabs .tab-container[role="tablist"] {
    position: relative !important;
    left: 0 !important;
    right: auto !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    overflow: hidden !important;
    display: flex !important;
  }
  #docqa-shell .docqa-context-tabs .tab-container[role="tablist"] button {
    flex: 0 0 auto;
    min-width: 72px;
  }
  #docqa-shell #sources-panel > .docqa-context-view {
    align-self: flex-start !important;
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    margin-inline-start: 0 !important;
  }
  #docqa-shell #sources-panel > .docqa-context-view .docqa-inspector-body {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
  }
  #docqa-shell .docqa-context-tabs .tabitem { padding: 10px 12px 14px; }
  #docqa-shell .docqa-source-card { padding: 11px; }
  #docqa-shell .docqa-notes-table table { width: 100%; min-width: 0; table-layout: fixed; }
  #docqa-shell .docqa-notes-table th,
  #docqa-shell .docqa-notes-table td { overflow-wrap: anywhere; word-break: break-word; }
  #docqa-shell .docqa-sidebar-footer { display: none; }

  /* HF-R3 must win over historical two-column toolbar rules at this breakpoint. */
  #docqa-shell .docqa-library-toolbar {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) !important;
    flex: 0 0 auto !important;
  }
  #docqa-shell .docqa-library-toolbar > .form,
  #docqa-shell .docqa-library-filter-bar,
  #docqa-shell .docqa-library-search { width: 100% !important; min-width: 0 !important; }
  #docqa-shell .docqa-library-search { grid-column: auto !important; }
  #docqa-shell .docqa-library-filter-bar { grid-template-columns: minmax(0, 1fr) !important; }
  #docqa-shell .docqa-library-filter-bar > .form {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important;
    width: 100% !important;
  }
  #docqa-shell .docqa-library-filter-bar > .form > :last-child { grid-column: 1 / -1; }
  #docqa-shell .docqa-library-count { justify-self: start; }
  #docqa-shell .docqa-document-row {
    grid-template-columns: minmax(0, 1fr) auto !important;
    gap: 7px 10px;
  }
  #docqa-shell .docqa-document-main { grid-column: 1 / -1; }
  #docqa-shell .docqa-document-format { display: none; }
  #docqa-shell .docqa-document-status { justify-self: start; }
  #docqa-shell .docqa-document-time { justify-self: end; }
}

/* HF-R4: a controlled, real-data context inspector.  The underlying Gradio
   JSON/Dataframe components keep their existing callbacks; these surfaces own
   the primary visual hierarchy. */
#docqa-shell .docqa-context-view,
#docqa-shell .docqa-context-view > .styler,
#docqa-shell .docqa-context-view .tabitem,
#docqa-shell .docqa-context-view .tabitem > .column {
  background: transparent !important;
}
#docqa-shell .docqa-context-tabs .tab-container[role="tablist"] {
  display: grid !important;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 3px;
  min-height: 40px;
  padding: 3px;
  overflow: hidden;
  border: 1px solid #27272a;
  border-radius: 12px;
  background: #09090b;
}
#docqa-shell .docqa-context-tabs .tab-container[role="tablist"] button {
  min-height: 32px;
  margin: 0 !important;
  padding: 0 10px !important;
  border: 0 !important;
  border-radius: 9px !important;
  background: transparent !important;
  color: #71717a !important;
  font-size: 12px !important;
  font-weight: 600;
}
#docqa-shell .docqa-context-tabs .tab-container[role="tablist"] button.selected,
#docqa-shell .docqa-context-tabs .tab-container[role="tablist"] button[aria-selected="true"] {
  background: #27282a !important;
  color: #f4f4f5 !important;
}
#docqa-shell .docqa-context-tabs .tabitem { padding: 14px 0 4px !important; }
#docqa-shell .docqa-source-cards { gap: 12px; margin-top: 0; }
#docqa-shell .docqa-source-card {
  gap: 9px;
  padding: 13px;
  border-color: #27272a;
  border-radius: 14px;
  background: #202023;
}
#docqa-shell .docqa-source-card:hover { border-color: #3f3f46; background: #242429; }
#docqa-shell .docqa-source-card-head { justify-content: space-between; }
#docqa-shell .docqa-source-card-primary { display: grid; gap: 5px; min-width: 0; }
#docqa-shell .docqa-source-card-name { color: #f4f4f5; font-size: 14px; line-height: 20px; }
#docqa-shell .docqa-source-location { color: #a1a1a9; font-size: 12px; line-height: 18px; }
#docqa-shell .docqa-source-badge { min-width: 78px; padding: 6px 10px; text-align: center; font-size: 11px; line-height: 18px; }
#docqa-shell .docqa-source-badge-pdf { background: #7c3aed; }
#docqa-shell .docqa-source-badge-markdown { background: #0ea5e9; }
#docqa-shell .docqa-source-score { display: none; }
#docqa-shell .docqa-source-expand { color: #a1a1a9; font-size: 11px; line-height: 17px; }
#docqa-shell .docqa-source-expand summary { cursor: pointer; list-style: none; }
#docqa-shell .docqa-source-expand summary::-webkit-details-marker { display: none; }
#docqa-shell .docqa-source-expand summary span { float: right; color: #d4d4d8; font-size: 16px; }
#docqa-shell .docqa-source-expand[open] summary { margin-bottom: 9px; color: #f4f4f5; }
#docqa-shell .docqa-source-excerpt { color: #d4d4d8; font-size: 12px; line-height: 19px; }
#docqa-shell .docqa-source-locator { color: #71717a; font-size: 10px; }
#docqa-shell .docqa-source-empty { min-height: 124px; margin-top: 0; padding: 28px 18px; }
#docqa-shell .docqa-note-editor {
  gap: 9px;
  padding: 13px;
  border: 1px solid #27272a;
  border-radius: 14px;
  background: #202023;
}
#docqa-shell .docqa-note-content textarea { min-height: 104px !important; resize: vertical; }
#docqa-shell .docqa-note-save button { min-height: 40px; }
#docqa-shell .docqa-note-update button { min-height: 38px; border-color: #3f3f46 !important; }
#docqa-shell .docqa-note-status { min-height: 20px; color: #a1a1aa !important; font-size: 11px; }
#docqa-shell .docqa-note-list-markup { margin-top: 12px; }
#docqa-shell .docqa-note-cards { display: grid; gap: 10px; }
#docqa-shell .docqa-note-card {
  display: grid;
  gap: 8px;
  padding: 13px;
  border: 1px solid #27272a;
  border-radius: 14px;
  background: #202023;
}
#docqa-shell .docqa-note-card-head,
#docqa-shell .docqa-note-card-meta { display: flex; align-items: center; justify-content: space-between; gap: 8px; min-width: 0; }
#docqa-shell .docqa-note-card-label { color: #f4f4f5; font-size: 12px; font-weight: 700; }
#docqa-shell .docqa-note-card time,
#docqa-shell .docqa-note-card-meta { color: #71717a; font-size: 10px; }
#docqa-shell .docqa-note-card-content { margin: 0; color: #d4d4d8; font-size: 12px; line-height: 19px; overflow-wrap: anywhere; }
#docqa-shell .docqa-note-card-meta { display: grid; gap: 3px; justify-content: start; overflow-wrap: anywhere; }
#docqa-shell .docqa-note-card-meta code { color: #a1a1aa; white-space: normal; overflow-wrap: anywhere; }
#docqa-shell .docqa-note-empty {
  min-height: 112px;
  padding: 20px 14px;
  place-items: center;
  border: 1px dashed #3f3f46;
  border-radius: 14px;
  color: #71717a;
  text-align: center;
}
#docqa-shell .docqa-note-empty strong { color: #f4f4f5; font-size: 13px; }
#docqa-shell .docqa-note-empty span { font-size: 11px; line-height: 17px; }
#docqa-shell .docqa-notes-table { display: none !important; }

@media (min-width: 761px) and (max-width: 1180px) {
  #docqa-shell .docqa-mobile-actions {
    position: absolute;
    top: 16px;
    right: 14px;
    z-index: 130;
    display: flex !important;
    width: 72px !important;
    min-width: 72px !important;
    height: 44px !important;
    align-items: center;
    background: transparent !important;
    border: 0 !important;
  }
  #docqa-shell .docqa-mobile-actions > .block,
  #docqa-shell .docqa-mobile-actions > .block > .wrap,
  #docqa-shell .docqa-mobile-actions .form,
  #docqa-shell .docqa-mobile-actions .styler {
    display: block !important;
    width: auto !important;
    min-width: 0 !important;
    height: 44px !important;
    min-height: 44px !important;
    overflow: visible !important;
  }
  #docqa-shell .docqa-mobile-nav-toggle { display: none !important; }
  #docqa-shell .docqa-mobile-context-toggle {
    display: block !important;
    width: 72px !important;
    min-width: 72px !important;
    min-height: 44px !important;
    margin: 0 !important;
    padding: 0 !important;
    border: 0 !important;
    background: transparent !important;
  }
  #docqa-shell .docqa-mobile-context-toggle .wrap {
    display: block !important;
    position: relative !important;
    width: 72px !important;
    min-height: 40px;
    border: 1px solid #3f3f46 !important;
    border-radius: 12px !important;
    background: #18181b !important;
  }
  #docqa-shell .docqa-mobile-context-toggle label {
    display: flex;
    min-height: 40px;
    align-items: center;
    justify-content: center;
    color: #d4d4d8 !important;
    font-size: 11px !important;
  }
  #docqa-shell .docqa-mobile-context-toggle input {
    position: absolute;
    width: 1px;
    height: 1px;
    opacity: 0;
    pointer-events: none;
  }
  #docqa-shell .docqa-inspector {
    display: none !important;
    position: fixed !important;
    z-index: 120;
    top: 82px;
    right: 14px;
    bottom: 14px;
    width: min(380px, calc(100vw - 28px)) !important;
    max-width: calc(100vw - 28px);
    min-height: 0 !important;
    overflow-x: hidden;
    overflow-y: auto;
    padding: 0 !important;
    border: 1px solid #3f3f46;
    border-radius: 18px;
    background: #101012 !important;
    box-shadow: -20px 0 48px rgba(0, 0, 0, .55);
  }
  #docqa-shell:has(#docqa-mobile-context-toggle input:checked)::after {
    content: "";
    position: fixed;
    z-index: 100;
    inset: 0;
    background: rgba(0, 0, 0, .42);
    pointer-events: none;
  }
  #docqa-shell:has(#docqa-mobile-context-toggle input:checked) #sources-panel { display: flex !important; }
  #docqa-shell .docqa-inspector-header { position: sticky; top: 0; z-index: 2; background: #101012; }
  #docqa-shell .docqa-context-tabs .tabitem { padding-bottom: 8px !important; }
  #docqa-shell .docqa-source-cards,
  #docqa-shell .docqa-note-cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 760px) {
  #docqa-shell .docqa-inspector { max-height: min(82vh, 720px); padding-bottom: env(safe-area-inset-bottom); }
  #docqa-shell .docqa-inspector-header { position: sticky; top: 0; z-index: 2; padding: 12px 14px 2px; background: #101012; }
  #docqa-shell .docqa-context-tabs .tab-container[role="tablist"] { min-height: 44px; }
  #docqa-shell .docqa-context-tabs .tab-container[role="tablist"] button { min-height: 36px; font-size: 13px !important; }
  #docqa-shell .docqa-context-tabs .tabitem { padding: 12px 0 18px !important; }
  #docqa-shell .docqa-source-card,
  #docqa-shell .docqa-note-card,
  #docqa-shell .docqa-note-editor { border-radius: 12px; }
  #docqa-shell .docqa-source-card-name { font-size: 13px; }
  #docqa-shell .docqa-source-badge { min-width: 72px; }
  #docqa-shell .docqa-note-content textarea { min-height: 112px !important; }
  #docqa-shell .docqa-note-save button,
  #docqa-shell .docqa-note-update button { min-height: 44px; }
}
"""


def _safe_error(exc: Exception) -> str:
    message = str(exc).strip() or type(exc).__name__
    message = re.sub(r"Bearer\s+\S+", "Bearer [REDACTED]", message, flags=re.IGNORECASE)
    message = re.sub(r"(api[\s_-]?key\s*[=:]\s*)\S+", r"\1[REDACTED]", message, flags=re.IGNORECASE)
    message = re.sub(r"(token\s*[=:]\s*)\S+", r"\1[REDACTED]", message, flags=re.IGNORECASE)
    return f"{type(exc).__name__}: {message}"


def _safe_error_text(message: str | None) -> str:
    if not message:
        return ""
    return _safe_error(RuntimeError(message))


def _empty_stats() -> dict[str, Any]:
    return {
        "period_start": None,
        "period_end": None,
        "session_count": 0,
        "question_count": 0,
        "answered_count": 0,
        "no_results_count": 0,
        "note_count": 0,
        "document_count": 0,
        "daily_events": [],
    }


def _format_document_location(item: Any) -> str:
    if item.format == "markdown":
        return f"{item.source_unit_count} 个章节/段落单元"
    return f"{item.pages_with_text} 页"


def _short_document_id(document_id: str) -> str:
    return document_id if len(document_id) <= 16 else f"{document_id[:12]}…"


def _format_source_summary(citations: list[dict[str, Any]]) -> str:
    if not citations:
        return "暂无可展示的来源。"
    lines = ["**当前回答来源**", "", "回答中的每个来源都保留原文定位；点击右侧原始数据可查看完整字段。"]
    for citation in citations:
        document_name = escape(str(citation.get("document_name", "未知文档")))
        locator = escape(str(citation.get("source_locator", "未知定位")))
        section = escape(str(citation.get("section", "") or ""))
        score = citation.get("score", "-")
        page_start = citation.get("page_start")
        page_end = citation.get("page_end")
        if page_start is not None:
            page_end = page_end or page_start
            location = f"PDF · 第 {page_start}–{page_end} 页"
        else:
            parsed_locator = urlparse(str(citation.get("source_locator", "")))
            query = parse_qs(parsed_locator.query or parsed_locator.fragment)
            paragraph = query.get("paragraph", [""])[0]
            line_range = query.get("lines", [""])[0]
            location_parts = ["Markdown"]
            if section:
                location_parts.append(section)
            if paragraph:
                location_parts.append(f"段落 {escape(paragraph)}")
            if line_range:
                location_parts.append(f"行 {escape(line_range)}")
            location = " · ".join(location_parts)
        content = escape(str(citation.get("content", "") or "").strip())
        excerpt = content[:240] + ("…" if len(content) > 240 else "")
        lines.append(
            f"\n### [{escape(str(citation.get('citation_id', '?')))}] {document_name}\n"
            f"`{location}` · 相似度 `{escape(str(score))}`\n\n"
            f"> {excerpt.replace(chr(10), '<br>')}\n\n"
            f"定位：`{locator}`"
        )
    return "\n".join(lines)


def _format_source_cards(citations: list[dict[str, Any]]) -> str:
    """Render citations as semantic inspector cards without changing citation data."""
    if not citations:
        return (
            '<div class="docqa-source-empty">'
            '<strong>暂无可展示的来源</strong>'
            '<span>完成一次问答后，PDF 页码或 Markdown 章节定位会显示在这里。</span>'
            '</div>'
        )

    cards: list[str] = []
    for citation in citations:
        locator_raw = str(citation.get("source_locator", "未知定位"))
        parsed_locator = urlparse(locator_raw)
        query = parse_qs(parsed_locator.query or parsed_locator.fragment)
        page_start = citation.get("page_start")
        page_end = citation.get("page_end") or page_start
        is_pdf = page_start is not None or parsed_locator.path.lower().endswith(".pdf")

        if is_pdf:
            location = f"第 {page_start or '-'} 页"
            if page_end and page_end != page_start:
                location = f"第 {page_start}–{page_end} 页"
            badge_class = "docqa-source-badge-pdf"
            format_label = "PDF"
        else:
            section = str(citation.get("section", "") or query.get("section", [""])[0])
            paragraph = query.get("paragraph", [""])[0]
            line_range = query.get("lines", [""])[0]
            location_parts = [part for part in [section, f"段落 {paragraph}" if paragraph else "", f"行 {line_range}" if line_range else ""] if part]
            location = " · ".join(location_parts) or "Markdown 原文定位"
            badge_class = "docqa-source-badge-markdown"
            format_label = "MARKDOWN"

        excerpt_text = str(citation.get("content", "") or "").strip()
        if len(excerpt_text) > 240:
            excerpt_text = excerpt_text[:240] + "…"
        document_name = escape(str(citation.get("document_name", "未知文档")))
        citation_id = escape(str(citation.get("citation_id", "来源")))
        score = escape(str(citation.get("score", "-")))
        location = escape(location)
        locator = escape(locator_raw)
        excerpt = escape(excerpt_text).replace("\n", "<br>")
        cards.append(
            f'<article class="docqa-source-card" data-citation-id="{citation_id}" '
            f'data-source-format="{format_label.lower()}">'
            '<div class="docqa-source-card-head">'
            f'<span class="docqa-source-badge {badge_class}">{format_label}</span>'
            f'<span class="docqa-source-score">相似度 {score}</span>'
            '</div>'
            '<div class="docqa-source-card-primary">'
            f'<span class="docqa-source-card-name">{document_name}</span>'
            f'<span class="docqa-source-location">{location}</span>'
            '</div>'
            '<details class="docqa-source-expand">'
            '<summary>展开片段和原始引用 <span aria-hidden="true">›</span></summary>'
            f'<p class="docqa-source-excerpt">{excerpt or "暂无来源片段"}</p>'
            f'<p class="docqa-source-locator">原始定位：<code>{locator}</code></p>'
            '</details>'
            '</article>'
        )
    return '<section class="docqa-source-cards" aria-label="回答来源">' + "".join(cards) + "</section>"


def _format_note_cards(notes: list[Any]) -> str:
    """Render the current session's real notes as compact inspector cards."""
    if not notes:
        return (
            '<section class="docqa-note-cards docqa-note-empty" aria-label="学习笔记列表">'
            '<strong>暂无学习笔记</strong>'
            '<span>完成问答后，可将当前理解保存为下一次复习的行动。</span>'
            '</section>'
        )

    cards: list[str] = []
    for note in notes:
        note_id = escape(str(getattr(note, "note_id", "笔记")))
        document_id = escape(str(getattr(note, "document_id", "") or "当前会话"))
        updated_at = escape(str(getattr(note, "updated_at", "未记录")))
        content_text = str(getattr(note, "content", "") or "").strip()
        if len(content_text) > 140:
            content_text = content_text[:140] + "…"
        content = escape(content_text).replace("\n", "<br>")
        cards.append(
            f'<article class="docqa-note-card" data-note-id="{note_id}">'
            '<div class="docqa-note-card-head">'
            '<span class="docqa-note-card-label">学习笔记</span>'
            f'<time>{updated_at}</time>'
            '</div>'
            f'<p class="docqa-note-card-content">{content or "（空笔记）"}</p>'
            '<div class="docqa-note-card-meta">'
            f'<span>文档 <code>{document_id}</code></span>'
            f'<span>笔记 <code>{note_id}</code></span>'
            '</div>'
            '</article>'
        )
    return '<section class="docqa-note-cards" aria-label="学习笔记列表">' + "".join(cards) + "</section>"


def _format_session_timeline(
    history: list[dict[str, Any]] | None,
    status: str = "等待提问",
    citations: list[dict[str, Any]] | dict[str, Any] | None = None,
) -> str:
    """Render real Chatbot history as the Figma-aligned session presentation layer."""
    safe_history = history if isinstance(history, list) else []
    safe_citations = citations if isinstance(citations, list) else []
    safe_status = escape(str(status or "等待提问"))

    if not safe_history:
        return (
            '<section class="docqa-timeline" aria-live="polite">'
            '<div class="docqa-timeline-separator">当前会话 · 问答记录</div>'
            '<div class="docqa-timeline-empty">'
            '<strong>从一个问题开始</strong>'
            '<span>回答、来源和可保存笔记会显示在这里。</span>'
            '</div>'
            f'<div class="docqa-timeline-state">{safe_status}</div>'
            '</section>'
        )

    message_markup: list[str] = ['<section class="docqa-timeline" aria-live="polite">']
    message_markup.append('<div class="docqa-timeline-separator">当前会话 · 问答记录</div>')
    last_index = len(safe_history) - 1
    for index, message in enumerate(safe_history):
        role = str(message.get("role", "assistant"))
        content = escape(str(message.get("content", "") or "")).replace("\n", "<br>")
        if role == "user":
            message_markup.append(
                '<article class="docqa-timeline-message docqa-timeline-user">'
                '<span class="docqa-timeline-role">问题</span>'
                f'<div class="docqa-timeline-content">{content}</div>'
                '</article>'
            )
            continue

        metadata = ""
        if index == last_index and safe_citations:
            source_count = len(safe_citations)
            metadata = (
                '<div class="docqa-timeline-meta">'
                f'<span>{source_count} 个来源</span>'
                '<span>可保存为笔记</span>'
                '</div>'
            )
        message_markup.append(
            '<article class="docqa-timeline-message docqa-timeline-assistant">'
            '<span class="docqa-timeline-role">回答</span>'
            f'<div class="docqa-timeline-content">{content}</div>'
            f'{metadata}'
            '</article>'
        )
    message_markup.append(f'<div class="docqa-timeline-state">{safe_status}</div>')
    message_markup.append('</section>')
    return "".join(message_markup)


def _format_document_detail_summary(detail: dict[str, Any]) -> str:
    if not detail:
        return "选择文档后，这里会显示完整 ID、格式、状态、定位规则和索引统计。"
    if detail.get("error") and not detail.get("document_id"):
        return f"**无法加载文档详情**\n\n`{escape(str(detail['error']))}`"
    document_name = escape(str(detail.get("document_name", "未命名文档")))
    document_id = escape(str(detail.get("document_id", "")))
    document_format = escape(str(detail.get("format", "unknown")).upper())
    status = escape(_document_status_label(str(detail.get("status", "unknown"))))
    content_hash = escape(str(detail.get("content_hash") or "未记录"))
    locator_scheme = escape(str(detail.get("source_locator_scheme") or "未记录"))
    location_units = escape(str(detail.get("pages_or_units") or 0))
    chunk_count = escape(str(detail.get("chunk_count") or 0))
    point_count = escape(str(detail.get("indexed_point_count") or 0))
    updated_at = escape(str(detail.get("updated_at") or "未记录"))
    error = escape(str(detail.get("error") or ""))
    location = escape(str(detail.get("note", "")))
    error_block = (
        f"\n\n**错误详情**\n\n<div class=\"docqa-detail-error\">{error}</div>"
        if error else ""
    )
    return (
        f"### {document_name}\n"
        f"<span class=\"docqa-detail-badge\">{document_format}</span> "
        f"<span class=\"docqa-detail-status\">{status}</span>\n\n"
        f"**document_id**\n`{document_id}`\n\n"
        f"**内容 hash**\n`{content_hash}`\n\n"
        f"**索引统计**\n\n"
        f"- 定位单元：`{location_units}`\n"
        f"- 分块：`{chunk_count}`\n"
        f"- Qdrant points：`{point_count}`\n"
        f"- 更新时间：`{updated_at}`\n\n"
        f"**定位方案**\n`{locator_scheme}`\n\n"
        f"{location}{error_block}"
    )


def _format_document_inspector(detail: dict[str, Any]) -> str:
    """Render the document-library inspector from real catalog metadata only."""
    if not detail:
        return (
            '<section class="docqa-inspector-empty">'
            '<strong>选择一个文档查看详情</strong>'
            '<span>完整 document_id、hash、索引统计和生命周期入口会显示在这里。</span>'
            '</section>'
        )
    if detail.get("error") and not detail.get("document_id"):
        return (
            '<section class="docqa-inspector-empty docqa-inspector-error">'
            '<strong>无法加载文档详情</strong>'
            f'<span>{escape(str(detail["error"]))}</span>'
            '</section>'
        )

    document_name = escape(str(detail.get("document_name", "未命名文档")))
    document_id = escape(str(detail.get("document_id", "未记录")))
    document_format = escape(str(detail.get("format", "unknown")).upper())
    status = str(detail.get("status", "unknown"))
    status_label = escape(_document_status_label(status))
    content_hash = escape(str(detail.get("content_hash") or "未记录"))
    locator_scheme = escape(str(detail.get("source_locator_scheme") or "未记录"))
    location_units = escape(str(detail.get("pages_or_units") or 0))
    chunk_count = escape(str(detail.get("chunk_count") or 0))
    point_count = escape(str(detail.get("indexed_point_count") or 0))
    updated_at = escape(str(detail.get("updated_at") or "未记录"))
    location_note = escape(str(detail.get("note") or ""))
    error = escape(str(detail.get("error") or ""))
    error_block = (
        '<div class="docqa-inspector-error-detail">'
        '<span>索引错误详情</span>'
        f'<p>{error}</p>'
        '</div>'
        if error
        else ""
    )
    return (
        '<section class="docqa-document-inspector-card">'
        '<span class="docqa-inspector-eyebrow">文档详情</span>'
        f'<h2 title="{document_name}">{document_name}</h2>'
        '<div class="docqa-inspector-badges">'
        f'<span class="docqa-detail-badge">{document_format}</span>'
        f'<span class="docqa-detail-status docqa-detail-status-{escape(status)}">{status_label}</span>'
        '</div>'
        '<dl class="docqa-inspector-metadata">'
        '<div><dt>document_id</dt>'
        f'<dd><code>{document_id}</code></dd></div>'
        '<div><dt>文件 hash</dt>'
        f'<dd><code>{content_hash}</code></dd></div>'
        '<div><dt>索引统计</dt>'
        f'<dd>{location_units} 个定位单元 · {chunk_count} 个分块 · {point_count} points</dd></div>'
        '<div><dt>来源定位</dt>'
        f'<dd>{locator_scheme}</dd></div>'
        '<div><dt>更新时间</dt>'
        f'<dd>{updated_at}</dd></div>'
        '</dl>'
        f'<p class="docqa-inspector-location-note">{location_note}</p>'
        f'{error_block}'
        '</section>'
    )

_DOCUMENT_STATUS_LABELS = {
    "indexed": "已索引",
    "archived": "已归档",
    "failed": "索引失败",
    "deleted": "已删除",
    "inconsistent": "需校验",
    "pending": "待处理",
    "validating": "校验中",
    "parsing": "解析中",
    "indexing": "索引中",
}


def _document_status_label(status: str) -> str:
    return _DOCUMENT_STATUS_LABELS.get(status, status or "未知状态")


class UIController:
    """Gradio 适配层；文档、问答和学习数据仍由业务服务负责。"""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings.from_env()
        self.store = SQLiteMemoryStore(self.settings.sqlite_path)
        self._scope_state = DocumentScopeState()
        self._learning: LearningService | None = None
        self._ingestion: DocumentIngestionService | None = None
        self._learning_indexer: QdrantIndexer | None = None
        self._ingestion_indexer: QdrantIndexer | None = None
        self._lifecycle: DocumentLifecycleService | None = None

    def _ensure_learning(self) -> LearningService:
        if self._learning is not None:
            return self._learning
        embedding = DashScopeEmbeddingProvider(
            model_name=self.settings.embedding_model,
            expected_dimension=self.settings.embedding_dimension,
            api_key=self.settings.embedding_api_key,
            base_url=self.settings.embedding_base_url,
            batch_size=self.settings.embedding_batch_size,
            max_retries=self.settings.embedding_max_retries,
            retry_backoff_seconds=self.settings.embedding_retry_backoff_seconds,
        )
        indexer = QdrantIndexer(
            self.settings.collection_name,
            self.settings.embedding_dimension,
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key,
            local_path=self.settings.qdrant_local_path,
            timeout=self.settings.qdrant_timeout,
        )
        try:
            chat = DeepSeekChatProvider(
                api_key=self.settings.deepseek_api_key,
                base_url=self.settings.deepseek_base_url,
                model_name=self.settings.deepseek_model,
                thinking=self.settings.deepseek_thinking,
                trust_env=self.settings.deepseek_trust_env,
                max_retries=self.settings.deepseek_max_retries,
                retry_backoff_seconds=self.settings.deepseek_retry_backoff_seconds,
            )
        except Exception:
            indexer.close()
            raise
        qa = QuestionAnswerService(self.settings, query_embedding=embedding, chat=chat, indexer=indexer)
        self._learning_indexer = indexer
        self._learning = LearningService(self.settings, qa_service=qa, store=self.store)
        return self._learning

    def _ensure_ingestion(self) -> DocumentIngestionService:
        if self._ingestion is not None:
            return self._ingestion
        embedding = DashScopeEmbeddingProvider(
            model_name=self.settings.embedding_model,
            expected_dimension=self.settings.embedding_dimension,
            api_key=self.settings.embedding_api_key,
            base_url=self.settings.embedding_base_url,
            batch_size=self.settings.embedding_batch_size,
            max_retries=self.settings.embedding_max_retries,
            retry_backoff_seconds=self.settings.embedding_retry_backoff_seconds,
        )
        indexer = QdrantIndexer(
            self.settings.collection_name,
            self.settings.embedding_dimension,
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key,
            local_path=self.settings.qdrant_local_path,
            timeout=self.settings.qdrant_timeout,
        )
        self._ingestion_indexer = indexer
        self._ingestion = DocumentIngestionService(
            self.settings,
            embedding=embedding,
            indexer=indexer,
            catalog=DocumentCatalogService(self.store),
        )
        return self._ingestion

    def initialize(self) -> tuple[str, str, list[dict[str, str]], dict[str, Any], list[list[str]], dict[str, Any]]:
        session = self.store.create_session()
        self._scope_state = self._scope_state.all_documents()
        return (
            session.session_id,
            "✅ 会话已就绪",
            [],
            {},
            self.document_table_rows(),
            self.store.stats().as_dict(),
        )

    def document_rows(self) -> list[list[str]]:
        return self._document_rows_for(self.store.list_documents())

    def _document_rows_for(self, documents: list[Any]) -> list[list[str]]:
        return [
            [
                item.document_name,
                item.format.upper(),
                _short_document_id(item.document_id),
                item.status,
                _format_document_location(item),
                str(item.chunk_count),
                str(item.indexed_point_count),
                item.source_locator_scheme,
                item.updated_at,
                _safe_error_text(item.error_message),
            ]
            for item in documents
        ]

    def _document_table_rows_for(self, documents: list[Any]) -> list[list[str]]:
        """Return the compact UI view; full metadata remains available in details."""
        return [
            [
                item.document_name,
                item.format.upper(),
                item.status,
                item.updated_at,
            ]
            for item in documents
        ]

    def document_table_rows(self) -> list[list[str]]:
        return self._document_table_rows_for(self.store.list_documents())

    def recent_document_rows(self, limit: int = 5) -> list[list[str]]:
        """Return the sidebar snapshot without changing the document catalog semantics."""
        return [
            [item.document_name, f"{item.format.upper()} · {item.status}"]
            for item in self.store.list_documents()[:limit]
        ]

    def recent_document_markup(self, limit: int = 5) -> str:
        """Render the real recent-document snapshot as a UI-only navigation list."""
        items = self.store.list_documents()[:limit]
        if not items:
            return '<div class="docqa-recent-empty">暂无最近文档。上传并索引文档后，会显示在这里。</div>'
        rows = []
        for item in items:
            name = escape(item.document_name)
            metadata = escape(f"{item.format.upper()} · {item.status}")
            rows.append(
                f'<div class="docqa-recent-item"><span class="docqa-recent-name">{name}</span>'
                f'<span class="docqa-recent-meta">{metadata}</span></div>'
            )
        return f'<div class="docqa-recent-list">{"".join(rows)}</div>'

    @staticmethod
    def _document_query_values(
        format_filter: str | None,
        status_filter: str | None,
        sort: str | None,
    ) -> tuple[str | None, str | None, str]:
        return (
            None if not format_filter or format_filter == "全部格式" else format_filter.lower(),
            None if not status_filter or status_filter == "全部状态" else status_filter,
            sort or "updated_desc",
        )

    def _filtered_documents(
        self,
        search: str | None,
        format_filter: str | None,
        status_filter: str | None,
        sort: str | None,
    ) -> list[Any]:
        document_format, document_status, document_sort = self._document_query_values(
            format_filter, status_filter, sort
        )
        return self.store.query_documents(
            search=search or "",
            format=document_format,
            status=document_status,
            sort=document_sort,
        )

    def document_library_markup(
        self,
        search: str | None = "",
        format_filter: str | None = "全部格式",
        status_filter: str | None = "全部状态",
        sort: str | None = "updated_desc",
    ) -> str:
        """Render the visible HF2 library rows; this is presentation-only HTML."""
        documents = self._filtered_documents(search, format_filter, status_filter, sort)
        if not documents:
            return (
                '<div class="docqa-library-empty">'
                '<strong>没有匹配的文档</strong>'
                '<span>调整搜索或筛选条件，或上传并索引一份 PDF / Markdown。</span>'
                '</div>'
            )
        rows: list[str] = [
            '<div class="docqa-document-list-columns">'
            '<span>文档</span><span>格式</span><span>状态</span><span>更新时间</span>'
            '</div>'
        ]
        for item in documents:
            name = escape(str(item.document_name))
            document_format = escape(str(item.format).upper())
            status = str(item.status or "unknown")
            status_label = escape(_document_status_label(status))
            updated_at = escape(str(item.updated_at or "未记录"))
            location = escape(_format_document_location(item))
            chunks = escape(str(item.chunk_count or 0))
            error_hint = ""
            if item.error_message:
                error_hint = f'<span class="docqa-document-error">{escape(_safe_error_text(item.error_message))}</span>'
            rows.append(
                f'<article class="docqa-document-row docqa-status-{escape(status)}">'
                f'<div class="docqa-document-main">'
                f'<strong class="docqa-document-name" title="{name}">{name}</strong>'
                f'<span class="docqa-document-meta">{location} · {chunks} 个分块{error_hint}</span>'
                f'</div>'
                f'<span class="docqa-document-format">{document_format}</span>'
                f'<span class="docqa-document-status docqa-status-pill">{status_label}</span>'
                f'<time class="docqa-document-time" title="{updated_at}">{updated_at}</time>'
                f'</article>'
            )
        return f'<div class="docqa-document-list">{"".join(rows)}</div>'

    def document_library_count(
        self,
        search: str | None = "",
        format_filter: str | None = "全部格式",
        status_filter: str | None = "全部状态",
        sort: str | None = "updated_desc",
    ) -> str:
        count = len(self._filtered_documents(search, format_filter, status_filter, sort))
        return f"{count} 个文档"

    def filter_documents(self, search: str | None, format_filter: str | None, status_filter: str | None, sort: str | None):
        documents = self._filtered_documents(search, format_filter, status_filter, sort)
        return self._document_rows_for(documents)

    def filter_document_table_rows(
        self, search: str | None, format_filter: str | None, status_filter: str | None, sort: str | None
    ):
        documents = self._filtered_documents(search, format_filter, status_filter, sort)
        return self._document_table_rows_for(documents)

    def document_details(self, document_id: str | None):
        if not document_id:
            return {}
        item = self.store.get_document(document_id)
        if item is None:
            return {"error": "文档不存在或已被移除"}
        return {
            "document_id": item.document_id,
            "document_name": item.document_name,
            "format": item.format,
            "status": item.status,
            "source_path": item.source_path,
            "content_hash": item.content_hash,
            "embedding": f"{item.embedding_model}/{item.embedding_dimension}",
            "source_locator_scheme": item.source_locator_scheme,
            "pages_or_units": item.pages_with_text if item.format == "pdf" else item.source_unit_count,
            "chunk_count": item.chunk_count,
            "indexed_point_count": item.indexed_point_count,
            "updated_at": item.updated_at,
            "error": _safe_error_text(item.error_message),
            "note": "PDF 使用页码定位；Markdown 使用章节/段落/行号定位。",
        }

    def document_detail_summary(self, document_id: str | None) -> str:
        return _format_document_detail_summary(self.document_details(document_id))

    def document_inspector_markup(self, document_id: str | None) -> str:
        return _format_document_inspector(self.document_details(document_id))

    def _ensure_lifecycle(self) -> DocumentLifecycleService:
        if self._lifecycle is None:
            self._lifecycle = DocumentLifecycleService(
                self.store,
                QdrantIndexer(
                    self.settings.collection_name, self.settings.embedding_dimension,
                    url=self.settings.qdrant_url, api_key=self.settings.qdrant_api_key,
                    local_path=self.settings.qdrant_local_path, timeout=self.settings.qdrant_timeout,
                ),
            )
        return self._lifecycle

    def _lifecycle_result(self, action: str, document_id: str | None, confirm: bool = True):
        try:
            service = self._ensure_lifecycle()
            if action == "archive":
                record = service.archive(document_id or "")
                message = f"✅ 已归档：{record.document_name}（Qdrant points 保留）"
            elif action == "unarchive":
                record = service.unarchive(document_id or "")
                message = f"✅ 已取消归档：{record.document_name}"
            elif action == "delete":
                record = service.delete(document_id or "", confirm=confirm)
                message = f"✅ 已删除向量并保留 SQLite tombstone：{record.document_name}"
            else:
                record = service.restore_deleted(document_id or "", reindex=lambda source: self._ensure_ingestion().index_document(source))
                message = f"✅ 已重新索引恢复：{record.document_name}"
            return message, self.document_rows(), gr.update(choices=self.document_choices()), self.document_details(record.document_id)
        except Exception as exc:
            return f"❌ 生命周期操作失败：{_safe_error(exc)}", self.document_rows(), gr.update(choices=self.document_choices()), self.document_details(document_id)

    def _lifecycle_table_result(self, action: str, document_id: str | None, confirm: bool = True):
        result = self._lifecycle_result(action, document_id, confirm)
        return result[0], self.document_table_rows(), result[2], result[3], _format_document_detail_summary(result[3])

    def document_choices(self) -> list[tuple[str, str]]:
        return [("全部文档", "")] + [
            (f"{item.document_name} · {item.format.upper()} · {item.status}", item.document_id)
            for item in self.store.list_documents()
        ]

    def refresh_document_choices(self):
        return gr.update(choices=self.document_choices())

    def default_document_detail_id(self) -> str:
        documents = self.store.list_documents()
        return documents[0].document_id if documents else ""

    def refresh_document_detail_selector(self):
        return gr.update(
            choices=self.document_choices(),
            value=self.default_document_detail_id(),
        )

    def _upsert_report_fallback(self, report: IndexReport, source: Path) -> None:
        if self.store.get_document(report.document_id) is not None:
            return
        self.store.upsert_document(
            document_id=report.document_id,
            document_name=report.document_name,
            source_path=report.source_path,
            pages_with_text=report.pages_with_text,
            chunk_count=report.chunk_count,
            indexed_point_count=report.indexed_point_count,
            status="indexed",
            format="markdown" if source.suffix.lower() in {".md", ".markdown"} else "pdf",
            content_hash=report.document_id,
            source_locator_scheme=(
                "markdown-heading-line-v1"
                if source.suffix.lower() in {".md", ".markdown"}
                else "pdf-page-v1"
            ),
            source_unit_count=report.pages_with_text,
        )

    def index_document(self, file_path: str | None):
        if not file_path:
            return "⚠️ 请先选择 PDF 或 Markdown 文件。", self.document_rows(), gr.update(choices=self.document_choices())
        source = Path(file_path)
        suffix = source.suffix.lower()
        if suffix not in SUPPORTED_DOCUMENT_SUFFIXES:
            return "❌ 仅支持 PDF、.md 和 .markdown 文件。", self.document_rows(), gr.update(choices=self.document_choices())
        if not source.is_file():
            return "❌ 文件不存在，请重新选择文件。", self.document_rows(), gr.update(choices=self.document_choices())
        try:
            if source.stat().st_size == 0:
                return "❌ 文件为空，无法建立索引。", self.document_rows(), gr.update(choices=self.document_choices())
            report = self._ensure_ingestion().index_document(source)
            self._upsert_report_fallback(report, source)
            status_text = "重复文档，未新增向量" if report.status == "duplicate" else "索引完成"
            message = (
                f"✅ {status_text}：{report.document_name} · {report.chunk_count} 个分块 · "
                f"{report.indexed_point_count} 个 points · {report.embedding_model}/{report.embedding_dimension}"
            )
            return message, self.document_rows(), gr.update(
                choices=self.document_choices(), value=report.document_id
            )
        except Exception as exc:
            return f"❌ 索引失败：{_safe_error(exc)}", self.document_rows(), gr.update(
                choices=self.document_choices()
            )

    def index_document_table(self, file_path: str | None):
        result = self.index_document(file_path)
        return result[0], self.document_table_rows(), result[2]

    def switch_document_scope(self, document_id: str | None):
        self._scope_state = self._scope_state.switch(document_id)
        label = document_id or "全部文档"
        return (
            f"已切换问答范围：`{label}`。当前回答、来源和临时上下文已清空，历史数据仍保留。",
            "等待提问",
            [],
            {},
            _format_source_cards([]),
            "",
            "",
            [],
            gr.update(choices=[], value=None),
            "",
        )

    def new_session(self):
        session = self.store.create_session()
        self._scope_state = self._scope_state.all_documents()
        return (
            session.session_id,
            "✅ 已切换到新会话",
            [],
            {},
            _format_source_cards([]),
            "等待提问",
            "",
            "",
            [],
            gr.update(choices=[], value=None),
            "",
            self.store.stats().as_dict(),
        )

    def _append_context(self, question: str, answer: str) -> None:
        context = list(self._scope_state.conversation_context)
        context.append({"question": question, "answer": answer})
        while len(context) > self.settings.memory_turn_limit:
            context.pop(0)
        while sum(len(item.get("question", "")) + len(item.get("answer", "")) for item in context) > self.settings.memory_context_max_chars:
            if len(context) <= 1:
                break
            context.pop(0)
        self._scope_state = DocumentScopeState(
            document_id=self._scope_state.document_id,
            conversation_context=tuple(context),
            citations=self._scope_state.citations,
            pending_note=self._scope_state.pending_note,
        )

    def ask(
        self,
        session_id: str,
        question: str,
        document_id: str | None,
        chat_history: list[dict[str, str]] | None,
    ):
        if not session_id:
            session_id = self.store.create_session().session_id
        if not question or not question.strip():
            return (
                session_id, chat_history or [], "⚠️ 问题不能为空。", {}, _format_source_cards([]), "", "", [], gr.update(choices=[]), self.store.stats().as_dict()
            )
        self._scope_state = self._scope_state.switch(document_id)
        try:
            response = self._ensure_learning().ask(
                session_id,
                question.strip(),
                document_id=document_id or None,
                conversation_context=list(self._scope_state.conversation_context),
            )
            history = list(chat_history or [])
            history.extend([
                {"role": "user", "content": response.question},
                {"role": "assistant", "content": response.answer},
            ])
            turn = self.store.list_turns(session_id)[-1]
            citations = [citation.as_dict() for citation in response.citations]
            locator = response.citations[0].source_locator if response.citations else ""
            self._scope_state = DocumentScopeState(
                document_id=self._scope_state.document_id,
                conversation_context=self._scope_state.conversation_context,
                citations=tuple(citations),
                pending_note="",
            )
            if response.status == "answered":
                self._append_context(response.question, response.answer)
                status = "✅ 已回答"
            else:
                status = "ℹ️ 当前文档范围没有足够依据"
            note_choices = [(note.content[:42], note.note_id) for note in self.store.list_notes(session_id)]
            return (
                session_id,
                history,
                status,
                citations,
                _format_source_cards(citations),
                turn.turn_id,
                locator,
                self.note_rows(session_id),
                gr.update(choices=note_choices, value=None),
                self.store.stats().as_dict(),
            )
        except Exception as exc:
            return (
                session_id,
                chat_history or [],
                f"❌ 问答失败：{_safe_error(exc)}",
                {},
                _format_source_cards([]),
                "",
                "",
                self.note_rows(session_id),
                gr.update(choices=[]),
                self.store.stats().as_dict(),
            )

    def note_rows(self, session_id: str | None) -> list[list[str]]:
        return [
            [note.note_id, note.content, note.document_id or "", note.updated_at]
            for note in self.store.list_notes(session_id)
        ]

    def note_list_markup(self, session_id: str | None) -> str:
        """Presentation-only note cards; storage and session isolation stay in the store."""
        return _format_note_cards(self.store.list_notes(session_id))

    def save_note(
        self,
        session_id: str,
        turn_id: str,
        document_id: str | None,
        source_locator: str,
        content: str,
    ):
        if not session_id or not turn_id:
            return "⚠️ 请先完成一次问答，再保存笔记。", [], gr.update(choices=[]), content
        try:
            note = self._ensure_learning().create_note(
                session_id,
                content,
                turn_id=turn_id,
                document_id=document_id or None,
                source_locator=source_locator or None,
            )
            choices = [(note.content[:42], note.note_id) for note in self.store.list_notes(session_id)]
            return f"✅ 笔记已保存：`{note.note_id}`", self.note_rows(session_id), gr.update(choices=choices, value=note.note_id), ""
        except Exception as exc:
            return f"❌ 笔记保存失败：{_safe_error(exc)}", self.note_rows(session_id), gr.update(choices=[]), content

    def load_note(self, note_id: str | None, session_id: str | None):
        if not note_id or not session_id:
            return ""
        for note in self.store.list_notes(session_id):
            if note.note_id == note_id:
                return note.content
        return ""

    def update_note(self, note_id: str, content: str, session_id: str):
        if not note_id:
            return "⚠️ 请先选择笔记。", self.note_rows(session_id)
        try:
            note = self._ensure_learning().update_note(note_id, content)
            return f"✅ 笔记已更新：`{note.note_id}`", self.note_rows(session_id)
        except Exception as exc:
            return f"❌ 笔记更新失败：{_safe_error(exc)}", self.note_rows(session_id)

    def refresh_stats(self, start_date: str | None, end_date: str | None):
        try:
            stats = self.store.stats(start_date or None, end_date or None).as_dict()
            return stats, self.store.report(start_date or None, end_date or None)
        except Exception as exc:
            return {"error": _safe_error(exc)}, {"error": _safe_error(exc)}

    def close(self) -> None:
        if self._learning_indexer:
            self._learning_indexer.close()
        if self._ingestion_indexer:
            self._ingestion_indexer.close()
        if self._lifecycle:
            self._lifecycle.indexer.close()
        self.store.close()


def build_app(controller: UIController | None = None) -> gr.Blocks:
    controller = controller or UIController()
    initial_document_detail_id = controller.default_document_detail_id()

    def show_library():
        return (
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(variant="primary"),
            gr.update(variant="secondary"),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(value=False),
            gr.update(value=False),
            gr.update(value="文档详情"),
            gr.update(value="完整标识、索引统计、错误详情和生命周期操作"),
        )

    def show_session():
        return (
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(variant="secondary"),
            gr.update(variant="primary"),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(value=False),
            gr.update(value=False),
            gr.update(value="上下文检查器"),
            gr.update(value="在学习会话查看来源和笔记；文档库可查看完整元数据。"),
        )

    def show_reports():
        return (
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(variant="secondary"),
            gr.update(variant="secondary"),
            gr.update(open=True),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(value=False),
            gr.update(value=False),
            gr.update(value="学习统计与报告"),
            gr.update(value="查看学习活动统计和确定性报告。"),
        )

    def initial_view():
        has_documents = bool(controller.store.list_documents())
        return (
            gr.update(visible=not has_documents),
            gr.update(visible=has_documents),
            gr.update(variant="primary" if not has_documents else "secondary"),
            gr.update(variant="primary" if has_documents else "secondary"),
            gr.update(visible=has_documents),
            gr.update(visible=not has_documents),
            gr.update(value=False),
            gr.update(value=False),
            gr.update(value="上下文检查器" if has_documents else "文档详情"),
            gr.update(
                value=(
                    "在学习会话查看来源和笔记；文档库可查看完整元数据。"
                    if has_documents
                    else "完整标识、索引统计、错误详情和生命周期操作"
                )
            ),
        )

    def mirror_rows(rows):
        return rows

    with gr.Blocks(title="文档学习助手", css=APP_CSS) as demo:
        session_state = gr.State("")
        current_turn_state = gr.State("")
        source_locator_state = gr.State("")

        with gr.Column(elem_id="docqa-shell"):
            with gr.Row(elem_classes=["docqa-topbar"]):
                with gr.Row(elem_classes=["docqa-brand"], scale=5):
                    gr.Markdown("▦", elem_classes=["docqa-brand-mark"])
                    with gr.Column(elem_classes=["docqa-brand-copy"]):
                        gr.Markdown("文档学习助手", elem_classes=["docqa-title"])
                        gr.Markdown("阅读 · 提问 · 复习", elem_classes=["docqa-kicker"])
                with gr.Row(elem_classes=["docqa-topbar-meta"], scale=4):
                    topbar_scope = gr.Markdown("全部文档", elem_classes=["docqa-topbar-chip", "docqa-topbar-scope"])
                    gr.Markdown("本地运行", elem_classes=["docqa-topbar-chip", "docqa-topbar-runtime"])
                    gr.Markdown("文", elem_classes=["docqa-topbar-chip", "docqa-topbar-language"])

            with gr.Row(elem_classes=["docqa-mobile-actions"], scale=0):
                mobile_nav_toggle = gr.Checkbox(
                    label="菜单",
                    value=False,
                    interactive=True,
                    elem_id="docqa-mobile-nav-toggle",
                    elem_classes=["docqa-mobile-nav-toggle"],
                )
                mobile_context_toggle = gr.Checkbox(
                    label="上下文",
                    value=False,
                    interactive=True,
                    elem_id="docqa-mobile-context-toggle",
                    elem_classes=["docqa-mobile-context-toggle"],
                )

            with gr.Row(elem_id="docqa-workspace", elem_classes=["docqa-workspace"]):
                with gr.Column(scale=0, min_width=220, elem_classes=["docqa-sidebar"], elem_id="docqa-sidebar"):
                    gr.Markdown("空间", elem_classes=["docqa-section-kicker"])
                    with gr.Column(elem_classes=["docqa-space-nav"]):
                        nav_library_button = gr.Button("▦  文档库", variant="secondary", elem_classes=["docqa-nav-item"])
                        nav_session_button = gr.Button("◌  学习会话", variant="secondary", elem_classes=["docqa-nav-item"])
                        nav_context_button = gr.Button("⌁  来源与笔记", variant="secondary", elem_classes=["docqa-nav-item"])
                        nav_reports_button = gr.Button("▥  学习报告", variant="secondary", elem_classes=["docqa-nav-item"])
                    gr.Markdown(
                        "来源与笔记会围绕当前回答显示；学习报告在工作区底部展开。",
                        elem_classes=["docqa-nav-note"],
                    )
                    gr.Markdown("最近文档", elem_classes=["docqa-recent-title"])
                    recent_documents = gr.HTML(
                        value=controller.recent_document_markup(),
                        elem_classes=["docqa-recent-block"],
                    )
                    gr.Markdown(
                        "<strong>本地知识工作台</strong><br>PDF / Markdown · 单用户",
                        elem_classes=["docqa-sidebar-footer"],
                    )

                with gr.Column(scale=1, elem_classes=["docqa-main-region"]):
                    with gr.Group(visible=False, elem_id="library-view", elem_classes=["docqa-library-view"]) as library_view:
                        with gr.Row(elem_classes=["docqa-library-header"]):
                            with gr.Column(scale=5):
                                gr.Markdown("文档库", elem_classes=["docqa-eyebrow"])
                                gr.Markdown("整理资料，建立可追溯的学习空间", elem_classes=["docqa-hero-title"])
                                gr.Markdown(
                                    "搜索、筛选和查看文档；问答范围与文档列表彼此独立。",
                                    elem_classes=["docqa-hero-copy"],
                                )
                            with gr.Column(elem_classes=["docqa-library-header-actions"]):
                                upload = gr.File(
                                    label="上传文档",
                                    file_types=[".pdf", ".md", ".markdown"],
                                    type="filepath",
                                    elem_classes=["docqa-upload", "docqa-upload-trigger"],
                                )
                                index_button = gr.Button(
                                    "开始索引",
                                    elem_classes=["docqa-library-index"],
                                )
                                document_status = gr.Markdown(
                                    "等待选择 PDF 或 Markdown",
                                    elem_classes=["docqa-status", "docqa-library-status"],
                                )
                        with gr.Column(elem_classes=["docqa-library-toolbar"]):
                            document_search = gr.Textbox(
                                label="搜索",
                                placeholder="搜索文档名或 document_id",
                                show_label=False,
                                elem_classes=["docqa-library-search", "docqa-library-search-field"],
                            )
                            with gr.Row(elem_classes=["docqa-library-filter-bar"]):
                                document_format = gr.Dropdown(
                                    ["全部格式", "PDF", "MARKDOWN"],
                                    value="全部格式",
                                    label="格式",
                                    elem_classes=["docqa-library-filter", "docqa-library-filter-control"],
                                )
                                document_status_filter = gr.Dropdown(
                                    ["全部状态", "indexed", "archived", "failed", "deleted", "inconsistent"],
                                    value="全部状态",
                                    label="状态",
                                    elem_classes=["docqa-library-filter", "docqa-library-filter-control"],
                                )
                                document_sort = gr.Dropdown(
                                    [
                                        ("最近更新", "updated_desc"),
                                        ("最早更新", "updated_asc"),
                                        ("文档名", "name_asc"),
                                    ],
                                    value="updated_desc",
                                    label="排序",
                                    elem_classes=["docqa-library-filter", "docqa-library-filter-control"],
                                )
                                library_count = gr.Markdown(
                                    controller.document_library_count(),
                                    elem_classes=["docqa-library-count"],
                                )
                        with gr.Row(elem_classes=["docqa-library-list-heading"]):
                            gr.Markdown("文档列表", elem_classes=["docqa-eyebrow"])
                            gr.Markdown("文档名 · 格式 · 状态 · 更新时间", elem_classes=["docqa-library-count"])
                        document_library = gr.HTML(
                            value=controller.document_library_markup(),
                            elem_classes=["docqa-document-library"],
                        )
                        document_table = gr.Dataframe(
                            headers=["文档", "格式", "状态", "更新时间"],
                            datatype=["str"] * 4,
                            value=[],
                            interactive=False,
                            wrap=True,
                            line_breaks=True,
                            column_widths=["2fr", "0.8fr", "1fr", "1.3fr"],
                            show_fullscreen_button=False,
                            show_copy_button=False,
                            show_row_numbers=False,
                            label=None,
                            visible=False,
                            elem_classes=["docqa-document-table", "docqa-document-table-compat"],
                        )
                        gr.Markdown(
                            "点击学习会话进入问答；完整 document_id、hash、定位方案和错误详情在右侧检查器查看。",
                            elem_classes=["docqa-hero-copy"],
                        )
                    with gr.Group(visible=True, elem_id="session-view", elem_classes=["docqa-session-view"]) as session_view:
                        with gr.Row(elem_classes=["docqa-session-header"]):
                            with gr.Column(elem_classes=["docqa-session-intro"]):
                                gr.Markdown("学习会话", elem_classes=["docqa-eyebrow"])
                                gr.Markdown("把问题问清楚，再回到原文", elem_classes=["docqa-hero-title"])
                                gr.Markdown(
                                    "回答必须绑定当前文档范围，并保留可追溯来源。",
                                    elem_classes=["docqa-hero-copy"],
                                )
                                with gr.Row(elem_classes=["docqa-session-chip-row"]):
                                    gr.Markdown("范围 · 当前文档", elem_classes=["docqa-chip"])
                                    session_status = gr.Markdown("正在初始化", elem_classes=["docqa-status"])
                            new_session_button = gr.Button(
                                "+ 新会话",
                                elem_classes=["docqa-header-action"],
                            )
                        with gr.Column(elem_classes=["docqa-session-workspace"]):
                            with gr.Column(elem_classes=["docqa-session-scope"]):
                                with gr.Row(elem_classes=["docqa-scope-heading"]):
                                    gr.Markdown("当前问答范围", elem_classes=["docqa-eyebrow"])
                                    gr.Markdown("检索边界", elem_classes=["docqa-session-meta"])
                                document_filter = gr.Dropdown(
                                    choices=[("全部文档", "")],
                                    label="当前问答范围",
                                    value="",
                                    show_label=False,
                                    elem_classes=["docqa-session-filter"],
                                )
                                scope_status = gr.Markdown(
                                    "当前范围：全部文档",
                                    elem_classes=["docqa-status", "docqa-scope"],
                                )
                            with gr.Column(elem_classes=["docqa-timeline-panel"]):
                                with gr.Row(elem_classes=["docqa-timeline-heading"]):
                                    gr.Markdown("对话时间线", elem_classes=["docqa-eyebrow"])
                                    gr.Markdown("问题 · 回答 · 来源", elem_classes=["docqa-session-meta"])
                                chatbot = gr.Chatbot(
                                    label="问答记录",
                                    type="messages",
                                    placeholder="先从一个问题开始；回答会显示在这里。",
                                    show_label=False,
                                    visible=False,
                                    elem_classes=["docqa-chatbot"],
                                )
                                conversation_timeline = gr.HTML(
                                    _format_session_timeline([], "等待提问", {}),
                                    elem_classes=["docqa-timeline-render"],
                                )
                                answer_status = gr.Markdown(
                                    "等待提问",
                                    visible=False,
                                    elem_classes=["docqa-answer-status", "docqa-status"],
                                )
                            with gr.Column(elem_classes=["docqa-composer"]):
                                with gr.Row(elem_classes=["docqa-composer-heading"]):
                                    gr.Markdown("向当前范围提问", elem_classes=["docqa-eyebrow"])
                                    gr.Markdown("回答会保留可追溯来源", elem_classes=["docqa-session-meta"])
                                question = gr.Textbox(
                                    label="向当前范围提问",
                                    placeholder="输入问题，例如：这份材料的核心章节如何推进？",
                                    lines=1,
                                    show_label=False,
                                    elem_classes=["docqa-composer-input"],
                                )
                                with gr.Row(elem_classes=["docqa-composer-actions"]):
                                    gr.Markdown(
                                        "⌕  Enter 提交 · Shift + Enter 换行",
                                        elem_classes=["docqa-session-meta", "docqa-composer-hint"],
                                    )
                                    ask_button = gr.Button("↑", variant="primary", elem_classes=["docqa-composer-send"])
                                    clear_button = gr.Button("清空", elem_classes=["docqa-composer-clear"])

                with gr.Column(scale=0, min_width=340, elem_classes=["docqa-inspector"], elem_id="sources-panel") as sources_panel:
                    with gr.Column(elem_classes=["docqa-inspector-header"]):
                        inspector_title = gr.Markdown("上下文检查器", elem_classes=["docqa-hero-title"])
                        inspector_copy = gr.Markdown(
                            "在文档库查看元数据；在学习会话查看来源和笔记",
                            elem_classes=["docqa-hero-copy"],
                        )
                    with gr.Group(visible=True, elem_classes=["docqa-context-view"]) as context_view:
                      with gr.Column(elem_classes=["docqa-inspector-body"]):
                        with gr.Tabs(elem_classes=["docqa-context-tabs"]):
                            with gr.Tab("来源", id="sources-tab"):
                                source_summary = gr.HTML(
                                    _format_source_cards([]),
                                    elem_classes=["docqa-source-summary"],
                                )
                                with gr.Accordion(
                                    "查看原始引用数据",
                                    open=False,
                                    elem_classes=["docqa-raw-source"],
                                ):
                                    sources = gr.JSON(label=None, value={})
                            with gr.Tab("笔记", id="notes-tab"):
                                with gr.Column(elem_classes=["docqa-notes-card", "docqa-note-editor"]):
                                    gr.Markdown("学习笔记", elem_classes=["docqa-eyebrow"])
                                    note_content = gr.Textbox(
                                        label="笔记内容",
                                        lines=4,
                                        placeholder="记录你的理解、疑问或下一步行动",
                                        elem_classes=["docqa-note-content"],
                                    )
                                    save_note_button = gr.Button(
                                        "保存为笔记",
                                        variant="primary",
                                        elem_classes=["docqa-note-save"],
                                    )
                                    note_status = gr.Markdown("等待保存笔记", elem_classes=["docqa-status", "docqa-note-status"])
                                    note_selector = gr.Dropdown(
                                        choices=[],
                                        label="选择已有笔记",
                                        elem_classes=["docqa-note-selector"],
                                    )
                                    update_note_button = gr.Button(
                                        "更新选中笔记",
                                        elem_classes=["docqa-note-update"],
                                    )
                                note_list_markup = gr.HTML(
                                    controller.note_list_markup(None),
                                    elem_classes=["docqa-note-list-markup"],
                                )
                                notes_table = gr.Dataframe(
                                    headers=["笔记 ID", "内容", "文档", "更新时间"],
                                    datatype=["str"] * 4,
                                    value=[],
                                    interactive=False,
                                    wrap=True,
                                    label="笔记列表",
                                    visible=False,
                                    elem_classes=["docqa-notes-table", "docqa-note-list"],
                                )
                    with gr.Group(visible=False, elem_id="document-inspector", elem_classes=["docqa-document-inspector"]) as document_inspector:
                        with gr.Column(elem_classes=["docqa-inspector-body"]):
                            document_detail_selector = gr.Dropdown(
                                choices=controller.document_choices(),
                                label="查看文档详情（不改变问答范围）",
                                value=initial_document_detail_id,
                                elem_classes=["docqa-detail-selector", "docqa-detail-selector-controlled"],
                            )
                            document_inspector_markup = gr.HTML(
                                controller.document_inspector_markup(initial_document_detail_id),
                                elem_classes=["docqa-document-inspector-markup"],
                            )
                            document_detail_summary = gr.Markdown(
                                controller.document_detail_summary(initial_document_detail_id),
                                visible=False,
                                elem_classes=["docqa-detail-summary"],
                            )
                            document_detail = gr.JSON(
                                label="完整 document_id、hash、索引统计和错误详情",
                                value=controller.document_details(initial_document_detail_id),
                                visible=False,
                                elem_classes=["docqa-document-detail"],
                            )
                            with gr.Column(elem_classes=["docqa-danger-zone"]):
                                gr.Markdown(
                                    "**危险操作区**\n\n归档保留向量；删除会移除对应 Qdrant points，并保留 SQLite 历史记录。",
                                    elem_classes=["docqa-danger-copy"],
                                )
                                with gr.Row(elem_classes=["docqa-actions-row"]):
                                    archive_button = gr.Button("归档")
                                    unarchive_button = gr.Button("取消归档")
                                with gr.Row(elem_classes=["docqa-actions-row"]):
                                    restore_button = gr.Button("重新索引恢复")
                                    delete_button = gr.Button("删除文档", variant="stop")
                                delete_confirm = gr.Checkbox(
                                    label="确认删除 Qdrant points；SQLite 历史保留",
                                    value=False,
                                )

            with gr.Accordion("学习统计与报告", open=False, elem_classes=["docqa-stats"]) as stats_section:
                with gr.Row():
                    start_date = gr.Textbox(label="开始日期", placeholder="YYYY-MM-DD")
                    end_date = gr.Textbox(label="结束日期", placeholder="YYYY-MM-DD")
                    stats_button = gr.Button("刷新统计")
                stats_json = gr.JSON(label="统计", value=_empty_stats())
                report_json = gr.JSON(label="确定性报告", value={})

        clear_button.click(lambda: "", outputs=[question])
        load_event = demo.load(
            controller.initialize,
            outputs=[session_state, session_status, chatbot, sources, document_table, stats_json],
        )
        load_event.then(
            initial_view,
            outputs=[
                library_view,
                session_view,
                nav_library_button,
                nav_session_button,
                context_view,
                document_inspector,
                mobile_nav_toggle,
                mobile_context_toggle,
                inspector_title,
                inspector_copy,
            ],
        )
        load_event.then(
            _format_session_timeline,
            inputs=[chatbot, answer_status, sources],
            outputs=[conversation_timeline],
        )
        load_event.then(controller.note_list_markup, inputs=[session_state], outputs=[note_list_markup])
        demo.load(controller.refresh_document_choices, outputs=[document_filter])
        detail_load_event = demo.load(
            controller.refresh_document_detail_selector,
            outputs=[document_detail_selector],
        )
        detail_load_event.then(
            controller.document_inspector_markup,
            inputs=[document_detail_selector],
            outputs=[document_inspector_markup],
        )
        demo.load(controller.document_library_markup, outputs=[document_library])
        demo.load(controller.document_library_count, outputs=[library_count])
        for control in [document_search, document_format, document_status_filter, document_sort]:
            filter_event = control.change(
                controller.filter_document_table_rows,
                inputs=[document_search, document_format, document_status_filter, document_sort],
                outputs=[document_table],
            )
            filter_event.then(
                controller.document_library_markup,
                inputs=[document_search, document_format, document_status_filter, document_sort],
                outputs=[document_library],
            )
            filter_event.then(
                controller.document_library_count,
                inputs=[document_search, document_format, document_status_filter, document_sort],
                outputs=[library_count],
            )
        index_event = index_button.click(
            controller.index_document_table,
            inputs=[upload],
            outputs=[document_status, document_table, document_filter],
            show_progress="full",
        )
        index_scope_event = index_event.then(
            controller.switch_document_scope,
            inputs=[document_filter],
            outputs=[scope_status, answer_status, chatbot, sources, source_summary, current_turn_state, source_locator_state, notes_table, note_selector, note_content],
        )
        index_scope_event.then(
            _format_session_timeline,
            inputs=[chatbot, answer_status, sources],
            outputs=[conversation_timeline],
        )
        index_detail_event = index_event.then(
            controller.refresh_document_detail_selector,
            outputs=[document_detail_selector],
        )
        index_detail_event.then(
            controller.document_details,
            inputs=[document_detail_selector],
            outputs=[document_detail],
        )
        index_detail_event.then(
            controller.document_detail_summary,
            inputs=[document_detail_selector],
            outputs=[document_detail_summary],
        )
        index_detail_event.then(
            controller.document_inspector_markup,
            inputs=[document_detail_selector],
            outputs=[document_inspector_markup],
        )
        index_event.then(controller.recent_document_markup, outputs=[recent_documents])
        index_event.then(controller.document_library_markup, outputs=[document_library])
        index_event.then(controller.document_library_count, outputs=[library_count])
        scope_change_event = document_filter.change(
            controller.switch_document_scope,
            inputs=[document_filter],
            outputs=[scope_status, answer_status, chatbot, sources, source_summary, current_turn_state, source_locator_state, notes_table, note_selector, note_content],
        )
        scope_change_event.then(
            _format_session_timeline,
            inputs=[chatbot, answer_status, sources],
            outputs=[conversation_timeline],
        )
        scope_change_event.then(controller.note_list_markup, inputs=[session_state], outputs=[note_list_markup])
        document_filter.change(
            lambda value: f"范围 · {value or '全部文档'}",
            inputs=[document_filter],
            outputs=[topbar_scope],
        )
        document_detail_selector.change(controller.document_details, inputs=[document_detail_selector], outputs=[document_detail])
        document_detail_selector.change(controller.document_detail_summary, inputs=[document_detail_selector], outputs=[document_detail_summary])
        document_detail_selector.change(
            controller.document_inspector_markup,
            inputs=[document_detail_selector],
            outputs=[document_inspector_markup],
        )
        lifecycle_outputs = [document_status, document_table, document_filter, document_detail, document_detail_summary]
        for action_button, action in [
            (archive_button, "archive"),
            (unarchive_button, "unarchive"),
            (restore_button, "restore"),
        ]:
            lifecycle_event = action_button.click(
                lambda document_id, selected_action=action: controller._lifecycle_table_result(selected_action, document_id),
                inputs=[document_detail_selector],
                outputs=lifecycle_outputs,
            )
            lifecycle_detail_event = lifecycle_event.then(
                controller.refresh_document_detail_selector,
                outputs=[document_detail_selector],
            )
            lifecycle_detail_event.then(
                controller.document_inspector_markup,
                inputs=[document_detail_selector],
                outputs=[document_inspector_markup],
            )
            lifecycle_event.then(controller.recent_document_markup, outputs=[recent_documents])
            lifecycle_event.then(controller.document_library_markup, outputs=[document_library])
            lifecycle_event.then(controller.document_library_count, outputs=[library_count])
        delete_event = delete_button.click(
            lambda document_id, confirm: controller._lifecycle_table_result("delete", document_id, confirm),
            inputs=[document_detail_selector, delete_confirm],
            outputs=lifecycle_outputs,
        )
        delete_detail_event = delete_event.then(
            controller.refresh_document_detail_selector,
            outputs=[document_detail_selector],
        )
        delete_detail_event.then(
            controller.document_inspector_markup,
            inputs=[document_detail_selector],
            outputs=[document_inspector_markup],
        )
        delete_event.then(controller.recent_document_markup, outputs=[recent_documents])
        delete_event.then(controller.document_library_markup, outputs=[document_library])
        delete_event.then(controller.document_library_count, outputs=[library_count])
        workspace_outputs = [
            library_view,
            session_view,
            nav_library_button,
            nav_session_button,
            context_view,
            document_inspector,
            mobile_nav_toggle,
            mobile_context_toggle,
            inspector_title,
            inspector_copy,
        ]
        report_outputs = [
            library_view,
            session_view,
            nav_library_button,
            nav_session_button,
            stats_section,
            context_view,
            document_inspector,
            mobile_nav_toggle,
            mobile_context_toggle,
            inspector_title,
            inspector_copy,
        ]
        nav_library_button.click(show_library, outputs=workspace_outputs)
        nav_session_button.click(show_session, outputs=workspace_outputs)
        nav_context_button.click(show_session, outputs=workspace_outputs)
        nav_reports_button.click(show_reports, outputs=report_outputs)
        new_session_event = new_session_button.click(
            controller.new_session,
            outputs=[session_state, session_status, chatbot, sources, source_summary, answer_status, current_turn_state, source_locator_state, notes_table, note_selector, note_content, stats_json],
        )
        new_session_event.then(
            _format_session_timeline,
            inputs=[chatbot, answer_status, sources],
            outputs=[conversation_timeline],
        )
        new_session_event.then(controller.note_list_markup, inputs=[session_state], outputs=[note_list_markup])
        new_session_button.click(lambda: "全部文档", outputs=[topbar_scope])
        ask_outputs = [session_state, chatbot, answer_status, sources, source_summary, current_turn_state, source_locator_state, notes_table, note_selector, stats_json]
        ask_event = ask_button.click(
            controller.ask,
            inputs=[session_state, question, document_filter, chatbot],
            outputs=ask_outputs,
            show_progress="full",
        )
        ask_event.then(
            _format_session_timeline,
            inputs=[chatbot, answer_status, sources],
            outputs=[conversation_timeline],
        )
        ask_event.then(controller.note_list_markup, inputs=[session_state], outputs=[note_list_markup])
        submit_event = question.submit(
            controller.ask,
            inputs=[session_state, question, document_filter, chatbot],
            outputs=ask_outputs,
            show_progress="full",
        )
        submit_event.then(
            _format_session_timeline,
            inputs=[chatbot, answer_status, sources],
            outputs=[conversation_timeline],
        )
        submit_event.then(controller.note_list_markup, inputs=[session_state], outputs=[note_list_markup])
        ask_event.then(lambda: "", outputs=[question])
        submit_event.then(lambda: "", outputs=[question])
        save_note_event = save_note_button.click(
            controller.save_note,
            inputs=[session_state, current_turn_state, document_filter, source_locator_state, note_content],
            outputs=[note_status, notes_table, note_selector, note_content],
        )
        save_note_event.then(controller.note_list_markup, inputs=[session_state], outputs=[note_list_markup])
        note_selector.change(controller.load_note, inputs=[note_selector, session_state], outputs=[note_content])
        update_note_event = update_note_button.click(
            controller.update_note,
            inputs=[note_selector, note_content, session_state],
            outputs=[note_status, notes_table],
        )
        update_note_event.then(controller.note_list_markup, inputs=[session_state], outputs=[note_list_markup])
        stats_button.click(controller.refresh_stats, inputs=[start_date, end_date], outputs=[stats_json, report_json])
    return demo


def main() -> None:
    controller = UIController()
    demo = build_app(controller)
    try:
        demo.launch(
            server_name=os.getenv("GRADIO_SERVER_NAME", "127.0.0.1"),
            server_port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
            share=False,
            show_error=True,
        )
    finally:
        controller.close()


if __name__ == "__main__":
    main()
