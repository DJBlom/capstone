# Impact Sentinel — User and System Requirements

**Product:** Impact Sentinel
**Status:** Requirements only (no implementation in this phase)
**Primary users:** Geologists; aeroscientists (planetary / aerospace scientists who study near-Earth objects)
**Architecture style:** Big-data ingest → event pipeline → analyze → persist → serve

Impact Sentinel monitors **current** asteroid-related impact events (observed fireballs and bolides) and **future** impact risk (published virtual-impactor / Sentry-style risk) and presents **impact zones** through a web application.

---

## 1. Product vision

Geologists and aeroscientists need a single place to see where Earth has recently experienced asteroid airbursts or impacts, and where published risk models say impacts could occur in the future. Public catalogs already exist (for example NASA CNEOS Sentry and Fireballs pages), but they are not assembled into a filterable **impact-zone** report for these two scientific audiences.

Impact Sentinel will:

1. **Collect** published near-Earth object (NEO) risk and fireball data from the public web (scraper / ingest workers).
2. **Analyze** that data into normalized objects, impact probabilities, energies, and geographic or global impact zones.
3. **Persist** raw and analyzed records.
4. **Serve** them through a web application (filter form + reports) and REST endpoints.

This document states **what** the product must do. See [stories.md](stories.md) for user stories and [architecture.md](architecture.md) for major components and diagrams.

---

## 2. Personas

| Persona | Who they are | What they need from Impact Sentinel |
| --- | --- | --- |
| Geologist | Studies impact sites, airburst effects, and ground/ocean consequences | Location (when known), estimated energy, affected-radius / zone class, whether the event is observed vs predicted, and a report they can filter by region and date |
| Aeroscientist | Studies NEO orbits, close approaches, and impact probability | Object designation, potential impact dates, impact probability, Torino / Palermo-style risk scales, and a report they can filter by risk and time window |
| Operator | Runs the product in a deployed environment | Health of collector, analyzer, store, and message bus; freshness of data; logs and metrics |
| Developer | Builds and verifies the product | Automated tests, test doubles for external sites and brokers, CI, and a path to deploy |

End-user requirements below are written for geologists and aeroscientists. Operator and developer needs appear as system requirements.

---

## 3. Glossary

| Term | Meaning in this product |
| --- | --- |
| NEO | Near-Earth object (asteroid or comet whose orbit brings it near Earth) |
| Fireball / bolide | A bright meteor; used here as a **current / observed** atmospheric impact or airburst |
| Sentry-style risk | Published future impact-risk entries (virtual impactors) with probability and energy estimates |
| Impact zone | The geographic or global region associated with an observed event or a future risk entry: a lat/lon plus energy-derived radius when location is known, otherwise an unconstrained Earth-impact classification |
| Current zone | An observed fireball/bolide within the configured recency window |
| Future zone | A published potential impact that has not occurred |
| Raw payload | The HTML, CSV, or JSON document as collected, stored before analysis |
| Analyzed record | Normalized object + zone produced by the analyzer |

---

## 4. Scope

### In scope for the product (later implementation)

- Web application with a basic filter form and reporting views
- Data collector that scrapes public web sources on a schedule
- Data analyzer that parses, classifies, and computes impact zones
- Persistence of raw and analyzed data
- REST collaboration (public query API and internal health/status APIs)
- Event collaboration over a message broker
- Unit tests, integration tests, and test doubles
- Distinct product environments
- Continuous integration and continuous delivery
- Production monitoring and instrumentation

### Out of scope for this documentation phase

- Writing or changing application code
- Choosing a final cloud vendor
- Building a high-fidelity globe or GIS workstation
- Orbital determination from raw astrometry (we consume published catalogs)
- Sending emergency alerts to civil authorities
- Authentication / multi-tenant accounts (single shared scientific workstation app)

### Out of scope for the product (unless later required)

- Predicting unpublished impactors the catalogs do not list
- Legal notice to the public; this is a scientific monitoring workstation, not a warning siren

---

## 5. User requirements

User requirements describe capabilities geologists and aeroscientists need. Each has an ID for traceability into [stories.md](stories.md).

### 5.1 Monitoring current and future impact zones

