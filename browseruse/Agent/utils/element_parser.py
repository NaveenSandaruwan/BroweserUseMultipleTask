def extract_simplified_elements(data: dict):
    elements = []
    for key in sorted(data.keys(), key=lambda k: int(k)):
        el = data[key]
        elements.append({
            "id": key,
            "tag": el.get("tag_name"),
            "text": el.get("text_content"),
            "visible": el.get("is_visible"),
            "x": el.get("bounding_box", {}).get("x"),
            "y": el.get("bounding_box", {}).get("y")
        })
    return elements

def convert_elements_to_text(elements):
    return "\n".join(
        [f"{e['id']}: tag={e['tag']}, text={e['text']}, visible={e['visible']}, "
         f"x={round(e['x']) if e['x'] else e['x']}, y={round(e['y']) if e['y'] else e['y']}"
         for e in elements]
    )
