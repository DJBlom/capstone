# Impact Sentinel — User Stories

**Derived from:** [requirements.md](requirements.md)
**Status:** Stories only (no implementation in this phase)

Stories are grouped into epics. Each story lists the requirement IDs it satisfies. Acceptance criteria are testable. Personas match the requirements document: **geologist**, **aeroscientist**, **operator**, **developer**.

Priority uses MoSCoW: **Must**, **Should**, **Could**, **Won’t** (this release). Everything needed to hit the course rubric is Must or Should.

---

## Story map

```text
Geologist / aeroscientist
  └── Monitor impact zones
        ├── See current (observed) zones
        ├── See future (predicted) zones
        ├── Filter with a form
        └── Read tabular + summary reports

Pipeline (big data)
  └── Collect  →  persist raw  →  event  →  analyze  →  persist zones  →  serve

Quality and delivery
  └── Tests + doubles  →  CI  →  environments  →  CD  →  monitor
```

| Epic | Stories | Rubric coverage |
| --- | --- | --- |
| E1 Reporting workstation | US-01 … US-12 | Web application, form, reporting |
| E2 Data collection | US-13 … US-16 | Data collection |
| E3 Data analysis | US-17 … US-21 | Data analyzer |
| E4 Persistence and REST | US-22 … US-26 | Data store, REST collaboration |
| E5 Events | US-27 … US-29 | Event collaboration messaging |
| E6 Quality | US-30 … US-33 | Unit tests, integration tests, mocks |
| E7 Environments and delivery | US-34 … US-37 | Product environment, CI, CD |
| E8 Operations | US-38 … US-40 | Production monitoring, instrumenting |

---

## Epic E1 — Reporting workstation (web application)

### US-01 — View the monitoring home

**As a** geologist or aeroscientist
**I want** to open the web application and see that Impact Sentinel is the asteroid impact-zone monitor
**So that** I know I am in the right workstation and can reach reports.

**Priority:** Must
**Requirements:** SR-WEB-01, SR-WEB-05

**Acceptance criteria**

- Opening the application root URL returns HTTP 200 and a page titled or headed as the impact-zone monitor.
- The page links to (or contains) the filter form and the summary report.
- Styles and images load from the web application.

---

### US-02 — Submit a filter form

**As a** geologist or aeroscientist
**I want** a form to filter impact zones by time, class, object, probability, risk scale, and region
**So that** I can ask a scientific question instead of reading the entire catalog.

**Priority:** Must
**Requirements:** UR-05, UR-06, SR-WEB-02

**Acceptance criteria**

- The form includes: time window, class (current / future / both), optional designation, optional minimum probability, optional minimum risk scale, optional region or bounding box.
- Submitting the form shows a result list or an explicit empty state.
- The result list honors every supplied filter.

---

### US-03 — Reject invalid form input

**As a** geologist or aeroscientist
**I want** clear validation when I enter a bad date range or non-numeric probability
**So that** I can correct the query without wondering whether the system failed.

**Priority:** Must
**Requirements:** UR-07, SR-WEB-02

**Acceptance criteria**

- Inverted or unparseable dates produce a visible validation message and HTTP 400 on the API equivalent.
- Non-numeric probability or risk scale is rejected the same way.
- The process does not crash; the user can resubmit.

---

### US-04 — See current impact zones

**As a** geologist
**I want** to list recent observed fireballs/bolides as current impact zones
**So that** I can study where energy was recently deposited in the atmosphere or on the ground.

**Priority:** Must
**Requirements:** UR-01, UR-03, UR-10, SR-ANL-02

**Acceptance criteria**

- Filtering to class = current returns only observed events.
- Each row shows event time, location or “location not published”, energy or “not published”, and source.
- Current vs future is labeled on every row.

---

### US-05 — See future impact zones

**As an** aeroscientist
**I want** to list published potential impacts as future impact zones
**So that** I can monitor virtual impactors and their probabilities.

