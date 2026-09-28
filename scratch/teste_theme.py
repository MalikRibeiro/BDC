from pathlib import Path

the_dir = Path("src/ui")
style_path = the_dir / "assets" / "style.css"
print("Exists:", style_path.exists())
if style_path.exists():
    content = style_path.read_text(encoding="utf-8")
    print("Length:", len(content))
    print("Contains bdc-kpi-grid:", "bdc-kpi-grid" in content)
    print("Contains bdc-view-header:", "bdc-view-header" in content)
