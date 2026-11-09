export const FPS = 30;
export const INTRO_SECONDS = 4;
export const OUTRO_SECONDS = 8;
export const SOURCE_SECONDS = 121.2667;

export const cuts = [
  [64.2, 69.4],
  [85.7, 90.0],
  [100.2, 104.5],
];

export const keeps = (() => {
  const out = [];
  let from = 0;
  cuts.forEach(([a, b]) => {
    out.push([from, a]);
    from = b;
  });
  out.push([from, SOURCE_SECONDS]);
  return out;
})();


export const segments = (() => {
  let offset = 0;
  return keeps.map(([from, to]) => {
    const frames = Math.round((to - from) * FPS);
    const seg = {from, startFrom: Math.round(from * FPS), frames, offset};
    offset += frames;
    return seg;
  });
})();

export const VIDEO_FRAMES = segments.reduce((sum, seg) => sum + seg.frames, 0);

export const toComp = (t) => {
  let removed = 0;
  cuts.forEach(([a, b]) => {
    if (t >= b) removed += b - a;
  });
  return t - removed;
};

const sourceOverlays = [
  {
    start: 0.6,
    end: 5.2,
    box: {left: 60, top: 290, width: 1000},
    text: 'Task 1 bug: with no login, the article list is empty, even though articles exist in the database.',
  },
  {
    start: 6.1,
    end: 10.8,
    box: {left: 60, top: 330, width: 1100},
    text: 'A negative offset returns a 500 and leaks the raw database error, including a path on the server.',
  },
  {
    start: 11.7,
    end: 16.9,
    box: {left: 900, top: 400, width: 620},
    text: 'Root cause: the query only lets through authors with demo = true (highlighted), or the logged-in user.',
  },
  {
    start: 18.0,
    end: 28.4,
    box: {left: 240, top: 100, width: 1060},
    text: 'Task 2: an hourly trigger calls GitHub, keeps the top 5 repos, fetches each README, then branches on stars. Failures take the error output.',
  },
  {
    start: 29.6,
    end: 43.3,
    box: {left: 240, top: 100, width: 1060},
    text: 'Running it live: each node turns green in turn, from the trigger through to Discord.',
  },
  {
    start: 45.5,
    end: 49.4,
    box: {left: 500, top: 745, width: 600},
    text: 'Top 5 Repos (Code node): sorts by stars and keeps five, with name, stars and URL.',
  },
  {
    start: 52.0,
    end: 55.6,
    box: {left: 500, top: 750, width: 600},
    text: 'Build Digest: pairs each repo with a README snippet and builds the hot and quiet messages.',
  },
  {
    start: 59.0,
    end: 63.6,
    box: {left: 1040, top: 330, width: 500},
    text: 'Top repo is over 1000 stars, so the hot branch ran and Discord returned success: true.',
  },
  {
    start: 69.9,
    end: 75.0,
    box: {left: 540, top: 150, width: 900},
    text: 'Saved failed run: the search URL was broken on purpose, so GitHub returned 404. The error output went to Format Error, then the alert.',
  },
  {
    start: 80.0,
    end: 84.0,
    box: {left: 1040, top: 330, width: 500},
    text: 'The alert reached Discord (success: true) with the real reason: 404 Not Found.',
  },
  {
    start: 90.5,
    end: 99.0,
    box: {left: 540, top: 150, width: 840},
    text: 'Bonus, uptime monitor. Healthy check: status 200 goes to Healthy - No Alert, so nothing is posted.',
  },
  {
    start: 105.0,
    end: 112.5,
    box: {left: 540, top: 150, width: 840},
    text: 'With the Task 1 app stopped: three attempts fail, then the down branch sends the alert.',
  },
  {
    start: 114.8,
    end: 119.3,
    box: {left: 1040, top: 330, width: 500},
    text: 'Alert text: no response after 6,034 ms of retries (3 tries, 3 s apart). Discord returned success: true.',
  },
];

export const overlays = sourceOverlays.map((o) => ({...o, start: toComp(o.start), end: toComp(o.end)}));

export const intro = {
  title: 'Automation & QA Developer Assessment',
  lines: ['Nayanaviram Panigrahi', 'Task 1: QA and debug report', 'Task 2: n8n morning-brief workflow', 'Bonus: uptime monitor'],
};

export const outro = {
  title: 'What is not covered',
  lines: [
    'Daily summary of the uptime monitor was only simulated: n8n keeps run history for published workflows only',
    'The quiet branch of the IF in Task 2 was not run in n8n',
    'No browser UI testing: the Task 1 repo has no frontend',
    'Workflows are saved but not published, so their schedules are not active',
    'github.com/nayanaviram2005/automation-qa-assessment',
  ],
};

export const totalFrames = (INTRO_SECONDS + OUTRO_SECONDS) * FPS + VIDEO_FRAMES;
