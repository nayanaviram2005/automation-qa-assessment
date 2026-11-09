# Bonus - Uptime Monitor (n8n)

Pings the Task 1 app every 5 minutes and posts to the same Discord channel as Task 2 when it does not answer 200.

## Files
- `Bonus_UptimeMonitor_NayanaviramPanigrahi.json` - import via n8n: Workflows > Import from File. Select your own Discord credential on the two Discord nodes (the file holds the placeholder id `REPLACE_ME`).
- `Bonus_Screenshot_Workflow.jpg` - canvas after a healthy run.
- `Bonus_Screenshot_DownAlert.jpg` - the alert node after the app was stopped.
- `build_monitor.py` - generator for the JSON.

## Flow
1. **Every 5 Minutes** (Schedule trigger).
2. **Stamp Start** (Code): records the start time.
3. **Ping App**: `GET http://localhost:3000/api/tags` with a 10 s timeout. "Never error" and "full response" are on, so any status code (404, 500) is returned as data instead of throwing. **Retry logic:** the node retries up to 3 times, 3 s apart, when there is no response at all (connection refused, timeout). If all three fail it continues with an error item instead of stopping.
4. **Evaluate Check** (Code): computes response time in ms (start to finish, including retries), works out the status (0 when there was no response), and keeps a rolling history of the last 600 checks in the workflow's static data. It also counts how many failed checks happened in a row.
5. **Status Is 200?** (IF): true goes to a no-op; false goes to **Send Down Alert**, which posts the reason, response time, consecutive-failure count, URL and time.
6. **Daily 9am Summary** (Schedule, cron `0 9 * * *`) -> **Build Summary** -> **Send Daily Summary**: checks run, failures, uptime %, average and slowest response over the last 24 h.

## Tested
- Healthy run in n8n: 200 went to "Healthy - No Alert", nothing was posted.
- Down run: with the Task 1 API stopped, the three attempts failed (recorded 6,034 ms, i.e. two 3 s waits) and Discord accepted the alert (`success: true`) reading "APP DOWN: No response: connect ECONNREFUSED ...". The API was then restarted.
- The Code nodes were also simulated in plain Node for 200, HTTP 500 and connection-refused inputs.

## Not tested / limits
- The daily summary was only simulated in Node. n8n keeps static data only for production (published) runs, not manual test runs, so the summary has real data only after the workflow is published and has been running.
- The 5-minute and 9am schedules only fire once the workflow is published; it is saved but not published.
- An alert is sent on every failing check (5-minute repeats while the app is down) rather than only on state change. This follows the brief literally and is easy to change.
- The target URL assumes n8n runs on the same machine as the app (`localhost`). If n8n runs in Docker, use `host.docker.internal` instead.
