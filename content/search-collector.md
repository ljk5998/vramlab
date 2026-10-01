---
title: "VRAMLab Weekly Search Collector"
layout: "single"
url: "/search-collector/"
description: "The private search performance tool used to prepare VRAM Lab's weekly operating reports, with its data practices and terms of use."
draft: false
showToc: true
ShowReadingTime: false
ShowBreadCrumbs: false
---

_Last updated: 2026-10-01._

**VRAMLab Weekly Search Collector** is the site owner's private tool for preparing weekly reports about Google Search performance for `vramlab.com`. It runs in Google Apps Script and saves data from the official Google Search Console API to a spreadsheet controlled by the owner.

The collected metrics include clicks, impressions, click-through rate, and average search position, grouped by date, search query, page, country, and device. These metrics help the owner identify changes in search performance and decide which articles need attention.

[Privacy policy](#privacy-policy) · [Terms of use](#terms-of-use) · [Contact](/contact/)

## Privacy policy

### Access and purpose

The owner authorizes Search Console read access, access to the spreadsheet containing the tool, and connections to external services. The Search Console permission covers the account's verified sites; the collector's code requests only `vramlab.com` data. The spreadsheet permission is limited to the spreadsheet in which the tool is installed. External requests retrieve data from Google's Search Console API.

The tool uses this data to record search performance and prepare private operating reports. Search Console may omit anonymized or low-volume queries, and different grouping methods can produce different totals.

### Storage and report processing

Search metrics and collection status are stored in the owner's Google spreadsheet. Google Apps Script manages the account authorization. Collection logs record dates, status, and row counts without recording authorization tokens or query text.

The owner has connected this spreadsheet to ChatGPT so Dots can read it and prepare weekly reports in the owner's conversation. Google provides the API, script runtime, and spreadsheet storage; OpenAI processes data used in ChatGPT reports under the owner's account settings and the applicable OpenAI policies.

Raw search data, account credentials, and the private spreadsheet are not published on this website. The collector does not use the data for advertising or sell it to other parties.

### Retention and control

Spreadsheet records remain until the owner removes them. The owner can review or revoke the tool's access in [Google Account connections](https://myaccount.google.com/connections), remove its execution triggers, and delete the spreadsheet records. ChatGPT report history and connected-app access are controlled separately through the owner's ChatGPT account.

Questions about this tool's data practices can be sent through [Contact](/contact/). The separate [website Privacy Policy](/privacy-policy/) describes information handled when visiting VRAM Lab.

## Terms of use

This tool is operated by the VRAM Lab site owner for their own reporting. It has no public registration or public account connection service. Access to the underlying script and spreadsheet requires the owner's permission.

The tool uses an account that already has access to the relevant Search Console property. Google's API and Apps Script limits apply. Data availability, omitted queries, and collection failures must be considered when interpreting a report.

VRAM Lab does not charge a fee for this tool. Use of Google services and ChatGPT remains subject to the owner's arrangements with those providers and their applicable terms. The owner can stop collection by removing the script's triggers or revoking its authorization.
