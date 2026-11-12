import re
import time
import html
import argparse
import requests
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
CLEANED_DIR = REPO_ROOT / "data" / "cleaned"

WIKI_API_URL = "https://en.wikipedia.org/w/api.php"
GEEKDO_API_URL = "https://api.geekdo.com/api/geekitems"
BGG_SEARCH_URL = "https://boardgamegeek.com/search/boardgame"

HEADERS = {
    "User-Agent": "Project4BoardGameBot/1.0 (https://github.com/Dbishop25/Project-4-Chat-bot; Educational RAG Project)"
}

# Core starter list
DEFAULT_GAME_NAMES = [
    "Catan",
    "Wingspan (board game)",
    "Ticket to Ride (board game)",
    "Carcassonne (board game)",
    "Terraforming Mars (board game)",
    "Pandemic (board game)",
    "Gloomhaven",
    "Root (board game)",
    "Scythe (board game)",
    "Azul (board game)",
]


def clean_text_noise(raw_text: str) -> str:
    """Strips HTML, Wiki markup, citations, and trailing reference sections."""
    text = html.unescape(raw_text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\[(?:\d+|citation needed|edit|note \d+)\]", "", text, flags=re.IGNORECASE)

    # Convert MediaWiki headers to Markdown headers
    text = re.sub(r"^====\s*(.+?)\s*====$", r"#### \1", text, flags=re.MULTILINE)
    text = re.sub(r"^===\s*(.+?)\s*===$", r"### \1", text, flags=re.MULTILINE)
    text = re.sub(r"^==\s*(.+?)\s*==$", r"## \1", text, flags=re.MULTILINE)

    # Remove non-gameplay footer sections
    text = re.split(
        r"^##\s*(?:References|External links|See also|Further reading|Notes)\b",
        text,
         flags=re.MULTILINE | re.IGNORECASE,
    )[0]

    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def auto_discover_games_from_wiki_category(category: str = "Category:German-style_board_games", limit: int = 20) -> list[str]:
    """Automatically fetches board game titles from a Wikipedia Category."""
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category,
        "cmtype": "page",
        "cmlimit": limit,
        "format": "json",
    }
    resp = requests.get(WIKI_API_URL, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    members = resp.json().get("query", {}).get("categorymembers", [])
    # Filter out generic list/index pages
    return [
        m["title"] for m in members
        if not m["title"].lower().startswith(("list of", "category:", "portal:", "template:"))
    ]


def search_wiki_article(query: str) -> tuple[str, str]:
    """Searches Wikipedia by plain game name and returns (official_title, full_extract)."""
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": f"{query} board game",
        "srlimit": 1,
        "format": "json",
    }
    s_resp = requests.get(WIKI_API_URL, params=search_params, headers=HEADERS, timeout=15)
    s_resp.raise_for_status()
    results = s_resp.json().get("query", {}).get("search", [])
    if not results:
        raise ValueError(f"No Wikipedia page found for '{query}'")

    best_title = results[0]["title"]

    extract_params = {
        "action": "query",
        "format": "json",
        "titles": best_title,
        "prop": "extracts",
        "explaintext": 1,
        "redirects": 1,
    }
    e_resp = requests.get(WIKI_API_URL, params=extract_params, headers=HEADERS, timeout=15)
    e_resp.raise_for_status()
    pages = e_resp.json().get("query", {}).get("pages", {})
    for page_id, page_data in pages.items():
        if page_id != "-1" and page_data.get("extract"):
            return page_data.get("title", best_title), page_data["extract"]

    raise ValueError(f"Empty extract for '{best_title}'")


