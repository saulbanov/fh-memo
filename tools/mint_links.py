"""Mint one tracked link per recipient for one send of one document.

Every recipient of every send gets a fresh random code, so a code names one person in one send. The key
(code -> person, send, document) is private: it is written OUTSIDE this public repo, to the send's own key file
and appended to the master key. Never commit a key file here.

python3 -I tools/mint_links.py --send <send-name> --doc <doc-slug> --recipients <recipients.json> --out <key.csv>

recipients.json is a list of objects with at least "name" and "to". The master key defaults to
$FH_MEMO_KEYS, else ~/Documents/Claude Code/future-heist/fhwr-runway/memo-links-master.csv.
"""
import argparse, csv, json, os, secrets, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://saulbanov.github.io/fh-memo'
MASTER = os.environ.get('FH_MEMO_KEYS', os.path.expanduser('~/Documents/Claude Code/future-heist/fhwr-runway/memo-links-master.csv'))
COLS = ['minted', 'send', 'doc', 'n', 'name', 'to', 'code', 'link']


def main():
    a = argparse.ArgumentParser(); a.add_argument('--send', required=True); a.add_argument('--doc', required=True)
    a.add_argument('--recipients', required=True); a.add_argument('--out', required=True)
    a.add_argument('--codes', help='reuse codes from an existing key csv (columns to, code) instead of minting')
    x = a.parse_args()
    if not os.path.exists(os.path.join(ROOT, x.doc, 'index.html')):
        sys.exit(f'no {x.doc}/index.html in this repo; publish the document first (tools/publish_doc.py)')
    if os.path.abspath(x.out).startswith(ROOT) or os.path.abspath(MASTER).startswith(ROOT):
        sys.exit('key files must live outside this public repo')
    if os.path.exists(x.out): sys.exit(f'{x.out} exists; pick a new file for a new send')
    taken = set()
    if os.path.exists(MASTER):
        rows = list(csv.DictReader(open(MASTER, encoding='utf-8')))
        taken = {r['code'] for r in rows}
        if any(r['send'] == x.send for r in rows): sys.exit(f'send "{x.send}" is already in {MASTER}')
    reuse = {r['to']: r['code'] for r in csv.DictReader(open(x.codes, encoding='utf-8'))} if x.codes else {}
    out = []
    for i, r in enumerate(json.load(open(x.recipients, encoding='utf-8')), 1):
        c = reuse.get(r['to'])
        while not c or c in taken: c = secrets.token_hex(3)
        taken.add(c)
        out.append({'minted': date.today().isoformat(), 'send': x.send, 'doc': x.doc, 'n': r.get('n', i),
                    'name': r['name'], 'to': r['to'], 'code': c, 'link': f'{BASE}/{x.doc}/?r={c}'})
    with open(x.out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, COLS); w.writeheader(); w.writerows(out)
    new = not os.path.exists(MASTER)
    with open(MASTER, 'a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, COLS)
        if new: w.writeheader()
        w.writerows(out)
    print(f'{len(out)} links -> {x.out}; appended to {MASTER}')


if __name__ == '__main__':
    main()
