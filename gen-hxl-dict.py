import sys

if sys.version_info < (3, 2):
    raise SystemExit("gen-hxl-dict requires at least Python 3.2")

import hxl, html


HASHTAGS_URL = 'https://docs.google.com/spreadsheets/d/1En9FlmM8PrbTWgl3UHPF_MXnJ6ziVZFhBbojSJzBdLI/edit#gid=319251406'
"""URL for the HXL dataset defining the core hashtags."""

ATTRIBUTES_URL = 'https://docs.google.com/spreadsheets/d/1En9FlmM8PrbTWgl3UHPF_MXnJ6ziVZFhBbojSJzBdLI/edit#gid=1810309357'
"""URL for the HXL dataset defining the core attributes."""


hashtag_categories = {}

def add_to_category (row):
    hashtag = row.get('#valid_tag')
    if not hashtag:
        return # TODO: print warning to stderr
    category = row.get('#meta +category')
    if not category:
        category = 'Uncategorised'
    if not hashtag_categories.get(category):
        hashtag_categories[category] = {}
    hashtag_categories[category][hashtag] = row


print('<!DOCTYPE html>')
print('<html>')
print('<body>')

print('<section id="hashtags">')
print('<h1>1. Core hashtags</h1>')

hashtag_data = hxl.data(HASHTAGS_URL)
for row in hashtag_data:
    add_to_category(row)

for (category, hashtags) in sorted(hashtag_categories.items()):
    print('<section>')
    print('  <h2>' + html.escape(category) + '</h2>')
    print('  <dl>')
    for (hashtag, row) in sorted(hashtags.items()):

        def esc(tagspec, default=''):
            value = row.get(tagspec)
            if not value:
                value = default
            return html.escape(value)
        
        print('    <dt class="hashtag" id="tag_' + html.escape(hashtag.replace('#', '')) + '">' + html.escape(hashtag) + '</dt>')
        print('    <dd class="description">' + esc('#description') + '</dd>')
        print('    <dd class="datatype">Data type: ' + esc('#valid_datatype', 'any') + '</dd>')
        print('    <dd class="status">Status: ' + esc('#status') + ' (' + esc('#meta+release', '') + ')</dd>')
        print('    <dd class="attributes">Suggested attributes: ' + esc('#valid_attributes', 'none') + '</dd>')
        if row.get('#meta +example +hxl'):
            print('    <dd class="example">Example: <code>' +
                  esc('#meta +example +hxl') +
                  '</code> &mdash; ' +
                  esc('#meta +example +description') +
                  ', such as ' +
                  esc('#meta +example +value') +
                  '</dd>')
    print('  </dl>')
    print('</section>')

print('</section>')

print('</body>')
print('</html>')

