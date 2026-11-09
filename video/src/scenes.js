export const FPS = 30;

export const scenes = [
  {
    seconds: 5,
    title: 'Automation & QA Developer Assessment',
    bullets: [
      'Nayanaviram Panigrahi',
      'Task 1: QA and debug report',
      'Task 2: n8n morning-brief workflow',
      'Bonus: uptime monitor',
    ],
    images: [],
  },
  {
    seconds: 8,
    title: 'Task 1: what I tested',
    bullets: [
      'App: RealWorld Conduit API (Express, Prisma, PostgreSQL), run locally',
      'The public demo is down (404), so I ran it myself',
      'Backend only, so I tested through the API with curl and read the source',
      '10 issues found: 1 Critical, 3 High, 4 Medium, 2 Low',
      'Authorization held up: other users got 403 on edit and delete',
    ],
    images: [],
  },
  {
    seconds: 9,
    title: 'Task 1: the main bug',
    bullets: [
      'Global feed is empty for visitors; users see only their own articles',
      'Cause: the list query only allows authors with demo = true, or yourself',
      'Fix: remove the demo filter, or put it behind a DEMO_MODE flag',
      'Also found: non-Latin titles all get the same slug',
      'Also found: changing email to a taken one returns 500 with a raw database error',
    ],
    images: [],
  },
  {
    seconds: 8,
    title: 'Task 2: the workflow',
    bullets: [
      'Hourly trigger, then GitHub search for the top n8n repos',
      'Code node keeps the top 5, then one README call per repo',
      'IF node: top repo over 1000 stars sends the hot digest, else the quiet one',
      'Output goes to Discord through a stored credential, no secrets in the file',
    ],
    images: ['Task2_Screenshot_A_Canvas.jpg'],
  },
  {
    seconds: 6,
    title: 'Task 2: a successful run',
    bullets: [
      'Real run in n8n: 5 repos, 5 READMEs, hot branch taken (top repo 209,915 stars)',
      'Discord node returned success: true',
    ],
    images: ['Task2_Screenshot_B_Execution.jpg'],
  },
  {
    seconds: 9,
    title: 'Task 2: error handling',
    bullets: [
      'I broke the search URL on purpose to get a 404',
      'The error output routed to Format Error, then a Discord failure alert',
      'The alert carried the real reason, and the happy path stayed idle',
      'A missing README does not stop the run; that repo shows README unavailable',
    ],
    images: ['Task2_ErrorPath_Canvas.jpg', 'Task2_ErrorPath_Alert.jpg'],
  },
  {
    seconds: 9,
    title: 'Bonus: uptime monitor',
    bullets: [
      'Pings the Task 1 app every 5 minutes, alerts if the status is not 200',
      'Retries 3 times, 3 seconds apart, and records response time',
      'Stopped the app to test: alert sent after about 6 seconds of retries',
      'Daily 9am summary: uptime, average and slowest response',
    ],
    images: ['Bonus_Screenshot_Workflow.jpg', 'Bonus_Screenshot_DownAlert.jpg'],
  },
  {
    seconds: 7,
    title: 'What is not covered',
    bullets: [
      'Daily summary only simulated: n8n keeps history for published runs only',
      'Quiet branch of the IF was not run in n8n',
      'No browser UI testing: the Task 1 repo has no frontend',
      'Workflows are saved but not published, so schedules are not active',
    ],
    images: [],
  },
];

export const totalFrames = scenes.reduce((sum, s) => sum + s.seconds * FPS, 0);
