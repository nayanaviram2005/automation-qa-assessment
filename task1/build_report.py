from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

OUT = "Task1_QA_Report_NayanaviramPanigrahi.pdf"

ss = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=18, spaceAfter=4)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=13, spaceBefore=10, spaceAfter=4)
body = ParagraphStyle("body", parent=ss["BodyText"], fontSize=9.5, leading=13)
cell = ParagraphStyle("cell", parent=ss["BodyText"], fontSize=7.8, leading=9.8)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
code = ParagraphStyle("code", parent=cell, fontName="Courier", fontSize=7.4, leading=9.2)

SEV = {"Critical": "#b3261e", "High": "#c75a00", "Medium": "#8a6d00", "Low": "#3a5f3a"}


def P(t, s=cell):
    return Paragraph(t, s)


def sev(s):
    return Paragraph('<font color="%s"><b>%s</b></font>' % (SEV[s], s), cell)


rows = [
    ("1", "Global article feed is empty for visitors; logged-in users see only their own articles",
     "1. Register two users and create an article as each.<br/>2. <font face='Courier'>GET /api/articles</font> with no token.<br/>3. Repeat with user A's token.",
     "<b>Expected:</b> every published article appears in the global feed for everyone.<br/><b>Actual:</b> anonymous call returns <font face='Courier'>{\"articles\":[],\"articlesCount\":0}</font>. User A sees only A's articles. <font face='Courier'>GET /api/tags</font> is also empty.",
     "Critical",
     "Query in <font face='Courier'>article.service.ts</font> (buildFindAllQuery) restricts authors to <font face='Courier'>demo = true</font> OR the caller's own id. Same <font face='Courier'>demo: true</font> filter in <font face='Courier'>tag.service.ts</font>."),
    ("2", "Titles in non-Latin scripts (e.g. Hindi) all get the same slug; the second one is rejected as \"must be unique\"",
     "1. As one user, POST an article titled \"मेरा पहला लेख\".<br/>2. POST a different article titled \"दूसरा बिलकुल अलग लेख\".",
     "<b>Expected:</b> both save with distinct URLs.<br/><b>Actual:</b> first gets slug <font face='Courier'>-2</font>; second returns 422 <font face='Courier'>title: must be unique</font>. Symbol-only titles behave the same (<font face='Courier'>!!-2</font>).",
     "High",
     "Slug is <font face='Courier'>slugify(title) + '-' + userId</font>. slugify drops non-Latin characters, leaving an empty string. The suffix is the user id, not the article id, so it cannot disambiguate."),
    ("3", "Changing email or username to one already taken returns HTTP 500 with a raw database error and a server file path",
     "1. Register users A and B.<br/>2. As A, <font face='Courier'>PUT /api/user</font> with B's email.",
     "<b>Expected:</b> 422 <font face='Courier'>email: has already been taken</font>, as registration does.<br/><b>Actual:</b> 500 whose body is the Prisma error text, including <font face='Courier'>C:\\...\\auth.service.ts:159</font> and the failed constraint.",
     "High",
     "<font face='Courier'>updateUser</font> has no uniqueness check (unlike <font face='Courier'>createUser</font>). The global error handler returns <font face='Courier'>err.message</font> for any unknown error, leaking internals."),
    ("4", "Registration accepts an invalid email, a 1-character username and a 1-character password",
     "1. <font face='Courier'>POST /api/users</font> with email \"not-an-email\", username \"a\", password \"1\".",
     "<b>Expected:</b> 422 with field errors.<br/><b>Actual:</b> 201 Created and a valid token.",
     "High",
     "<font face='Courier'>createUser</font> only checks the fields are non-empty. No format or length rules."),
    ("5", "Invalid pagination values give wrong results or a 500",
     "1. As a user with 3 articles: <font face='Courier'>GET /api/articles?limit=-1</font>.<br/>2. <font face='Courier'>GET /api/articles?offset=-1</font>.",
     "<b>Expected:</b> 422 or a clamped default.<br/><b>Actual:</b> limit=-1 returns 1 article (the oldest) while <font face='Courier'>articlesCount</font> says 3. offset=-1 returns 500 with the Prisma invocation text.",
     "Medium",
     "<font face='Courier'>Number(query.limit) || 10</font> passes negatives straight to Prisma (<font face='Courier'>take</font> &lt; 0 reads backwards; negative <font face='Courier'>skip</font> throws)."),
    ("6", "Malformed or oversized JSON bodies return 500 instead of 400/413",
     "1. <font face='Courier'>POST /api/users</font> with body <font face='Courier'>{\"user\":</font>.<br/>2. POST an article with a 200 KB body.",
     "<b>Expected:</b> 400 for bad JSON, 413 for too large.<br/><b>Actual:</b> both return 500 with the parser's message as the body.",
     "Medium",
     "<font face='Courier'>body-parser</font> errors carry a status but the error handler in <font face='Courier'>main.ts</font> ignores it and falls to the generic 500 branch. Default 100 KB limit is also not documented."),
    ("7", "Wrong login status code and no brute-force protection",
     "1. <font face='Courier'>POST /api/users/login</font> with a wrong password 30 times in a row.",
     "<b>Expected:</b> 401 (or 422) and throttling or lock-out after repeated failures.<br/><b>Actual:</b> every attempt returns 403 immediately; none were slowed or blocked.",
     "Medium",
     "403 is hard-coded in <font face='Courier'>login</font>. No rate limiter middleware is installed."),
    ("8", "Editing an article title silently changes its URL; the old link returns 404",
     "1. Create \"Hello\" (slug Hello-2).<br/>2. <font face='Courier'>PUT</font> a new title.<br/>3. Open the old slug.",
     "<b>Expected:</b> the existing link keeps working.<br/><b>Actual:</b> slug becomes <font face='Courier'>Hello-renamed-2</font>; <font face='Courier'>GET /api/articles/Hello-2</font> returns 404.",
     "Medium",
     "<font face='Courier'>updateArticle</font> recomputes the slug from the title and keeps no redirect or stable id."),
    ("9", "HTML in title and body is stored and returned unescaped",
     "1. POST an article with title <font face='Courier'>&lt;script&gt;alert(1)&lt;/script&gt;</font> and body <font face='Courier'>&lt;img src=x onerror=alert(1)&gt;</font>.",
     "<b>Expected:</b> content is rejected or sanitised, or the client escapes on render.<br/><b>Actual:</b> stored as typed (201). Safe only if every client escapes it. Not tested in a browser because this repo has no frontend.",
     "Low",
     "No server-side sanitisation. Risk depends on whichever frontend renders the data."),
    ("10", "A user can follow themselves; tokens last 60 days with no server-side revoke",
     "1. <font face='Courier'>POST /api/profiles/alice/follow</font> as alice.<br/>2. Decode the JWT: exp minus iat is 5,184,000 s.",
     "<b>Expected:</b> self-follow refused; a way to end a session.<br/><b>Actual:</b> self-follow returns 200 and following: true. No logout or revoke endpoint exists.",
     "Low",
     "No self-check in the follow handler. Stateless JWT with a long expiry and no deny-list."),
]