**Priority:** Must
**Requirements:** UR-02, UR-03, UR-11, SR-ANL-02

**Acceptance criteria**

- Filtering to class = future returns only published potential-impact records.
- Each row shows designation, date window, probability, risk-scale fields when present, and source.
- No future row is labeled as observed.

---

### US-06 — Read a tabular impact-zone report

**As a** geologist or aeroscientist
**I want** a table of zones matching my filters
**So that** I can scan many objects in one view.

**Priority:** Must
**Requirements:** UR-08, SR-WEB-02

**Acceptance criteria**

- Table columns include: id/designation, class, time, probability or “observed”, energy, zone summary, source.
- Sorting or default order is documented (for example future by probability descending, current by time descending).

---

### US-07 — Read a summary report

**As a** geologist or aeroscientist
**I want** counts and highlights, not only a raw table
**So that** I can get situational awareness in one glance.

**Priority:** Must
**Requirements:** UR-09, UR-12, SR-WEB-02

**Acceptance criteria**

- Summary shows count of current records, count of future records, highest-probability future object (or none), most energetic recent current event (or none).
- Summary shows last successful collection time and last successful analysis time.
- If those times are older than the freshness threshold, the summary labels the data stale.

---

### US-08 — Open object or event detail

**As a** geologist or aeroscientist
**I want** a detail page for one record
**So that** I can inspect identifiers, source, computed zone, and timestamps.

**Priority:** Must
**Requirements:** UR-04, UR-13

**Acceptance criteria**

- Navigating from a table row opens a detail view for that id.
- Detail shows source URL/name, collected-at, analyzed-at, raw-derived fields, and computed zone.
- Missing published fields display as “not published,” not as zero.

---

### US-09 — Geologist reading of a zone

**As a** geologist
**I want** energy and a zone description that is honest about location
**So that** I can reason about ground or ocean effects without fake coordinates.

**Priority:** Must
**Requirements:** UR-10, UR-14, NFR-08

**Acceptance criteria**

- When lat/lon are published, detail shows them and an energy-derived radius or documented default radius.
- When lat/lon are not published, detail states “location unconstrained” or “location not published” and does not invent a point.

---

### US-10 — Aeroscientist reading of a zone

**As an** aeroscientist
**I want** probability, date window, and risk-scale values on future records
**So that** I can compare objects the way catalog papers do.

**Priority:** Must
**Requirements:** UR-11

**Acceptance criteria**

- Future detail includes probability and date window when the source published them.
- Torino/Palermo-style fields appear when present and “not published” when absent.

---

### US-11 — See data freshness

**As a** geologist or aeroscientist
**I want** to know when data was last collected and analyzed
**So that** I do not treat a stalled pipeline as a live catalog.

**Priority:** Must
**Requirements:** UR-12, SR-MON-04, NFR-01, NFR-04

**Acceptance criteria**

- Dashboard and summary show last successful scrape and last successful analysis (UTC).
- Stale threshold is configurable; exceeding it shows a visible stale warning.

---

### US-12 — Use the app when workers are down

**As a** geologist or aeroscientist
**I want** to still read the last analyzed report if the collector or analyzer is temporarily down
**So that** the workstation remains useful during a worker outage.

**Priority:** Should
**Requirements:** SR-WEB-04, NFR-03

**Acceptance criteria**

- With persisted analyzed data and a stopped collector, the report still renders.
- A health/freshness warning indicates workers are not currently succeeding.

---

## Epic E2 — Data collection

### US-13 — Scrape public NEO impact sources on a schedule

**As an** operator
**I want** the data collector to scrape the public Sentry-style risk listing and Fireballs listing on a schedule
**So that** the product has current and future source data without a human download step.

**Priority:** Must
**Requirements:** SR-COL-01, SR-COL-02, SR-COL-05

**Acceptance criteria**

