# Impact Sentinel documentation

This directory holds the product definition for **Impact Sentinel**, a monitoring system for current and future asteroid impact zones. These documents are design artifacts only. They do not describe implemented behavior of the current starter code.

| Document | Purpose |
| --- | --- |
| [requirements.md](requirements.md) | User requirements and system requirements, including every rubric capability |
| [stories.md](stories.md) | User stories derived from those requirements, with acceptance criteria and traceability |
| [architecture.md](architecture.md) | High-level component outline and design diagrams (no implementation) |
| [diagrams/impact-sentinel-high-level.png](diagrams/impact-sentinel-high-level.png) | High-level architecture diagram (PNG) |

Intended users are **geologists** and **aeroscientists**. The runtime shape is a **web front end** plus two back-end workers: a **data collector** (web scraper) and a **data analyzer**.