| ID | Requirement | Rationale |
| --- | --- | --- |
| UR-01 | A user shall be able to view a dashboard of **current** impact zones (recent observed fireballs/bolides), including location when published, estimated energy, and collection freshness. | Geologists need observed events; aeroscientists need to separate observed from predicted. |
| UR-02 | A user shall be able to view a dashboard of **future** impact zones (published potential impacts), including object designation, potential impact date window, impact probability, and risk-scale values when published. | Future risk is the Sentry-style monitoring problem. |
| UR-03 | A user shall be able to distinguish current vs future records in every list and detail view. | Mixing observed airbursts with virtual impactors would be scientifically misleading. |
| UR-04 | A user shall be able to open a **detail view** for one object or event: identifiers, source, raw-derived fields, computed zone, and last-updated time. | Both personas drill from a report into a single object. |

### 5.2 Basic form (query / filter)

| ID | Requirement | Rationale |
| --- | --- | --- |
| UR-05 | A user shall be able to submit a **filter form** with at least: time window, current vs future vs both, object designation (optional), minimum impact probability (optional), minimum risk scale (optional), and geographic region or bounding box (optional). | Rubric: basic form. Scientists will not page through the full catalog. |
| UR-06 | Submitting the form shall produce a result set that matches the filters, or a clear empty state if nothing matches. | Form without reporting is incomplete. |
| UR-07 | Invalid form input (bad dates, inverted ranges, non-numeric probability) shall be rejected with a visible validation message and shall not crash the application. | Workstation reliability. |

### 5.3 Reporting

| ID | Requirement | Rationale |
| --- | --- | --- |
| UR-08 | A user shall be able to view a **tabular report** of impact zones that includes designation/event id, class (current/future), time, probability or “observed”, energy, zone summary, and source. | Rubric: reporting. |
| UR-09 | A user shall be able to view a **summary report**: counts of current vs future records, highest-probability future object, most energetic recent fireball, and last successful collection/analysis times. | Quick situational awareness. |
| UR-10 | A geologist-oriented reading of a zone shall include estimated energy and a zone description usable for ground-effect thinking (location and energy-derived radius when known; otherwise “location unconstrained”). | Geologist persona. |
| UR-11 | An aeroscientist-oriented reading of a zone shall include probability, date window, and published risk-scale fields when present. | Aeroscientist persona. |
| UR-12 | Reports shall show **data freshness** (last successful scrape and last successful analysis). Stale data shall be labeled, not silently shown as current. | Scientific use depends on knowing whether the catalog is up to date. |

### 5.4 Trust and transparency

| ID | Requirement | Rationale |
| --- | --- | --- |
| UR-13 | A user shall be able to see which public source a record came from (for example CNEOS Fireballs vs CNEOS Sentry). | Traceability of scientific data. |
| UR-14 | When a source does not publish a geographic location for a future impactor, the product shall say so rather than inventing coordinates. | Honest impact-zone semantics. |

---

## 6. System requirements

System requirements are grouped by rubric area. They are the obligations of the software, environments, and delivery machinery.

### 6.1 Web application (basic form, reporting)

| ID | Requirement |
| --- | --- |
| SR-WEB-01 | The product shall provide a server-rendered web application as the primary user interface (Flask is the web framework; `src/app.py` is the intended home). |
| SR-WEB-02 | The web application shall host the filter form specified in UR-05 and the reports specified in UR-08 and UR-09. |
| SR-WEB-03 | The web application shall obtain report data from the serving layer (data store and/or REST API), not by scraping the public web itself. |
| SR-WEB-04 | The web application shall remain usable when the collector or analyzer is temporarily down, showing the last persisted analyzed data plus a freshness/health warning. |
| SR-WEB-05 | Static assets (styles, images) shall be served by the web application. |

### 6.2 Data collection

