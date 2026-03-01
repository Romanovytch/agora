from __future__ import annotations

from pydantic import BaseModel, Field


class SourceDefaults(BaseModel):
    """Cross-kind defaults (safe for any file-based source)."""

    include_globs: list[str] = ["**/*.md", "**/*.qmd", "**/*.Rmd"]
    exclude_dirs: list[str] = [
        ".git",
        "_book",
        "docs",
        ".quarto",
        "renv",
        ".github",
        "node_modules",
        "build",
        "dist",
        "site",
    ]
    default_lang: str = "en"
    follow_symlinks: bool = False


class SourcesConfig(BaseModel):
    """Top-level configuration with shared defaults and named sources.

    `sources` is a mapping: source name -> typed config (discriminated by `kind`).
    The discriminated union is assembled in the loader, so we keep the field
    shape here and let the loader fill the type info.
    """

    version: int = 1
    defaults: SourceDefaults = Field(default_factory=SourceDefaults)
    # The loader will parse this into a discriminated union.
    sources: dict[str, dict]