- A collector worker runs on a configurable interval using the project’s work-scheduler pattern.
- It fetches the configured future-risk source and the configured current-fireball source.
- Requests include a bounded rate and an identifying user-agent.
- The worker process stays up if a single fetch fails.

---

### US-14 — Persist raw payloads

**As a** developer
**I want** every successful fetch stored as a raw payload with URL, timestamp, and body
**So that** analysis is reproducible and we can re-parse without scraping again.

**Priority:** Must
**Requirements:** SR-COL-03, SR-PER-02, NFR-02

**Acceptance criteria**

- A successful fetch writes a raw record: source id, URL, collected-at (UTC), HTTP status, body.
- Re-running analysis against that stored body does not require the public site.

---

### US-15 — Record collection failures without crashing

**As an** operator
**I want** timeouts and non-success HTTP responses logged and counted
**So that** I can see source outages in monitoring instead of a dead process.

**Priority:** Must
**Requirements:** SR-COL-04, SR-MON-05

**Acceptance criteria**

- Timeout, HTTP 5xx, and empty body do not kill the scheduler.
- Failure is logged at error/warn with source URL and reason.
- Failure increments a collection-failure metric (see US-38).

---

### US-16 — Announce that collection completed

**As a** pipeline
**I want** a `collection.completed` event after a raw payload is stored
**So that** the analyzer can start without polling forever.

**Priority:** Must
**Requirements:** SR-COL-06, SR-EVT-02, SR-EVT-03

**Acceptance criteria**

- After a raw insert, an event is published with payload id, source, timestamp, correlation id.
- If the broker is down, the raw row still exists (US-29).

---

## Epic E3 — Data analysis

### US-17 — Consume new raw payloads

**As a** pipeline
**I want** the analyzer to pick up new raw payloads from events and from unprocessed store rows
**So that** analysis proceeds both in the fast path and after a missed message.

**Priority:** Must
**Requirements:** SR-ANL-01, SR-EVT-04

**Acceptance criteria**

- An analyzer worker is scheduled like the collector.
- It processes a `collection.completed` event into analyzed records.
- It also processes raw rows marked unprocessed if no event arrives.

---

### US-18 — Parse and classify current vs future

**As an** aeroscientist
**I want** fireballs classified as current and Sentry-style rows as future
**So that** reports never mix observed airbursts with virtual impactors.

**Priority:** Must
**Requirements:** SR-ANL-02, SR-ANL-04, UR-03

**Acceptance criteria**

- Fixture fireball payloads produce class = current.
- Fixture risk-table payloads produce class = future.
- Classification is stored on the analyzed record, not decided only in the UI.

---

### US-19 — Compute an honest impact zone

**As a** geologist
**I want** the analyzer to compute a zone from published location and energy, or to mark the zone unconstrained
**So that** the map/report never shows a made-up city.

**Priority:** Must
**Requirements:** SR-ANL-03, UR-14, NFR-08, requirements §8

**Acceptance criteria**

- Published lat/lon → zone with those coordinates and a radius rule (energy-derived or documented default).
- Missing lat/lon → zone type unconstrained / location not published; coordinates remain null.
- Unit tests cover both branches with fixtures.

---

### US-20 — Upsert analyzed records (idempotent)

**As a** developer
**I want** re-analyzing the same payload version to update the serving row, not duplicate it
**So that** reports stay unique per object/event.

**Priority:** Must
**Requirements:** SR-ANL-05, SR-EVT-05

**Acceptance criteria**

- Processing the same payload id twice yields one serving record.
- Duplicate `collection.completed` events do not create duplicate zones.

---

### US-21 — Mark unparseable payloads failed

**As an** operator
**I want** poison payloads marked failed with a reason
**So that** one bad HTML change does not stall the whole analyzer.

**Priority:** Must
**Requirements:** SR-ANL-07, SR-MON-05

**Acceptance criteria**

- A deliberately broken fixture is marked failed, with a stored reason.
- Subsequent good payloads still process.
- Failure is logged and counted.

