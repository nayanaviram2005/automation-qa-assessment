# Automation & QA Developer Assessment - Nayanaviram Panigrahi

Take-home assessment: QA report on a web app, an n8n API workflow, and an uptime-monitor bonus.

| Part | Folder | Main file |
|---|---|---|
| Task 1: QA and debug report | `task1/` | `Task1_QA_Report_NayanaviramPanigrahi.pdf` |
| Task 2: n8n morning-brief workflow | `task2/` | `Task2_Workflow_NayanaviramPanigrahi.json`, `README_Task2.md` |
| Bonus: uptime monitor | `bonus/` | `Bonus_UptimeMonitor_NayanaviramPanigrahi.json`, `README_Bonus.md` |
| Walkthrough video | `video/` | `out/walkthrough.mp4` (screen recording of the live demo with on-screen captions, no voice-over) |

## Task 1 - QA report
The public RealWorld demo (`demo.realworld.io`) was down (404), so I ran the Express + Prisma + PostgreSQL implementation, [gothinkster/node-express-realworld-example-app](https://github.com/gothinkster/node-express-realworld-example-app), locally with Postgres 15 in Docker. That clone is not included here. The repo has no frontend, so I tested through the HTTP API with curl and by reading the source.

Found 10 issues (1 Critical, 3 High, 4 Medium, 2 Low). The root-cause analysis covers the Critical one: the article list only returns articles whose author has `demo = true` or is the logged-in user, so visitors see an empty feed. Other findings include non-Latin titles getting identical slugs, a 500 with a raw database error when changing email to a taken one, and no input validation at registration. Not tested: a successful owner delete and comment post, and anything in a browser.

## Task 2 - n8n workflow
Hourly schedule, GitHub Search API for top `n8n` repos, Code node keeps the top 5, a second GitHub call fetches each README, an IF node on "top repo over 1000 stars" picks a hot or quiet digest, and Discord receives it. Failed search or transform steps go to a failure alert; a missing README does not stop the run. The Discord webhook sits in n8n's credential store, not in the file. Run end to end in n8n 2.22.6 and the failure path was tested with a deliberately broken URL; screenshots are in `task2/`. The quiet branch was not run.

## Bonus - uptime monitor
Pings the Task 1 app every 5 minutes with 3 retries, records response time, alerts Discord on anything but 200, and has a daily summary. Tested healthy and with the app stopped. The daily summary was only simulated, because n8n keeps run history for published workflows only.

## Using the workflows
Import the JSON through Workflows > Import from File, then select your own Discord Webhook credential on each Discord node (the files contain the placeholder id `REPLACE_ME`). The workflows are saved, not published.

## Rebuilding
`build_report.py`, `build_workflow.py` and `build_monitor.py` regenerate the report and the two workflow files. The video is a Remotion project: in `video/`, run `npm install` then `npm run render`. It overlays captions on `video/public/walkthrough.mp4`, a 1600x900 recording of a real click-through (the API bug pages, the live n8n run, the saved error run and the monitor runs). The recording script is not included.
