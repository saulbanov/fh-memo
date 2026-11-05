# fh-memo

Future Heist documents shared by tracked link, served by GitHub Pages at https://saulbanov.github.io/fh-memo/.
Every page is `noindex`; the root page shows nothing and lists nothing. Each document lives in its own folder:

| Folder | Document | Source |
|---|---|---|
| `2026-11-postelection/` | Post-election funder memo, November 2026 | `future-heist/fhwr-runway/working/memo-send/Future_Heist_memo.html` |

## A new document

```
python3 -I tools/publish_doc.py <standalone.html> <doc-slug>
```

Writes `<doc-slug>/index.html` with the noindex tag and the visit counter added. Edit the source and republish;
don't hand-edit the copy here.

## A new send

```
python3 -I tools/mint_links.py --send <send-name> --doc <doc-slug> --recipients <recipients.json> --out <key.csv>
```

Every recipient of every send gets a fresh random code (`?r=<code>`), so a code names one person in one send.
The key from code to person is private. The script refuses to write it inside this repo; it writes the send's
key file where `--out` says and appends to the master key (`$FH_MEMO_KEYS`, default
`future-heist/fhwr-runway/memo-links-master.csv`).

## Reading the counts

Visits are counted by GoatCounter (account `futureheist`, https://futureheist.goatcounter.com). Each visit is
recorded with its full path, `/fh-memo/<doc-slug>/?r=<code>`; look the code up in the master key, or run

```
python3 -I tools/visits.py [--send <send-name>]
```

which pulls the counts from GoatCounter's API (key in `GOATCOUNTER_TOKEN`; setup note at the top of the script) and
prints one row per recipient. A visit means
someone opened that link, not that the named person read it: forwards count under the original code, and some
mail systems' link scanners open links before a person does.
