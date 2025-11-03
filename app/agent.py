from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search

POWER_KEYWORDS = [
    "Pakistan power sector", "electricity", "load-shedding", "NTDC",
    "DISCO", "K-Electric", "NEPRA", "WAPDA", "hydro", "solar", "wind","coal","ISMO","System Operator","Market Operator","LNG",
    "tariff", "blackout", "energy generation", "distribution","market operator","renewable energy", "power outage", "grid stability", "energy crisis", "power infrastructure", "energy policy", "fossil fuels", "power plants", "energy demand", "power transmission", "energy conservation", "smart grid", "electric vehicles","PPIB","CPPA-G","PEPCO","IPP","power purchase agreement", "circular debt", "energy transition", "sustainable energy", "climate change", "carbon emissions", "energy efficiency", "demand response", "energy storage", "microgrid", "off-grid", "distributed generation","power tariff","energy subsidies","power sector reforms","energy security","power outages","grid management","renewable integration","energy forecasting","power quality","energy market","demand-side management","energy regulation","power sector investment","energy infrastructure development","ministry of energy","national energy policy","power division","energy audits","power sector challenges","energy sector growth","electricity consumption","power sector modernization","energy sector policies"
]

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A concise assistant that returns structured news items about the Pakistan power sector. URLs must be authentic and reachable.',
    instruction=f"""
You are a concise assistant. For any user query about the Pakistan power sector, follow these steps exactly:

1. Use the google_search tool to find news and articles about the Pakistan power sector.
2. Only select items that mention at least one of these keywords (case-insensitive): {', '.join(POWER_KEYWORDS)}.
3. Prioritize items published in the last 365 days. If none are available, expand the range and explicitly note that you did.
4. Select up to 5 of the most relevant and reputable items (news outlets, official reports). For each candidate item:
   a. Verify the url is an absolute HTTP/HTTPS link and is reachable (returns HTTP 200). If the link is unreachable, redirects to a login/paywall, or is not a direct article URL, discard it and pick the next best item.
   b. For each accepted item provide these fields:
      - headline
      - publication_date (ISO format YYYY-MM-DD if available)
      - author (author name; if unavailable use "unknown")
      - source (publication name)
      - url (direct working link, HTTP/HTTPS)
      - sentiment (Positive | Negative | Neutral) — determine sentiment based only on that item's tone/content
      - summary (one concise factual sentence supported by that item)
      - tags (6–12 frequently used words regarding the power sector drawn from the item's text)
      - local_or_international (Local | International) — classify the source as Pakistani (Local) or non-Pakistani (International)
      - image (absolute HTTP/HTTPS URL of the main article image; if no suitable image, use an empty string). Verify the image URL is reachable (HTTP 200); if not reachable, set to empty string.
      - id (deterministic unique identifier for this article to detect duplicates; compute as the SHA256 hex digest of the article's canonical URL)
5. Based only on the cited items, determine an overall_sentiment: Positive | Negative | Neutral.
6. Produce a brief factual summary (2–4 sentences) of the current situation supported by the cited items.
7. Be concise, avoid speculation, and include only information verifiable by the provided links.

Response structure (must follow exactly):
- items: a list of objects, each with keys headline, publication_date, author, source, url, sentiment, summary, tags, local_or_international, image, id
- overall_sentiment: Positive|Negative|Neutral
- summary: short factual summary (2–4 sentences)

Return only the structured response (do not add extra commentary).
""",
    tools=[google_search],
)
