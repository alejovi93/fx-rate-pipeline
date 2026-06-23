# Design Note

## Data source

frankfurter.dev v2 was selected as the data source. It is free, requires no API key, and sources rates directly from the European Central Bank. 
The ECB provider filter was applied explicitly to ensure official reference rates rather than blended estimates.

## Historical window

YTD from January 1st of the current year. This window is sufficient to support all required metrics (YTD change, daily change, trend) and keeps the output file lightweight for Power BI. The pipeline can be extended to multi-year history by changing START_DATE.

## Cross pair computation

All 42 cross pairs are computed in Python via a self-join on date, using EUR as a pivot: rate(A/B) = rate(B/EUR) / rate(A/EUR). 
This approach guarantees internal consistency and avoids fetching redundant data from the API. Cross pairs are materialized in the CSV as required by the functional scope.

## Output format

Long format was chosen over wide format. Each row represents one currency pair for one date. Adding a currency requires no schema change.

## Metrics

Daily change and YTD metrics are implemented as DAX measures in Power BI rather than precomputed columns. This keeps the Python layer focused on extraction and transformation, and gives Power BI full flexibility to recalculate metrics dynamically based on slicer selections.

## Trade-offs

- frankfurter.dev has no SLA. In production, a more resilient source or a caching layer would be needed.
- The pipeline overwrites the CSV on every run. An append mode with deduplication would be more suitable for production scheduling.
- In a production environment, the pandas self-join would be replaced with a SQL transformation layer for better scalability.