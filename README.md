# CMOrienta

**CMOrienta** is a platform designed to make it easier for students in the Molecular Sciences course to find potential academic advisors.

**Status:** Under development

## Problem

The interdisciplinary nature of BSc Molecular Sciences degree gives students access to research across many USP institutes and departments. However, finding a potential advisor currently requires navigating multiple institutional websites and extensive faculty lists.

This makes it difficult to efficiently discover researchers based on specific research interests.

## Solution

CMOrienta centralizes advisor information from different USP institutes into a single searchable platform.

Students can:

* Search advisors by name and research interests
* Filter by institute and department
* Access institutional profiles and contact information
* Explore researchers across different areas of the university

The project also includes a data collection pipeline to standardize publicly available information from institutional websites.

## Technologies

* **Frontend:** React, Vite, CSS
* **Backend:** Node.js, Express
* **Data collection:** Python, Requests, BeautifulSoup
* **Database:** Supabase / PostgreSQL

### Architecture

```text
USP Websites → Python Scrapers → PostgreSQL
                                  ↓
                            Node.js API
                                  ↓
                              React UI
```

## Outcomes

The project establishes a centralized, searchable database of potential advisors across USP.

The initial implementation includes:

* Automated data collection from institutional faculty pages
* Standardized advisor records
* Search and filtering functionality
* Integration between scrapers, database, API, and frontend

## Roadmap

* [ ] Expand coverage to additional USP institutes
* [ ] Automate periodic database updates
* [ ] Improve extraction of research interests and keywords
* [ ] Implement semantic search
* [ ] Develop AI-assisted advisor matching
* [ ] Deploy the platform

---

Copyright © 2026 Júlia Chaves Neuenschwander Magalhães. All Rights Reserved.

This repository is publicly available for viewing and academic/portfolio reference. No permission is granted to copy, modify, distribute, or use the source code for other purposes without prior written permission.
