import json
import sys

CRED_ID = sys.argv[1] if len(sys.argv) > 1 else "REPLACE_ME"
OUT = sys.argv[2] if len(sys.argv) > 2 else "Bonus_UptimeMonitor_NayanaviramPanigrahi.json"
TARGET = "http://localhost:3000/api/tags"

STAMP = "return [{ json: { t0: Date.now() } }];"

EVAL = """const t0 = $('Stamp Start').first().json.t0;
const ms = Date.now() - t0;
const j = $input.first().json;
const status = typeof j.statusCode === 'number' ? j.statusCode : 0;
const detail = (j.error && (j.error.message || j.error)) || 'no response';
const reason = status ? 'HTTP ' + status : 'No response: ' + String(detail).slice(0, 200);
const ok = status === 200;
const s = $getWorkflowStaticData('global');
s.checks = s.checks || [];
s.checks.push({ t: Date.now(), status, ms, ok });
s.checks = s.checks.slice(-600);
s.failStreak = ok ? 0 : (s.failStreak || 0) + 1;
const when = new Date().toISOString();
return [{
  json: {
    ok,
    status,
    ms,
    reason,
    failStreak: s.failStreak,
    checkedAt: when,
    message: ok ? '' : 'APP DOWN: ' + reason + ' after ' + ms + ' ms (failed check ' + s.failStreak + ' in a row)\\nURL: """ + TARGET + """\\nTime: ' + when
  }
}];"""

SUMMARY = """const s = $getWorkflowStaticData('global');
const since = Date.now() - 24 * 3600 * 1000;
const c = (s.checks || []).filter(x => x.t >= since);
if (c.length === 0) {
  return [{ json: { message: 'Daily uptime summary: no checks recorded in the last 24 hours.' } }];
}
const fails = c.filter(x => !x.ok).length;
const times = c.map(x => x.ms);
const avg = Math.round(times.reduce((a, b) => a + b, 0) / times.length);
const max = Math.max(...times);
const up = ((c.length - fails) / c.length * 100).toFixed(2);
return [{
  json: {
    message: 'Daily uptime summary (last 24h)\\nChecks: ' + c.length + '\\nFailed: ' + fails + '\\nUptime: ' + up + '%\\nAverage response: ' + avg + ' ms\\nSlowest response: ' + max + ' ms'
  }
}];"""


def discord(name, expr, pos):
    return {
        "parameters": {"authentication": "webhook", "content": expr, "options": {}},
        "id": name.lower().replace(" ", "-"),
        "name": name,
        "type": "n8n-nodes-base.discord",
        "typeVersion": 2,
        "position": pos,
        "onError": "continueRegularOutput",
        "credentials": {"discordWebhookApi": {"id": CRED_ID, "name": "Discord Webhook account"}},
    }


nodes = [
    {
        "parameters": {"rule": {"interval": [{"field": "minutes", "minutesInterval": 5}]}},
        "id": "every5", "name": "Every 5 Minutes",
        "type": "n8n-nodes-base.scheduleTrigger", "typeVersion": 1.2, "position": [0, 100],
    },
    {
        "parameters": {"jsCode": STAMP},
        "id": "stamp", "name": "Stamp Start",
        "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [220, 100],
    },
    {
        "parameters": {
            "url": TARGET,
            "options": {"timeout": 10000, "response": {"response": {"fullResponse": True, "neverError": True}}},
        },
        "id": "ping", "name": "Ping App",
        "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2, "position": [440, 100],
        "onError": "continueRegularOutput",
        "retryOnFail": True, "maxTries": 3, "waitBetweenTries": 3000,
    },
    {
        "parameters": {"jsCode": EVAL},
        "id": "eval", "name": "Evaluate Check",
        "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [660, 100],
    },
    {
        "parameters": {"conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
            "conditions": [{
                "id": "ok-true", "leftValue": "={{ $json.ok }}", "rightValue": "",
                "operator": {"type": "boolean", "operation": "true", "singleValue": True},
            }],
            "combinator": "and",
        }, "options": {}},
        "id": "healthy", "name": "Status Is 200?",
        "type": "n8n-nodes-base.if", "typeVersion": 2.2, "position": [880, 100],
    },
    {
        "parameters": {},
        "id": "noop", "name": "Healthy - No Alert",
        "type": "n8n-nodes-base.noOp", "typeVersion": 1, "position": [1100, 20],
    },
    discord("Send Down Alert", "={{ $json.message }}", [1100, 200]),
    {
        "parameters": {"rule": {"interval": [{"field": "cronExpression", "expression": "0 9 * * *"}]}},
        "id": "daily", "name": "Daily 9am Summary",
        "type": "n8n-nodes-base.scheduleTrigger", "typeVersion": 1.2, "position": [0, 380],
    },
    {
        "parameters": {"jsCode": SUMMARY},
        "id": "summary", "name": "Build Summary",
        "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [220, 380],
    },
    discord("Send Daily Summary", "={{ $json.message }}", [440, 380]),
]

conn = {
    "Every 5 Minutes": {"main": [[{"node": "Stamp Start", "type": "main", "index": 0}]]},
    "Stamp Start": {"main": [[{"node": "Ping App", "type": "main", "index": 0}]]},
    "Ping App": {"main": [[{"node": "Evaluate Check", "type": "main", "index": 0}]]},
    "Evaluate Check": {"main": [[{"node": "Status Is 200?", "type": "main", "index": 0}]]},
    "Status Is 200?": {"main": [
        [{"node": "Healthy - No Alert", "type": "main", "index": 0}],
        [{"node": "Send Down Alert", "type": "main", "index": 0}],
    ]},
    "Daily 9am Summary": {"main": [[{"node": "Build Summary", "type": "main", "index": 0}]]},
    "Build Summary": {"main": [[{"node": "Send Daily Summary", "type": "main", "index": 0}]]},
}

wf = {
    "name": "Uptime Monitor - Conduit API",
    "nodes": nodes,
    "connections": conn,
    "active": False,
    "settings": {"executionOrder": "v1"},
    "pinData": {},
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)
print("wrote", OUT, len(nodes), "nodes")