---

## Epic E4 — Persistence and REST collaboration

### US-22 — Survive process restart

**As an** operator
**I want** analyzed zones to still be queryable after all three processes restart
**So that** memory is not the source of truth.

**Priority:** Must
**Requirements:** SR-PER-01, SR-PER-03, NFR-03

**Acceptance criteria**

- After restart, query API returns previously analyzed records.
- Web report still renders from the store.

---

### US-23 — Store raw, analyzed, and pipeline metadata

**As a** developer
**I want** the data store to hold raw payloads, analyzed zones, and last-run metadata
**So that** the dashboard can show freshness and we can re-analyze.

**Priority:** Must
**Requirements:** SR-PER-02, SR-PER-04

**Acceptance criteria**

- Logical entities exist for: raw_payload, impact_zone (or object + zone), pipeline_run.
- Records retain source and collected-at.
- Current vs future is a stored field.

---

### US-24 — Query impact zones via REST

**As an** aeroscientist (or the web UI acting for them)
**I want** a JSON API to list and get impact zones with the same filters as the form
**So that** the front end and any later client collaborate through a stable contract.

**Priority:** Must
**Requirements:** SR-API-01, SR-API-03, UR-05

**Acceptance criteria**

- `GET` list endpoint accepts the filter set from US-02 and returns JSON.
- `GET` by id returns one record or 404.
- Validation errors return 400 with a JSON error body.

---

### US-25 — Internal health and status REST

**As an** operator
**I want** each process to expose liveness and last-run status over HTTP
**So that** the platform and the dashboard can probe collector, analyzer, and web independently.

**Priority:** Must
**Requirements:** SR-API-02, SR-API-04, SR-MON-03

**Acceptance criteria**

- Web, collector, and analyzer each have a liveness endpoint that does not call CNEOS.
- Collector/analyzer status includes last success and last error when known.
- Liveness returns success if the process is up even if the last scrape failed.

---

### US-26 — Web reads serving data, not the live web

**As a** geologist
**I want** page loads to hit the store/API, not NASA, on every request
**So that** the app stays fast and does not scrape as a side effect of browsing.

**Priority:** Must
**Requirements:** SR-WEB-03, NFR-03

**Acceptance criteria**

- Rendering a report does not require outbound HTTP to public NEO sites.
- Tests can prove the web handler uses a repository/API double.

---

## Epic E5 — Event collaboration (messaging)

### US-27 — Collector and analyzer collaborate through events

**As a** developer
**I want** collector and analyzer to communicate via a message broker
**So that** the pipeline is event-driven (big-data ingest) rather than a hidden function call.

**Priority:** Must
**Requirements:** SR-EVT-01, SR-EVT-02

**Acceptance criteria**

- `collection.completed` is produced by the collector and consumed by the analyzer.
- `analysis.completed` is produced by the analyzer after a successful write.
- Collaboration does not require the web process to be running.

---

### US-28 — Events carry correlation identifiers

**As an** operator
**I want** events to include payload id, source, timestamp, and correlation id
**So that** I can join logs, store rows, and messages for one scrape.

**Priority:** Must
**Requirements:** SR-EVT-03, SR-MON-01

**Acceptance criteria**

- Published event schema includes those fields.
- Analyzer logs include the same correlation id when processing the event.

---

### US-29 — Store is the source of truth if the broker drops messages

**As an** operator
**I want** unprocessed raw rows to be analyzed even when a message was lost
**So that** a broker blip does not permanently skip a scrape.

**Priority:** Should
**Requirements:** SR-EVT-04, SR-EVT-05, SR-ANL-01

**Acceptance criteria**

- Analyzer has a scan path for raw payloads not yet analyzed.
- Duplicate events do not duplicate zones (US-20).

---

## Epic E6 — Quality (tests and doubles)

### US-30 — Unit-test parsers and zone math without the network

