import json

TOP5 = """const res = $input.first().json;
const repos = Array.isArray(res.items) ? res.items : [];
if (repos.length === 0) {
  throw new Error('GitHub search returned no repositories');
}
return repos
  .filter(r => !r.archived)
  .sort((a, b) => b.stargazers_count - a.stargazers_count)
  .slice(0, 5)
  .map(r => ({
    json: {
      name: r.full_name,
      stars: r.stargazers_count,
      url: r.html_url,
      description: r.description || '',
      language: r.language || 'n/a'
    }
  }));"""

DIGEST = """const repos = $('Top 5 Repos').all();
const enriched = $input.all();
let readmeFailures = 0;
const lines = repos.map((r, i) => {
  const e = (enriched[i] && enriched[i].json) || {};
  const raw = typeof e.readme === 'string' ? e.readme : '';
  if (!raw) readmeFailures += 1;
  const snippet = raw
    ? raw.replace(/!\\[[^\\]]*\\]\\([^)]*\\)/g, ' ').replace(/<[^>]*>?/g, ' ').replace(/\\[([^\\]]*)\\]\\([^)]*\\)/g, '$1').replace(/[#>*`\\[\\]]/g, '').replace(/\\s+/g, ' ').trim().slice(0, 120) || 'README has no plain text'
    : 'README unavailable';
  return (i + 1) + '. ' + r.json.name + ' (' + r.json.stars + ' stars, ' + r.json.language + ')\\n' + r.json.url + '\\n> ' + snippet;
});
const topStars = repos[0].json.stars;
const body = lines.join('\\n\\n');
const note = readmeFailures ? '\\n\\n(' + readmeFailures + ' README lookup(s) failed)' : '';
return [{
  json: {
    topStars,
    readmeFailures,
    hotMessage: ('HOT morning brief - top n8n repo has ' + topStars + ' stars\\n\\n' + body + note).slice(0, 1900),
    quietMessage: ('Quiet morning brief - nothing above 1000 stars today\\n\\n' + body + note).slice(0, 1900)
  }
}];"""

ERR = """const j = $input.first().json;
const msg = (j.error && (j.error.message || j.error)) || j.message || JSON.stringify(j);
return [{
  json: {
    content: 'Morning brief FAILED at ' + new Date().toISOString() + '\\nReason: ' + String(msg).slice(0, 500) + '\\nNo digest was sent; check the n8n execution log.'
  }
}];"""

GH_HEADERS = {"parameters": [
    {"name": "Accept", "value": "application/vnd.github+json"},
    {"name": "User-Agent", "value": "n8n-morning-brief"},
]}


def discord(name, expr, pos):
    return {
        "parameters": {"authentication": "webhook", "content": expr, "options": {}},
        "id": name.lower().replace(" ", "-"),
        "name": name,
        "type": "n8n-nodes-base.discord",
        "typeVersion": 2,
        "position": pos,
        "onError": "continueRegularOutput",
        "credentials": {"discordWebhookApi": {"id": "REPLACE_ME", "name": "Discord Webhook (morning brief)"}},
    }


nodes = [
    {
        "parameters": {"rule": {"interval": [{"field": "hours", "hoursInterval": 1}]}},
        "id": "schedule", "name": "Every Hour (test)",
        "type": "n8n-nodes-base.scheduleTrigger", "typeVersion": 1.2, "position": [0, 200],
    },
    {
        "parameters": {
            "url": "https://api.github.com/search/repositories",
            "sendQuery": True,
            "queryParameters": {"parameters": [
                {"name": "q", "value": "topic:n8n"},
                {"name": "sort", "value": "stars"},
                {"name": "order", "value": "desc"},
                {"name": "per_page", "value": "20"},
            ]},
            "sendHeaders": True, "headerParameters": GH_HEADERS,
            "options": {"timeout": 15000},
        },
        "id": "search", "name": "GitHub Search",
        "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [220, 200],
        "onError": "continueErrorOutput",
        "retryOnFail": True, "maxTries": 2, "waitBetweenTries": 2000,
    },
    {
        "parameters": {"jsCode": TOP5},
        "id": "top5", "name": "Top 5 Repos",
        "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [440, 120],
        "onError": "continueErrorOutput",
    },
    {
        "parameters": {
            "url": "=https://api.github.com/repos/{{ $json.name }}/readme",
            "sendHeaders": True,
            "headerParameters": {"parameters": [
                {"name": "Accept", "value": "application/vnd.github.raw+json"},
                {"name": "User-Agent", "value": "n8n-morning-brief"},
            ]},
            "options": {"timeout": 15000, "response": {"response": {"responseFormat": "text", "outputPropertyName": "readme"}}},
        },
        "id": "readme", "name": "Fetch README",
        "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [660, 120],
        "onError": "continueRegularOutput",
    },
    {
        "parameters": {"jsCode": DIGEST},
        "id": "digest", "name": "Build Digest",
        "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [880, 120],
    },
    {
        "parameters": {"conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
            "conditions": [{
                "id": "stars-gt-1000", "leftValue": "={{ $json.topStars }}", "rightValue": 1000,
                "operator": {"type": "number", "operation": "gt"},
            }],
            "combinator": "and",
        }, "options": {}},
        "id": "if", "name": "Top Repo Over 1000 Stars?",
        "type": "n8n-nodes-base.if", "typeVersion": 2.2, "position": [1100, 120],
    },
    discord("Send Hot Digest", "={{ $json.hotMessage }}", [1320, 40]),
    discord("Send Quiet Digest", "={{ $json.quietMessage }}", [1320, 220]),
    {
        "parameters": {"jsCode": ERR},
        "id": "fmterr", "name": "Format Error",
        "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [660, 380],
    },
    discord("Send Failure Alert", "={{ $json.content }}", [880, 380]),
]

conn = {
    "Every Hour (test)": {"main": [[{"node": "GitHub Search", "type": "main", "index": 0}]]},
    "GitHub Search": {"main": [
        [{"node": "Top 5 Repos", "type": "main", "index": 0}],
        [{"node": "Format Error", "type": "main", "index": 0}],
    ]},
    "Top 5 Repos": {"main": [
        [{"node": "Fetch README", "type": "main", "index": 0}],
        [{"node": "Format Error", "type": "main", "index": 0}],
    ]},
    "Fetch README": {"main": [[{"node": "Build Digest", "type": "main", "index": 0}]]},
    "Build Digest": {"main": [[{"node": "Top Repo Over 1000 Stars?", "type": "main", "index": 0}]]},
    "Top Repo Over 1000 Stars?": {"main": [
        [{"node": "Send Hot Digest", "type": "main", "index": 0}],
        [{"node": "Send Quiet Digest", "type": "main", "index": 0}],
    ]},
    "Format Error": {"main": [[{"node": "Send Failure Alert", "type": "main", "index": 0}]]},
}

wf = {
    "name": "Morning Brief - GitHub n8n Digest",
    "nodes": nodes,
    "connections": conn,
    "active": False,
    "settings": {"executionOrder": "v1"},
    "pinData": {},
}

with open("Task2_Workflow_NayanaviramPanigrahi.json", "w", encoding="utf-8") as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)
print("ok", len(nodes), "nodes")
