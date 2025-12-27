"""
OCR layout parser: reconstructs human-like reading order from EasyOCR boxes.
Groups words into lines, lines into blocks, and returns structured segments + text.
"""
from typing import List, Tuple, Dict, Any
import math

BBox = List[List[int]]  # 4 points [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
Item = Tuple[BBox, str, float]


def _rect_from_bbox(bbox: BBox):
    xs = [p[0] for p in bbox]
    ys = [p[1] for p in bbox]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    return x_min, y_min, x_max, y_max


def _center(rect):
    x_min, y_min, x_max, y_max = rect
    return (x_min + x_max) / 2.0, (y_min + y_max) / 2.0


def _height(rect):
    return rect[3] - rect[1]


def group_lines(items: List[Item]) -> List[List[Dict[str, Any]]]:
    """Group OCR items into lines using y proximity and sort by x within lines."""
    if not items:
        return []

    enriched = []
    for bbox, text, conf in items:
        rect = _rect_from_bbox(bbox)
        cx, cy = _center(rect)
        enriched.append({
            "bbox": bbox,
            "rect": rect,
            "cx": cx,
            "cy": cy,
            "h": _height(rect),
            "text": text,
            "conf": conf,
        })

    # Sort top-to-bottom, then left-to-right
    enriched.sort(key=lambda e: (round(e["cy"]), round(e["cx"])) )

    # Median height guides line threshold
    heights = sorted(e["h"] for e in enriched if e["h"] > 0)
    median_h = heights[len(heights)//2] if heights else 16
    y_thresh = max(10, median_h * 0.7)

    lines: List[List[Dict[str, Any]]] = []
    current: List[Dict[str, Any]] = []
    current_y: float | None = None

    for e in enriched:
        if current_y is None:
            current = [e]
            current_y = e["cy"]
            continue
        if abs(e["cy"] - current_y) <= y_thresh:
            current.append(e)
        else:
            # finalize previous line
            current.sort(key=lambda x: x["cx"])  # left-to-right
            lines.append(current)
            current = [e]
            current_y = e["cy"]

    if current:
        current.sort(key=lambda x: x["cx"])  # left-to-right
        lines.append(current)

    return lines


def group_blocks(lines: List[List[Dict[str, Any]]]) -> List[List[List[Dict[str, Any]]]]:
    """
    Group lines into blocks by analyzing large vertical gaps.
    """
    if not lines:
        return []
    blocks: List[List[List[Dict[str, Any]]]] = []
    current_block: List[List[Dict[str, Any]]] = []

    # Estimate line height to decide block breaks
    line_heights = [sum(l[i]["h"] for i in range(len(l)))/max(1,len(l)) for l in lines]
    median_line_h = sorted(line_heights)[len(line_heights)//2] if line_heights else 16
    v_gap_thresh = max(20, median_line_h * 1.5)

    prev_bottom: float | None = None
    for line in lines:
        # compute line top/bottom
        y_tops = [w["rect"][1] for w in line]
        y_bottoms = [w["rect"][3] for w in line]
        top = min(y_tops)
        bottom = max(y_bottoms)
        if prev_bottom is None or (top - prev_bottom) <= v_gap_thresh:
            current_block.append(line)
        else:
            blocks.append(current_block)
            current_block = [line]
        prev_bottom = bottom

    if current_block:
        blocks.append(current_block)
    return blocks


def reconstruct_text(items: List[Item]) -> Dict[str, Any]:
    """
    Build human-readable text with logical line breaks and punctuation fixes.
    Returns segments and full text.
    """
    lines = group_lines(items)
    blocks = group_blocks(lines)

    segments: List[Dict[str, Any]] = []
    texts: List[str] = []

    for block in blocks:
        block_lines_text = []
        for line in block:
            words = [w["text"].strip() for w in line if w.get("text")]
            line_text = " ".join(words)
            # Handle hyphenation at line ends
            if texts and texts[-1].endswith("-"):
                texts[-1] = texts[-1][:-1] + words[0] if words else texts[-1][:-1]
            else:
                block_lines_text.append(line_text)
        # Merge lines with commas if ingredient context
        merged = []
        for lt in block_lines_text:
            merged.append(lt)
        block_text = " \n".join(merged)
        texts.append(block_text)
        segments.append({
            "type": "block",
            "lines": [
                {
                    "text": lt,
                    "words": [w["text"] for w in line]
                } for lt, line in zip(block_lines_text, block)
            ],
        })

    full_text = "\n\n".join(texts)
    # Minor normalization: replace multiple spaces/newlines
    full_text = " ".join(full_text.split())
    return {"text": full_text.strip(), "segments": segments}
