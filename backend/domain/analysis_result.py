def normalize_analysis_sections(sections):
    if sections is None:
        return None
    if not isinstance(sections, list):
        return sections
    return sections


def normalize_analysis_item(item: dict | None) -> dict:
    data = item or {}
    return {
        "name": data.get("name", ""),
        "headers": data.get("headers", []),
        "rows": data.get("rows", []),
        "description": data.get("description", ""),
        "sections": normalize_analysis_sections(data.get("sections")),
    }


def normalize_analysis_items(result) -> list[dict]:
    items = result if isinstance(result, list) else [result]
    return [normalize_analysis_item(item) for item in items]

