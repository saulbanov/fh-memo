"""Publish one document as <doc>/index.html: copies a standalone HTML file and adds the noindex tag and the
GoatCounter hook (the counted path keeps ?r=, so each recipient's code shows in the dashboard).

python3 -I tools/publish_doc.py <source.html> <doc-slug>
"""
import os, sys

GC = 'futureheist'   # GoatCounter account code
HEAD = '''<meta name="robots" content="noindex, nofollow">
<script>
  var GC = '%s';
  window.goatcounter = { path: function () { return location.pathname + location.search; } };
  if (GC) { var s = document.createElement('script'); s.async = true; s.src = '//gc.zgo.at/count.js';
            s.setAttribute('data-goatcounter', 'https://' + GC + '.goatcounter.com/count'); document.head.appendChild(s); }
</script>
''' % GC


def main():
    src, slug = sys.argv[1], sys.argv[2]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    h = open(src, encoding='utf-8').read()
    if '</head>' not in h: sys.exit(f'{src}: no </head>; give a standalone HTML file')
    if 'name="robots"' in h: sys.exit(f'{src}: already has a robots tag; publish from the clean source')
    os.makedirs(os.path.join(root, slug), exist_ok=True)
    out = os.path.join(root, slug, 'index.html')
    open(out, 'w', encoding='utf-8').write(h.replace('</head>', HEAD + '</head>', 1))
    print(f'wrote {out}\nlive at https://saulbanov.github.io/fh-memo/{slug}/ once pushed')


if __name__ == '__main__':
    main()
