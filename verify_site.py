import re
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.request import urlopen

from build_map import RESTAURANTS


ROOT = Path(__file__).resolve().parent


class IframeParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.iframes = []

    def handle_starttag(self, tag, attrs):
        if tag == "iframe":
            self.iframes.append(dict(attrs))


def main():
    pages = {}
    for filename in ("index.html", "map.html"):
        path = ROOT / filename
        assert path.is_file(), f"Missing {filename}"
        pages[filename] = path.read_text(encoding="utf-8")
        assert pages[filename].strip(), f"Empty {filename}"

    parser = IframeParser()
    parser.feed(pages["index.html"])
    assert parser.iframes == [
        {"src": "map.html", "width": "800", "height": "600", "style": "border:0;"}
    ], "Expected one borderless 800 × 600 iframe with a relative URL"

    map_html = pages["map.html"]
    assert re.search(r"center:\s*\[38\.5434,\s*-121\.7413\]", map_html)
    assert re.search(r'"zoom":\s*15\b', map_html)
    assert re.search(
        r"html\s*>\s*body\s*\{\s*width:\s*800px;\s*height:\s*600px;\s*\}",
        map_html,
    ), "The outer map body must have fixed pixel dimensions"
    assert len(re.findall(r"L\.marker\s*\(", map_html)) == 3
    markers = re.findall(
        r"L\.marker\s*\(\s*\[([\d.-]+),\s*([\d.-]+)\](.*?)(?=L\.marker\s*\(|</script>)",
        map_html,
        re.DOTALL,
    )
    assert len(markers) == 3, "Expected three marker definitions with coordinates"
    expected = {tuple(location): name for name, location in RESTAURANTS}
    seen = set()
    for lat_text, lon_text, definition in markers:
        lat, lon = float(lat_text), float(lon_text)
        assert 38.52 < lat < 38.57 and -121.79 < lon < -121.69, (lat, lon)
        assert (lat, lon) not in seen, "Duplicate marker coordinates"
        seen.add((lat, lon))
        name = expected[(lat, lon)]
        popup, tooltip = definition.split(".bindTooltip(", 1)
        assert ".bindPopup(" in popup and name in popup and name in tooltip, name

    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        thread = Thread(target=server.serve_forever)
        thread.start()
        try:
            for filename, content in pages.items():
                url = f"http://127.0.0.1:{server.server_port}/{filename}"
                with urlopen(url, timeout=5) as response:
                    assert response.status == 200, url
                    assert response.read().decode("utf-8") == content, url
        finally:
            server.shutdown()
            thread.join()

    print("Verified map dimensions, center, zoom, three markers, iframe, and HTTP responses.")


if __name__ == "__main__":
    main()