**As a** developer
**I want** unit tests for collector parsing and analyzer zone computation using fixtures
**So that** catalog HTML changes are caught without calling the live site in CI.

**Priority:** Must
**Requirements:** SR-UT-01, SR-UT-02, SR-UT-04, NFR-05

**Acceptance criteria**

- Fixture-based tests cover at least one fireball parse and one future-risk parse.
- Zone tests cover location-present and location-absent.
- `./gradlew test` runs them; they pass with outbound network disabled conceptually (no live HTTP in unit tests).

---

### US-31 — Unit-test form validation and report mapping

**As a** developer
**I want** unit tests for filter validation and report DTO mapping
**So that** the form and JSON API stay consistent.

**Priority:** Must
**Requirements:** SR-UT-03, UR-07

**Acceptance criteria**

- Invalid filter objects fail validation in tests.
- A sample analyzed record maps to the report columns in US-06.

---

### US-32 — Integration-test HTTP and the pipeline contract

**As a** developer
**I want** integration tests for web/REST handlers and for “raw in → zone out”
**So that** the three pieces still collaborate after refactors.

**Priority:** Must
**Requirements:** SR-IT-01, SR-IT-02, SR-IT-03, SR-IT-04

**Acceptance criteria**

- Flask handler tests cover home, filter/report, and JSON list/get.
- A pipeline-contract test inserts (or publishes) a fixture payload and asserts the query API returns the analyzed zone.
- These tests use doubles or an isolated store; they do not call live CNEOS.
- CI runs them.

---

### US-33 — Inject test doubles for HTTP, broker, and store

**As a** developer
**I want** fake HTTP clients, an in-memory bus, and a fake repository
**So that** unit tests are deterministic and do not need Docker for every class.

**Priority:** Must
**Requirements:** SR-TD-01, SR-TD-02, SR-TD-03, SR-TD-04

**Acceptance criteria**

- Collector worker is tested with a stub HTTP client that returns fixture bodies.
- Analyzer worker is tested with an in-memory publisher/subscriber.
- Web/API handlers are tested with a fake zone repository.
- Production adapters implement the same interfaces as the doubles.

---

## Epic E7 — Product environment, CI, CD

### US-34 — Run three processes in named environments

**As an** operator
**I want** local, ci, and production environments for web, collector, and analyzer
**So that** configuration and data never collide.

**Priority:** Must
**Requirements:** SR-ENV-01, SR-ENV-02, SR-ENV-03, SR-ENV-05

**Acceptance criteria**

- Documented env vars cover port, `APP`, store location, broker location, scrape interval, source URLs.
- Local uses isolated store (for example docker-compose services).
- CI uses a throwaway store or fakes; production is a separate store.

---

### US-35 — Package with Docker Compose

**As an** operator
**I want** to start the three processes the way the starter already does (one image, `APP` selects the JAR)
**So that** local and production-like runs match.

**Priority:** Must
**Requirements:** SR-ENV-04, SR-CD-02, NFR-06

**Acceptance criteria**

- Compose (or equivalent) can start web, collector, and analyzer on distinct ports.
- A fourth/fifth service for the store and broker is specified in architecture (not implemented in this phase).

---

### US-36 — Continuous integration on every push

**As a** developer
**I want** a CI pipeline that builds and tests on every push to the integration branch
**So that** a broken parser never sits unnoticed on main.

**Priority:** Must
**Requirements:** SR-CI-01, SR-CI-02, SR-CI-03

**Acceptance criteria**

- Push triggers build + `test` (unit and integration).
- Test failure fails the pipeline.
- CI has no credentials to the production store.

---

### US-37 — Continuous delivery of tested artifacts

**As an** operator
**I want** deployable JARs/images produced only from a passing CI run, with config supplied at deploy time
**So that** production runs the same bits that were tested.

**Priority:** Must
**Requirements:** SR-CD-01, SR-CD-03, SR-CD-04

**Acceptance criteria**

