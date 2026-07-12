<p align="center">
  <a href="https://opendataodc.com/">
    <img src="assets/opendataodc-mark.png" alt="OpenDataODC logo" width="96">
  </a>
</p>

# OpenDataODC Index

[OpenDataODC](https://opendataodc.com/) is a searchable catalog for open data contracts and source dataset links. This repo is the public contribution index for dataset references.

Dataset references are reviewed by humans before ingestion. OpenDataODC uses these source facts to build the searchable catalog.

## Contributing a dataset

1. Add one YAML file under `datasets/by-domain/<source-domain>/<short-topic>/<dataset-id>.yml`.
2. Keep the YAML small. Do not add internal policy, crawl, storage, or review fields.
3. Run `make check`.
4. Open a pull request and use the PR body for human review notes.

## Dataset YAML fields

Required fields:

- `dataset_id`: lowercase ASCII slug, for example `cms-asp-pricing-files`.
- `title`: human-readable dataset name. Non-ASCII names are allowed, for example `Météo France observations` or `東京都オープンデータ`.
- `source_url`: provider page, feed, file, or API URL.
- `source_domain`: provider domain, for example `cms.gov`.
- `source_type`: one of `api`, `rss`, `html_page`, `file`, or `mixed`.
- `update_frequency`: one of `daily`, `weekly`, `monthly`, `quarterly`, `yearly`, or `adhoc`.
- `geography`: optional countries, regions, or cities covered by the dataset, for example `[United States]`.
- `license.name`: short license or terms label.
- `license.url`: URL where reviewers can verify terms.

Optional fields:

- `source_hints.rss_url`: RSS feed URL, or `null` if unknown.
- `source_hints.api_url`: API URL, or `null` if unknown.
- `source_hints.file_formats`: expected formats such as `[zip, csv]`.

Public contributors only provide source facts. Internal processing rules live outside this public repo.

## Local checks

```bash
make check
```

Pull requests are reviewed by humans only for now.

## Links

- Site: https://opendataodc.com/
- Catalog: https://opendataodc.com/catalog/
