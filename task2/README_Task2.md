# Task 2 - Morning Brief workflow (n8n)

Every hour the workflow finds the five most-starred GitHub repositories for the topic `n8n`, reads each one's README, and posts a digest to Discord.

## Files
- `Task2_Workflow_NayanaviramPanigrahi.json` - import via n8n: Workflows > Import from File.
- `build_workflow.py` - generator for the JSON, kept so the workflow can be rebuilt.

## APIs used and why
- **GitHub Search API** (`GET /search/repositories?q=topic:n8n&sort=stars`). Free, needs no key for one call an hour, and returns stars, so a threshold is natural.
- **GitHub Repository README endpoint** (`GET /repos/{owner}/{repo}/readme`, `Accept: application/vnd.github.raw+json`). A second endpoint of the same API, used to enrich each of the five repos with a short description from its README.
- **Discord webhook** for output, through n8n's Discord node.

## What the flow does
1. **Every Hour (test)**: Schedule trigger.
2. **GitHub Search**: fetches 20 repos sorted by stars.
3. **Top 5 Repos** (Code): drops archived repos, sorts by stars, keeps the top 5, and keeps only name, stars, URL, language and description. Throws if the search returned nothing.
4. **Fetch README**: one call per repo, response read as text.
5. **Build Digest** (Code): pairs each repo with its README, strips HTML, images and markdown, keeps the first 120 characters, and builds two message variants under Discord's 2000-character limit.
6. **Top Repo Over 1000 Stars?** (IF): true sends the "HOT" digest, false sends the "Quiet" digest. 1000 is a placeholder threshold that the real data passes easily; change it in the IF node to see the other branch.

## Error path
- **GitHub Search** and **Top 5 Repos** use *On Error: continue (using error output)*. A failed or empty search goes to **Format Error**, which builds a message with the time and reason, then **Send Failure Alert** posts it to the same Discord channel. The run ends visibly instead of silently.
- **Fetch README** uses *continue (regular output)*. A missing README does not stop the run; that repo shows "README unavailable" and the digest notes how many lookups failed.
- GitHub Search also retries once after 2 seconds.
- The three Discord nodes use *continue (regular output)*, so a failed send leaves its error in the execution data. A failed send cannot be reported to Discord itself, so check the execution list.

## Credentials
No secrets are in the JSON. The Discord webhook URL lives in an n8n credential of type "Discord Webhook"; after import, open each Discord node and select your own credential (the file holds the placeholder id `REPLACE_ME`). GitHub is called without a token; at one run an hour it stays far under the 60 requests/hour unauthenticated limit.

## Tested
Run end to end in a local n8n (2.22.6): search returned results, 5 repos were kept, 5 READMEs were fetched, the IF took the "true" branch (top repo 209,915 stars) and Send Hot Digest returned `success: true` to Discord. Screenshots: `Task2_Screenshot_A_Canvas.jpg` and `Task2_Screenshot_B_Execution.jpg`. The Code nodes were also run in plain Node against live GitHub data with a simulated README failure. Failure path: with the search URL deliberately broken (404), the error output routed to Format Error and Send Failure Alert, which posted to Discord with the 404 reason (`Task2_ErrorPath_Canvas.jpg`, `Task2_ErrorPath_Alert.jpg`); the URL was then restored and a normal run passed again. Not yet exercised inside n8n: the "false" (quiet) branch of the IF.
