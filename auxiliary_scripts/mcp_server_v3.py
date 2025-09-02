from fastmcp import FastMCP  # ← newer import style that expects Pydantic style annotation
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from typing import List, ClassVar
from pydantic import BaseModel, HttpUrl, Field, PositiveInt  # <-- for the Pydantic schema


# --------------------------------------------------------------
# 1️⃣  Initialise the server – give it a human‑readable name.
# --------------------------------------------------------------
mcp = FastMCP("URL Text Fetcher")  # shown in LM Studio UI


# ----------------------------------------------------------------------
# 2️⃣  Pydantic data model Arguments (these become the “parameters” objects that
#     LM‑Studio shows to the LLM).
# ----------------------------------------------------------------------
class UrlArg(BaseModel):
    """
    Input arguments for both tools.
    * "url" - required fully-qualified HTTP/HTTPS URL. Positional argument (...).
    * "max_chars" - optional hard cut-off in **characters** (default: 40000), ratio of 1:4 of tokens to chars. Optional argument.
    """

    MAX_CHARS: ClassVar[int] = 40000  # hard-coded chars limit, add explicit type annotation and tells Pydantic to ignore it (“this is not a field” )

    url: HttpUrl = Field(...,
        description="The address of the web page you want to fetch."
    )
    max_chars: PositiveInt = Field(
        default=MAX_CHARS,
        description=(
            "Maximum number of characters to return. If omitted the server "
            f"uses the hard-coded default {MAX_CHARS}."
        ),
    )


# Helper function: “extract main visible text” from HTML page
def _clean_body(html: str) -> str:
    """
    Return a string that contains only the *readable* body content.
    Steps:
      1. Parse with BeautifulSoup.
      2. Drop <script>, <style>, <noscript>, <header>, <footer>, <nav>.
      3. Keep text from <p>, headings, list items and blockquotes - these are
         the parts that usually constitute the main article body.
      4. Collapse whitespace to a single space and strip leading/trailing blanks.
    """

    soup = BeautifulSoup(html, "html.parser")

    # Remove boiler‑plate tags that never contain the “main article”
    for element in soup.find_all(["script", "style", "noscript", "header", "footer", "nav"]):
        element.decompose()

    # Locate the <body> (fallback to whole document if missing).
    body = soup.body or soup

    # Collect visible text from the tags we consider “content”
    # visible_parts: list[str] = []
    # for element in body.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote", "pre", "code"]):
    #     txt = element.get_text(separator=" ", strip=True)
    #     if txt:
    #         visible_parts.append(txt)

    # Alternative approach - “all visible text/elements” that exists under <body> (but without duplication)
    cleaned = " ".join(body.stripped_strings)

    # If nothing matched (e.g. a very sparse page), fall back to all text in body
    # if not visible_parts:
    #     visible_parts.append(body.get_text(separator=" ", strip=True))

    # cleaned = " ".join(visible_parts)

    # Whitespace normalisation (collapse multiple spaces/tabs/newlines into a single space)
    return " ".join(cleaned.split())


# ----------------------------------------------------------------------
# 3️⃣  Functions – decorated with @mcp.tool.
#     • The only parameter is a Pydantic model instance.
#       FastMCP extracts its JSON‑Schema automatically.
#     • Return values are any JSON‑serialisable object; LM‑Studio will
#       pass them back to the LLM as `result`.
# ----------------------------------------------------------------------

@mcp.tool(description="Fetch the main readable body text from a URL web page, with optional size limits.")
def fetch_url_text(args: UrlArg) -> str:
    """
    1. Retrieve the textual content of a page (*args.url*).
    2. Strip out scripts, navigation, etc., and keep only the visible
       content (paragraphs, headings, list items, etc.).
    3. Apply a hard limit of "max_chars" (ratio of 1:4 of tokens to chars)
    """

    # Download the raw HTML
    resp = requests.get(str(args.url), timeout=10)
    resp.raise_for_status()
    html = resp.text

     # Keep only the main body text
    cleaned = _clean_body(html)

    # Apply size limits
    result = cleaned[:args.max_chars]

    return result


@mcp.tool(description="Return a list of every URL hyperlink (href) found on a page.")
def fetch_page_links(args: UrlArg) -> List[str]:
    """
    Crawl *args.url* and collect the value of each ``href`` attribute
    from `<a>` elements.  The returned list contains the raw strings as
    they appear in the HTML (relative URLs are **not** resolved).
    """

    resp = requests.get(str(args.url), timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    links: List[str] = [a["href"] for a in soup.find_all("a", href=True)]
    return links


# ----------------------------------------------------------------------
# 4️⃣  Boiler‑plate to start the server when the module is executed.
# ----------------------------------------------------------------------
def main() -> None:
    """
    Launch the MCP server that hosts the 2 MCP functions defined above. FastMCP will pick an available port automatically. 
    LM-Studio will launch this file via the command you configured in *mcp.json*.
    """
    # mcp.run(transport="http", host="127.0.0.1", port=8000)  # HTTP Transport (Streamable), turns the MCP server into a web service accessible via a URL, uses Streamable HTTP protocol, which allows clients to connect over the network.
    mcp.run()  # STDIO (Standard Input/Output) is the default transport for FastMCP servers, communications via standard input and output streams, started on-demand by the client.


if __name__ == "__main__":
    main()