- Pipeline publishes the Docker image / JARs after tests pass.
- Production deploy uses those artifacts plus environment configuration.
- Web, collector, and analyzer can be deployed independently.

---

## Epic E8 — Production monitoring and instrumentation

### US-38 — Instrument the pipeline

**As an** operator
**I want** metrics for scrape and analysis success/failure, durations, records written, unprocessed raw count, and HTTP statuses
**So that** I can see pipeline health without reading every log line.

**Priority:** Must
**Requirements:** SR-MON-02, NFR-04

**Acceptance criteria**

- Each listed metric exists as a named instrument (counter/timer/gauge).
- Metrics are exposed in a way a production monitor can scrape or ingest (endpoint or log-metric convention, chosen at implementation).

---

### US-39 — Structured logs with correlation

**As an** operator
**I want** JSON logs including event type, source, and correlation/run id
**So that** I can trace one scrape through collector, broker, analyzer, and API.

**Priority:** Must
**Requirements:** SR-MON-01, SR-EVT-03

**Acceptance criteria**

- Processes log JSON (the starter JSON logger is the intended foundation).
- Collection and analysis log lines include correlation id when in a run.

---

### US-40 — Detect stale production data

**As an** operator (and as a scientist on the dashboard)
**I want** an explicit stale condition when collection or analysis has not succeeded within the threshold
**So that** silence is not mistaken for “no asteroids.”

**Priority:** Must
**Requirements:** SR-MON-04, UR-12, NFR-01

**Acceptance criteria**

- A freshness check compares last success to the threshold.
- The condition is visible in monitoring (metric or log) and on the web summary (US-07, US-11).

---

## Traceability matrix (requirements → stories)

| Requirement IDs | Stories |
| --- | --- |
| UR-01 | US-04 |
| UR-02 | US-05 |
| UR-03 | US-04, US-05, US-18 |
| UR-04 | US-08 |
| UR-05, UR-06 | US-02, US-24 |
| UR-07 | US-03, US-31 |
| UR-08 | US-06 |
| UR-09 | US-07 |
| UR-10 | US-04, US-09, US-19 |
| UR-11 | US-05, US-10 |
| UR-12 | US-07, US-11, US-40 |
| UR-13 | US-08 |
| UR-14 | US-09, US-19 |
| SR-WEB-01–05 | US-01, US-02, US-12, US-26 |
| SR-COL-01–06 | US-13 … US-16 |
| SR-ANL-01–07 | US-17 … US-21 |
| SR-UT-01–04 | US-30, US-31 |
| SR-PER-01–04 | US-14, US-22, US-23 |
| SR-API-01–04 | US-24, US-25 |
| SR-ENV-01–05 | US-34, US-35 |
| SR-IT-01–04 | US-32 |
| SR-TD-01–04 | US-33 |
| SR-CI-01–03 | US-36 |
| SR-MON-01–05 | US-11, US-15, US-21, US-25, US-38, US-39, US-40 |
| SR-EVT-01–05 | US-16, US-17, US-20, US-27, US-28, US-29 |
| SR-CD-01–04 | US-35, US-37 |
| NFR-01–08 | US-11, US-12, US-14, US-19, US-22, US-26, US-30, US-35, US-40 |

Every rubric row in [requirements.md](requirements.md) §10 is covered by at least one Must story.

---

## Out of scope stories (Won’t, this phase)

| ID | Story | Reason |
| --- | --- | --- |
| US-X1 | As a civil-defense officer I want push alerts to phones | Product is a scientific workstation, not a public warning system |
| US-X2 | As a user I want to log in with a university SSO | AuthN is not required in requirements |
| US-X3 | As a geologist I want a full GIS workstation | Tabular + summary reports satisfy the rubric; maps can come later |
| US-X4 | As an aeroscientist I want the system to discover unpublished impactors | We consume published catalogs only |

These are recorded so they are not accidentally treated as missing Must stories.
