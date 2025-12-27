"""Quick validation: call FastAPI /detect and print segments + allergens."""
import sys, requests, json

def main(path: str):
    url = "http://localhost:8000/detect"
    with open(path, "rb") as f:
        files = {"file": (path, f, "image/jpeg")}
        data = {"use_ocr": "true"}
        r = requests.post(url, files=files, data=data, timeout=60)
    print("Status:", r.status_code)
    j = r.json()
    print("success:", j.get("success"))
    print("allergen keys:", list((j.get("detected_allergens") or {}).keys()))
    print("cleaned_text sample:", (j.get("cleaned_text") or "")[:160])
    segs = j.get("segments") or []
    if segs:
        print("segments count:", len(segs))
        print("first segment lines:")
        for line in segs[0].get("lines", [])[:3]:
            print(" -", line.get("text"))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_api_layout.py <image_path>")
        sys.exit(1)
    main(sys.argv[1])
