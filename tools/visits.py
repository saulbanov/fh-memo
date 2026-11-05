"""Who opened which tracked link: GoatCounter visit counts per funder code, joined to the private key.

Reads visit counts from the GoatCounter API (account `futureheist`), matches each counted path's `?r=<code>` to the
master key that tools/mint_links.py writes, and prints one row per recipient: send, name, visits, days seen. Paths with
a code that is in no key file print at the end as unmatched (a forward with an edited link, or a test like ?r=test).

Setup, once: in GoatCounter, open the account menu > API, create a key with "Read statistics" checked, then put it in
~/.zshenv as  export GOATCOUNTER_TOKEN=<key>  and open a new terminal.

python3 -I tools/visits.py [--send <send-name>] [--since YYYY-MM-DD]

A visit means someone opened that funder's link: a forward counts under the original code, and some mail systems'
link scanners open links before a person does. No visit is not "didn't read": the memo is also inline in the email.
"""
import argparse, csv, json, os, re, sys, urllib.parse, urllib.request
from collections import defaultdict

SITE = 'https://futureheist.goatcounter.com'
MASTER = os.environ.get('FH_MEMO_KEYS', os.path.expanduser('~/Documents/Claude Code/future-heist/fhwr-runway/memo-links-master.csv'))


def api(path, token, **q):
    url = f'{SITE}/api/v0/{path}?' + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})
    try:
        return json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        sys.exit(f'GoatCounter API {e.code} on {path}: {e.read().decode()[:300]}')


def hits(token, since):
    """Every counted path since `since`, with its total and the days it was seen (pages through `more`)."""
    out, after = [], None
    while True:
        q = {'start': f'{since}T00:00:00Z', 'limit': 100}
        if after: q['exclude_paths'] = after
        r = api('stats/hits', token, **q)
        out += r.get('hits', [])
        if not r.get('more'): return out
        after = ','.join(str(h['path_id']) for h in out)


def main():
    a = argparse.ArgumentParser(); a.add_argument('--send'); a.add_argument('--since')
    x = a.parse_args()
    token = os.environ.get('GOATCOUNTER_TOKEN')
    if not token: sys.exit('GOATCOUNTER_TOKEN is not set; see the setup note at the top of this file')
    keys = [r for r in csv.DictReader(open(MASTER, encoding='utf-8')) if not x.send or r['send'] == x.send]
    if not keys: sys.exit(f'no rows in {MASTER}' + (f' for send "{x.send}"' if x.send else ''))
    since = x.since or min(r['minted'] for r in keys)
    by_code = {r['code']: r for r in keys}

    seen, days, unmatched = defaultdict(int), defaultdict(set), []
    for h in hits(token, since):
        m = re.search(r'[?&]r=([0-9a-z]+)', h.get('path', ''))
        if not m: continue
        code = m.group(1)
        if code not in by_code: unmatched.append((h['path'], h.get('count', 0))); continue
        seen[code] += h.get('count', 0)
        for s in h.get('stats', []):
            if s.get('daily'): days[code].add(s['day'])

    rows = sorted(keys, key=lambda r: (-seen[r['code']], r['send'], int(r['n'])))
    w = max(len(r['name']) for r in rows)
    print(f'GoatCounter visits since {since}, {len(rows)} recipients' + (f' in "{x.send}"' if x.send else ''))
    for r in rows:
        d = sorted(days[r['code']])
        print(f"  {r['name']:<{w}}  {seen[r['code']]:>3} visits  {(d[0] + ' to ' + d[-1]) if d else '':<24}  {r['send']}  ?r={r['code']}")
    opened = sum(1 for r in rows if seen[r['code']])
    print(f'{opened} of {len(rows)} links opened at least once')
    if unmatched:
        print('Paths with a code in no key file:')
        for p, n in unmatched: print(f'  {p}  {n}')


if __name__ == '__main__':
    main()
