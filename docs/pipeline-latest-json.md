# The pipeline's "latest" file for the home page sky

malavnaik.com's hero shows every Dublinbikes station as a light.

**Status: live since 16 Nov 2026.** The pipeline (**malavnaik99/dublin-data-pipeline**, `transform.py` → `sky()`) publishes
the file below every hour, and `_data/sky_live.json` points at it:
`https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-marts/resolve/main/sky/latest.json`
(Hugging Face sends `Access-Control-Allow-Origin: https://malavnaik.com`, so the page can read it). If it is over two
hours old, the page shows the saved snapshot in `_data/sky.json` instead. What to do when it breaks: `MAINTENANCE.md`.

How it was built differs from the original request below in one way: STATION118 is dropped in `dim_station`, but stations
reporting 0 docks are only left out of this file, not the marts. Parnell Square North's feed reports 0 docks, yet its bike
counts are real, so the marts keep it.

The prompt that set it up is kept below as the reference for the file's format.

---

**Prompt for the dublin-data-pipeline repo**

> In this repo (malavnaik99/dublin-data-pipeline), on a new branch, add one small output to the pipeline run that
> already publishes the marts to the Hugging Face dataset `Malavnaik/dublin-bikes-weather-marts`:
>
> 1. On every run, write `sky/latest.json` to that same dataset (same token and upload step as the marts). Format, exactly:
>    ```json
>    {"source": "Dublin bikes pipeline, hourly averages", "generated_utc": "2026-11-12T09:15:00Z",
>     "hours": ["2026-11-10T10:00", "... 48 local Europe/Dublin hours, oldest first ..."],
>     "stations": [["Station Name", 53.34611, -6.26835, 29], "... [name, lat, lon, capacity] ..."],
>     "bikes": [[12, 11, null, "... one number per hour, null if missing ..."], "... one row per station, same order ..."]}
>    ```
>    - `generated_utc`: when this file was made (UTC, ISO 8601 with Z).
>    - `hours`: the last 48 hours in `fct_station_hour`, as local Dublin time `YYYY-MM-DDTHH:00`, oldest first.
>    - `stations`: from `dim_station`; names in normal capitals ("O'Connell Street", not "O'CONNELL STREET"),
>      coordinates rounded to 5 decimals.
>    - `bikes`: `round(avg_bikes)` from `fct_station_hour`.
>    - Leave out the placeholder station `STATION118` and every station with `capacity = 0`.
>    - Keep it small (about 20 KB): no other columns, no indentation.
> 2. Fix STATION118 at the source too: exclude it in the staging model (or `dim_station`), and add a dbt test that fails
>    if any station has capacity 0 or a name like 'STATION%'. Keep the existing 14 tests passing.
> 3. Make sure the file can be read from a browser on another site: `https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-marts/resolve/main/sky/latest.json`
>    must answer with an `Access-Control-Allow-Origin` header. Check it with
>    `curl -sI <that URL> -H "Origin: https://malavnaik.com"` and tell me the result. If Hugging Face doesn't send that header,
>    stop and tell me (we'll publish the file somewhere else instead).
> 4. Test the run once by hand, show me the first 300 characters of the published file, then open a pull request. Don't merge it.

---

**On malavnaik.com (done 16 Nov 2026):** the URL is in `_data/sky_live.json` (`"url": "…"`). The sky uses live data whenever
the file is under two hours old (otherwise it shows the snapshot and says "saved snapshot"). The hourly **Bike sky
freshness** action opens an issue if the file goes stale. Empty that `url` to switch live data off.