doc = SimpleDocTemplate(OUT, pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm,
                        topMargin=12 * mm, bottomMargin=12 * mm,
                        title="Task 1 - QA and Debug Report", author="Nayanaviram Panigrahi")
st = []
st.append(Paragraph("Task 1 &mdash; Web App QA &amp; Debug Report", h1))
st.append(Paragraph(
    "<b>Prepared by:</b> Nayanaviram Panigrahi<br/>"
    "<b>App tested:</b> RealWorld &ldquo;Conduit&rdquo; API, <font face='Courier'>gothinkster/node-express-realworld-example-app</font> "
    "(Express + Prisma + PostgreSQL 15), run locally on port 3000.<br/>"
    "<b>Why not the live demo:</b> <font face='Courier'>demo.realworld.io</font> returned 404 and its API returned Cloudflare error 1016 on the day of testing.<br/>"
    "<b>Scope and limits:</b> this repo is backend only, so the flows were exercised through the HTTP API with curl and by reading the source: "
    "sign-up, login, profile update, article create and edit, follow, comment validation, and edit/delete attempts by a non-owner. "
    "A successful owner delete and a successful comment post were not run. No browser UI, accessibility or visual "
    "checks were possible. There is no logout endpoint, because auth is a stateless JWT.<br/>"
    "<b>Result:</b> 10 issues found (1 Critical, 3 High, 4 Medium, 2 Low). Each was reproduced against the running server; the "
    "suspected cause comes from reading the source.", body))