def auto_lookup_bgg_metadata(game_name: str) -> dict:
    """Automatically looks up a game's BGG metadata via Geekdo JSON search without needing an ID."""
    clean_query = re.sub(r"\s*\(.*?\)\s*", "", game_name).strip()
    try:
        resp = requests.get(
            BGG_SEARCH_URL,
            params={"q": clean_query, "showcount": 1},
            headers={**HEADERS, "Accept": "application/json"},
            timeout=10,
        )
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if items:
                bgg_id = items[0].get("objectid")
                detail_resp = requests.get(
                    GEEKDO_API_URL,
                    params={"objectid": bgg_id, "objecttype": "thing"},
                    headers=HEADERS,
                    timeout=10,
                )
                if detail_resp.status_code == 200:
                    item = detail_resp.json().get("item", {})
                    return {
                        "bgg_id": bgg_id,
                        "title": item.get("name", clean_query),
                        "year": item.get("yearpublished", "N/A"),
                        "min_players": item.get("minplayers", "N/A"),
                        "max_players": item.get("maxplayers", "N/A"),
                        "min_playtime": item.get("minplaytime", "N/A"),
                        "max_playtime": item.get("maxplaytime", "N/A"),
                        "min_age": item.get("minage", "N/A"),
                        "short_desc": item.get("short_description", "Tabletop board game."),
                    }
    except Exception:
        pass
    return {"bgg_id": "N/A", "title": clean_query}


def ingest_game_by_name(game_query: str):
    """Fetches, cleans, and saves any game given just its name."""
    wiki_title, wiki_raw = search_wiki_article(game_query)
    bgg_meta = auto_lookup_bgg_metadata(wiki_title)

    display_title = bgg_meta.get("title") or re.sub(r"\s*\(.*?\)\s*", "", wiki_title)
    slug = re.sub(r"[^a-z0-9]+", "_", display_title.lower()).strip("_")

    # 1. Save raw uncleaned text
    raw_filepath = RAW_DIR / f"{slug}_raw.txt"
    raw_filepath.write_text(wiki_raw, encoding="utf-8")

    # 2. Clean and format into structured Markdown headers
    cleaned_body = clean_text_noise(wiki_raw)
    parts = re.split(r"(?=^##\s+)", cleaned_body, maxsplit=1, flags=re.MULTILINE)
    intro_text = parts[0].strip()
    sections_text = parts[1].strip() if len(parts) > 1 else ""

    structured_md = f"""# {display_title}

## Game Specifications and Overview
### Quick Rules & Player Metadata
- **Game Title:** {display_title}
- **BGG ID:** {bgg_meta.get("bgg_id", "N/A")}
- **Year Published:** {bgg_meta.get("year", "N/A")}
- **Player Count:** {bgg_meta.get("min_players", "N/A")} to {bgg_meta.get("max_players", "N/A")} players
- **Playing Time:** {bgg_meta.get("min_playtime", "N/A")}–{bgg_meta.get("max_playtime", "N/A")} minutes
- **Recommended Age:** {bgg_meta.get("min_age", "N/A")}+
- **Summary:** {bgg_meta.get("short_desc", "Tabletop strategy board game.")}

### Overview and Concept
{intro_text}

{sections_text}
"""
    cleaned_filepath = CLEANED_DIR / f"{slug}.md"
    cleaned_filepath.write_text(structured_md.strip() + "\n", encoding="utf-8")
    print(f"[✓] Ingested & Cleaned: {display_title} -> data/cleaned/{slug}.md")


def main():
    parser = argparse.ArgumentParser(description="Automated Board Game Ingestion & Cleaning Pipeline")
    parser.add_argument("--auto-discover", type=int, default=0, help="Auto-crawl N extra board games from Wikipedia categories")
    parser.add_argument("--add", nargs="+", help="Add specific game names by search (e.g. --add 'Ark Nova' 'Clank!')")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)

    if args.add:
        games_to_process = args.add
    else:
        games_to_process = list(DEFAULT_GAME_NAMES)
        if args.auto_discover > 0:
            print(f"Auto-discovering up to {args.auto_discover} board games from Wikipedia...")
            discovered = auto_discover_games_from_wiki_category(limit=args.auto_discover)
            for g in discovered:
                if g not in games_to_process:
                    games_to_process.append(g)

    print(f"Processing {len(games_to_process)} board games...\n")
    for game_name in games_to_process:
        try:
            ingest_game_by_name(game_name)
            time.sleep(1)
        except Exception as e:
            print(f"[!] Skipped '{game_name}': {e}")

    print("\nIngestion & Cleaning complete!")
    print(f"Total games processed: {len(games_to_process)}")


if __name__ == "__main__":
    main()