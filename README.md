# opendataodc-index

Public dataset reference index for OpenDataODC.

Dataset references are organized to mirror object-storage catalog paths. New datasets are submitted by pull request and require human approval before ingestion.

The current fixture is CMS ASP pricing files under `datasets/by-domain/cms.gov/asp-pricing-files/asp-pricing-files.yml`.

## Contributing a dataset

1. Add one YAML file under `datasets/by-domain/<source-domain>/<short-topic>/<dataset-id>.yml`.
2. Keep the YAML small. Do not add backend-only policy fields or R2 prefix fields.
3. Run `make manifest` to regenerate the sharded files under `index/`.
4. Run `make check`.
5. Open a pull request and use the PR body for human review notes.

## Dataset YAML fields

Required fields:

- `dataset_id`: lowercase slug, for example `cms-asp-pricing-files`.
- `title`: human-readable dataset name.
- `source_url`: provider page, feed, file, or API URL.
- `source_domain`: provider domain, for example `cms.gov`.
- `source_type`: one of `api`, `rss`, `html_page`, `file`, or `mixed`.
- `update_frequency`: one of `daily`, `weekly`, `monthly`, `quarterly`, `yearly`, or `adhoc`.
- `license.name`: short license or terms label.
- `license.url`: URL where reviewers can verify terms.

Optional fields:

- `source_hints.rss_url`: RSS feed URL, or `null` if unknown.
- `source_hints.api_url`: API URL, or `null` if unknown.
- `source_hints.file_formats`: expected formats such as `[zip, csv]`.

The `index/` directory is generated. It is split by domain and shard, and each shard derives `r2_prefix` from `source_domain` and `dataset_id` so contributors cannot accidentally create conflicting storage paths.

## Local checks

```bash
make manifest
make check
```

`index/` is generated from `datasets/**/*.yml`. Pull requests are reviewed by humans only for now.