| ID | Requirement |
| --- | --- |
| SR-COL-01 | A **data collector** worker shall scrape the public web for NEO impact-risk and fireball publications needed by the product. Primary intended sources: CNEOS Sentry risk listings (future) and CNEOS Fireballs (current). Close-approach listings may be collected as supporting context. |
| SR-COL-02 | Collection shall run on a schedule (the existing `WorkScheduler` / worker pattern is the intended mechanism). |
| SR-COL-03 | Each successful collection shall store the **raw payload** (body, source URL, collected-at timestamp, HTTP status) before analysis. |
| SR-COL-04 | Collection failures (timeouts, non-success HTTP, empty body, parse-unready content) shall be logged, shall not crash the worker process, and shall be visible to monitoring. |
| SR-COL-05 | The collector shall identify sources politely (user-agent, bounded rate) and shall not hammer public sites. |
| SR-COL-06 | After storing a raw payload, the collector shall publish a **collection event** on the message broker (see §6.12). |

### 6.3 Data analyzer

| ID | Requirement |
| --- | --- |
| SR-ANL-01 | A **data analyzer** worker shall consume collection events (and/or scan unprocessed raw payloads) and parse them into normalized records. |
| SR-ANL-02 | The analyzer shall classify each record as **current** (observed fireball/bolide) or **future** (published potential impact). |
| SR-ANL-03 | The analyzer shall compute an **impact zone**: latitude/longitude and energy-derived radius when the source provides location; otherwise an explicit unconstrained-Earth-impact zone. It shall not fabricate coordinates. |
| SR-ANL-04 | The analyzer shall map published energy, probability, and risk-scale fields into a single analyzed schema so the web report does not depend on HTML layout. |
| SR-ANL-05 | Analysis shall be idempotent for the same raw payload version (re-processing shall update, not duplicate, the serving record). |
| SR-ANL-06 | After writing analyzed records, the analyzer shall publish an **analysis-completed event** on the message broker. |
| SR-ANL-07 | Unparseable payloads shall be marked failed with a reason; they shall not block processing of other payloads. |

### 6.4 Unit tests

| ID | Requirement |
| --- | --- |
| SR-UT-01 | Collector parsing, URL/source handling, and failure classification shall have unit tests that do not call the live public web. |
| SR-UT-02 | Analyzer classification, zone computation, and idempotent upsert logic shall have unit tests with fixture payloads. |
| SR-UT-03 | Web form validation and report-model mapping shall have unit tests. |
| SR-UT-04 | Unit tests shall run via the existing Gradle / JUnit toolchain (`./gradlew test`). |

### 6.5 Data persistence (any data store)

| ID | Requirement |
| --- | --- |
| SR-PER-01 | The product shall persist data in a durable data store that survives process restart. Any store that can hold structured records is acceptable; the intended serving store is a relational database (for example PostgreSQL). |
| SR-PER-02 | The store shall hold at least: raw collection payloads, analyzed objects/events, computed impact zones, and pipeline run metadata (last success/failure). |
| SR-PER-03 | The web application and REST API shall read analyzed data from the store, not from in-memory-only caches as the source of truth. |
| SR-PER-04 | Schema shall distinguish current vs future records and shall retain source URL and collected-at for audit. |

### 6.6 REST collaboration (internal or API endpoint)

| ID | Requirement |
| --- | --- |
| SR-API-01 | The product shall expose a **query REST API** for analyzed impact zones (list + get-by-id) using the same filters as the web form, returning JSON. This is the collaboration surface for the web UI and any later scientific client. |
| SR-API-02 | Collector and analyzer processes shall expose **internal REST** health/status endpoints (liveness, last run, last success, last error). |
| SR-API-03 | REST error responses shall use appropriate HTTP status codes (400 validation, 404 missing, 503 dependency down) and a JSON error body. |
| SR-API-04 | Internal status endpoints shall not require the public web sources to be reachable in order to answer liveness. |

### 6.7 Product environment

| ID | Requirement |
| --- | --- |
| SR-ENV-01 | The product shall run as three collaborating processes: a Flask web application (`src/app.py`), a data collector, and a data analyzer. |
| SR-ENV-02 | At least three named environments shall be defined: **local**, **ci**, and **production**. A staging environment is recommended as a promotion step for continuous delivery. |
| SR-ENV-03 | Environment-specific configuration (ports, store location, broker location, scrape interval, source URLs) shall be injected via environment variables, not hard-coded. |
| SR-ENV-04 | Local and production-like runs shall be expressible with the existing Docker / `docker-compose` packaging (one image, `APP` selects the process). |
| SR-ENV-05 | Each environment shall use an isolated data store so tests and local work cannot overwrite production records. |