st.append(Paragraph("Bug table", h2))

head = [P(x, cellb) for x in ("#", "Title / Summary", "Steps to Reproduce", "Expected vs Actual", "Severity", "Suspected Cause")]
data = [head]
for r in rows:
    data.append([P(r[0]), P("<b>%s</b>" % r[1]), P(r[2]), P(r[3]), sev(r[4]), P(r[5])])
t = Table(data, colWidths=[8 * mm, 46 * mm, 62 * mm, 72 * mm, 15 * mm, 62 * mm], repeatRows=1)
t.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6e6e6")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
st.append(t)

st.append(PageBreak())
st.append(Paragraph("Root-cause analysis &mdash; Issue 1: global feed shows no articles", h2))
rca = (
    "Anonymous visitors get an empty article list, and a logged-in user sees only articles they wrote themselves, even though "
    "the database holds articles from several users. The cause is in <font face='Courier'>buildFindAllQuery</font> in "
    "<font face='Courier'>article.service.ts</font>. It always adds a condition that the article's author must have "
    "<font face='Courier'>demo = true</font>, or must be the logged-in user. Users created through the normal "
    "<font face='Courier'>POST /api/users</font> route have <font face='Courier'>demo = false</font> by default, so the first "
    "condition never matches them. The tag list in <font face='Courier'>tag.service.ts</font> has the same "
    "<font face='Courier'>demo: true</font> filter, which is why <font face='Courier'>/api/tags</font> was also empty after I "
    "created an article with a tag. This looks like a guard meant for a public showcase site, where only seeded demo content "
    "should be shown, and it was left on for every deployment. For a real product it makes the main page look broken: new users "
    "sign up and see nothing. I would fix it by removing the author filter from the default query and keeping only the optional "
    "<font face='Courier'>author</font>, <font face='Courier'>tag</font> and <font face='Courier'>favorited</font> filters. If the "
    "demo behaviour is still wanted, it should sit behind an environment flag such as <font face='Courier'>DEMO_MODE=true</font>. "
    "I would add an integration test that creates two non-demo users and asserts both articles appear in an anonymous "
    "<font face='Courier'>GET /api/articles</font>.")
st.append(Paragraph(rca, body))

st.append(Paragraph("Observations that were not bugs", h2))
st.append(Paragraph(
    "Authorisation held up: another user's edit and delete both returned 403 and the article was unchanged; missing or invalid "
    "tokens returned 401; blank article and comment fields returned 422; an unknown slug returned 404. The "
    "<font face='Courier'>Bearer</font> scheme is accepted as well as <font face='Courier'>Token</font>, which is harmless.", body))

st.append(Paragraph("Environment", h2))
st.append(Paragraph(
    "Windows 11, Node 22.17, PostgreSQL 15 in Docker (host port 5433), Prisma 4.16 migrations applied with "
    "<font face='Courier'>prisma migrate deploy</font>, server started with <font face='Courier'>npx nx serve api</font>. "
    "Test accounts were throw-away values created for this run.", body))
doc.build(st)
print("built", OUT)
