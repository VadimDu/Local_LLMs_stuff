from fastmcp import FastMCP  # ← newer import style that expects Pydantic style annotation
import requests
from bs4 import BeautifulSoup
from typing import List
from pydantic import BaseModel, HttpUrl, Field  # <-- for the Pydantic schema


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
    A single, fully‑qualified HTTP/HTTPS URL.
    A Pydantic data model (inherited from pydantic.BaseModel) gives you automatic validation, self‑documenting schema, 
    and typed access inside the functions that use this argument.
    """

    url: HttpUrl = Field(
        ..., description="The address of the web page you want to fetch."
    )


# ----------------------------------------------------------------------
# 3️⃣  Functions – decorated with @mcp.tool.
#     • The only parameter is a Pydantic model instance.
#       FastMCP extracts its JSON‑Schema automatically.
#     • Return values are any JSON‑serialisable object; LM‑Studio will
#       pass them back to the LLM as `result`.
# ----------------------------------------------------------------------

@mcp.tool(description="Download and return the plain text of a web page.")
def fetch_url_text(args: UrlArg) -> str:
    """
    Retrieve the textual content of *args.url*.
    The HTML is parsed with BeautifulSoup and all tags are stripped,
    leaving only readable paragraphs separated by new‑lines.
    """

    resp = requests.get(str(args.url), timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    return soup.get_text(separator="\n", strip=True)


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
    LM‑Studio will launch this file via the command you configured in *mcp.json*.
    """
	# mcp.run(transport="http", host="127.0.0.1", port=8000)  # HTTP Transport (Streamable), turns the MCP server into a web service accessible via a URL, uses Streamable HTTP protocol, which allows clients to connect over the network.
    mcp.run()  # STDIO (Standard Input/Output) is the default transport for FastMCP servers, communications via standard input and output streams, started on-demand by the client.

if __name__ == "__main__":
    main()