### 6.8 Integration tests

| ID | Requirement |
| --- | --- |
| SR-IT-01 | Integration tests shall exercise HTTP handlers of the web app and REST API (for example Flask's test client). |
| SR-IT-02 | At least one integration test shall cover the pipeline contract: a raw payload in the store (or a published collection event) results in an analyzed zone that the query API can return. |
| SR-IT-03 | Integration tests shall not depend on the live CNEOS site being up; they shall use fixtures and test doubles. |
| SR-IT-04 | Integration tests shall be runnable in CI on every pipeline run. |

### 6.9 Mock objects / test doubles

| ID | Requirement |
| --- | --- |
| SR-TD-01 | HTTP calls to public web sources shall be replaceable with a test double (fake HTTP client or stubbed responses). |
| SR-TD-02 | The message broker shall be replaceable with a test double (in-memory publisher/subscriber) in unit tests. |
| SR-TD-03 | The data store shall be replaceable with a fake repository in unit tests. |
| SR-TD-04 | Collector and analyzer workers shall depend on interfaces (HTTP, store, bus), not concrete live services, so doubles can be injected. |

### 6.10 Continuous integration

| ID | Requirement |
| --- | --- |
| SR-CI-01 | Every push to the main integration branch shall trigger a CI pipeline that builds the project and runs unit and integration tests. |
| SR-CI-02 | CI shall fail the build on test failure; a failing pipeline shall be treated as not shippable. |
| SR-CI-03 | CI shall run in a clean environment with no access to production data stores. |

### 6.11 Production monitoring (instrumenting)

| ID | Requirement |
| --- | --- |
| SR-MON-01 | All three processes shall emit **structured logs** (JSON logs already exist in `support/logging-support`) including event type, source, and correlation/run id where applicable. |
| SR-MON-02 | The product shall instrument at least: scrape success/failure counts, scrape duration, analysis success/failure counts, analysis duration, records written, consumer lag or “unprocessed raw payload” count, and HTTP request counts/status for the web and REST surfaces. |
| SR-MON-03 | Each process shall expose a health endpoint suitable for a platform probe. |
| SR-MON-04 | Production shall be able to detect **stale data** (no successful collection or analysis within a configured threshold) and surface it in logs/metrics and on the web dashboard. |
| SR-MON-05 | Unhandled worker exceptions shall be logged at error severity and counted; they shall not silently drop the scheduler. |

### 6.12 Event collaboration (messaging)

| ID | Requirement |
| --- | --- |
| SR-EVT-01 | Collector and analyzer shall collaborate through a **message broker** (event collaboration), not only through synchronous REST calls. |
| SR-EVT-02 | At minimum the broker shall carry: `collection.completed` (raw payload stored; ready to analyze) and `analysis.completed` (zones updated). |
| SR-EVT-03 | Events shall include a payload identifier, source, timestamp, and a correlation id so logs and records can be joined. |
| SR-EVT-04 | If the broker is unavailable, the collector shall still persist raw payloads; the analyzer shall be able to recover by scanning unprocessed raw records (events are the fast path, the store is the source of truth). |
| SR-EVT-05 | Consumers shall be safe to receive a duplicate event (at-least-once delivery assumed). |

### 6.13 Continuous delivery

| ID | Requirement |
| --- | --- |
| SR-CD-01 | A successful CI build shall produce deployable artifacts (the existing Gradle JAR + Docker image flow). |
| SR-CD-02 | Delivery shall be able to deploy the three processes independently (web, collector, analyzer) using the same image and different `APP` / port settings. |
| SR-CD-03 | Promotion to production shall only occur from an artifact that passed CI tests. |
| SR-CD-04 | Configuration for production (store, broker, source URLs, intervals) shall be supplied at deploy time, not baked into the artifact beyond defaults. |

---

## 7. Non-functional requirements

| ID | Category | Requirement |
| --- | --- | --- |
| NFR-01 | Freshness | A healthy production system shall attempt collection often enough that fireball dashboards are no more than 24 hours behind source publication, unless the source is down (in which case freshness shall be labeled). |
| NFR-02 | Integrity | Analyzed records shall be reproducible from stored raw payloads. |
| NFR-03 | Availability | Web reporting shall not require a live scrape on each page load. |
| NFR-04 | Observability | A developer or operator shall be able to answer “did we scrape, did we analyze, how old is the data?” from logs, metrics, and the dashboard without SSH-debugging the JVM. |
| NFR-05 | Testability | External network and broker shall not be required to run the unit test suite. |
| NFR-06 | Portability | The three processes shall run locally (JAR or Docker Compose) and in a containerized production environment. |
| NFR-07 | Time | All stored timestamps shall be UTC. |
| NFR-08 | Honesty | Missing geographic data shall remain missing; the UI shall not plot a fake point. |

---

## 8. Data rules the analyzer must honor

These rules exist so user-facing “impact zone” has a defined meaning.

1. **Current zone** comes from an observed fireball/bolide with a published time. If latitude and longitude are published, the zone is that point plus a radius derived from published energy (or a documented default radius when energy is missing). If location is missing, the zone is “observed, location not published.”
2. **Future zone** comes from a published potential-impact / virtual-impactor entry. If a geographic corridor is published, use it. If only a global impact probability is published (typical of many Sentry table rows), the zone is “future Earth impact, location unconstrained” plus probability, date window, and energy.
3. **Never** interpolate a country or city from probability alone.
4. **Source fields** that are not present stay null; the report shows “not published.”

---

## 9. Intended public sources (collector)

The collector is specified as a **web scraper**. Exact selectors are an implementation detail. Intended public pages:

| Source | Role | Typical record |
| --- | --- | --- |
| CNEOS Sentry risk table | Future impact risk | Designation, potential impact dates, probability, Palermo/Torino-style scales, estimated energy / diameter |
| CNEOS Fireballs | Current/recent observed events | Peak brightness time, lat/lon, altitude, velocity, energy |
| CNEOS close approaches (optional supporting) | Context for aeroscientists | Object, date, distance, velocity |

If a source offers both HTML and a machine file at the same URL family, the collector may fetch the machine file; that is still collection from the public web and must still persist the raw payload.

---

## 10. Traceability to the course rubric

| Rubric item | Requirement IDs | How the product meets it |
| --- | --- | --- |
| Web application — basic form, reporting | UR-05–UR-12, SR-WEB-01–05 | Filter form + tabular and summary reports in the Flask front end |
| Data collection | SR-COL-01–06 | Scheduled scraper worker |
| Data analyzer | SR-ANL-01–07, §8 | Parse, classify current/future, compute zones |
| Unit tests | SR-UT-01–04 | Gradle/JUnit unit tests with fixtures |
| Data persistence — any data store | SR-PER-01–04 | Durable store for raw + analyzed data |
| REST collaboration — internal or API | SR-API-01–04 | Query API + internal health/status |
| Product environment | SR-ENV-01–05 | Local, CI, production; Docker Compose |
| Integration tests | SR-IT-01–04 | HTTP and pipeline-contract tests in CI |
| Mock objects / test doubles | SR-TD-01–04 | Fake HTTP, bus, and repository |
| Continuous integration | SR-CI-01–03 | Build and test on every push |
| Production monitoring — instrumenting | SR-MON-01–05, NFR-04 | JSON logs, metrics, health, freshness |
| Event collaboration — messaging | SR-EVT-01–05 | Broker events between collector and analyzer |
| Continuous delivery | SR-CD-01–04 | Tested artifacts deployed as three processes |

---

## 11. Assumptions and open decisions (not blocking this phase)

These are recorded so later implementation does not pretend they were decided here.

| Topic | Assumption for requirements | Can change later |
| --- | --- | --- |
| Serving store | Relational database (PostgreSQL-class) | Any durable store |
| Message broker | Any at-least-once broker (Kafka or RabbitMQ class) | Implementation choice |
| AuthN | None; trusted scientific users on a shared app | Add if the course requires it |
| Map UI | Optional later; reports are tabular + summary first | GIS view is not required to satisfy UR-08 |
| Scrape interval | Configurable; NFR-01 sets a 24h freshness goal | Tune in operations |

---

## 12. Related documents

- [stories.md](stories.md) — user stories derived from these requirements
- [architecture.md](architecture.md) — major components and design diagrams
