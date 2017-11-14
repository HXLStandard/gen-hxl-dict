import sys

if sys.version_info < (3, 2):
    raise SystemExit("gen-hxl-dict requires at least Python 3.2")

import hxl, html, jinja2, re


HASHTAGS_URL = 'https://docs.google.com/spreadsheets/d/1En9FlmM8PrbTWgl3UHPF_MXnJ6ziVZFhBbojSJzBdLI/edit#gid=319251406'
"""URL for the HXL dataset defining the core hashtags."""

ATTRIBUTES_URL = 'https://docs.google.com/spreadsheets/d/1En9FlmM8PrbTWgl3UHPF_MXnJ6ziVZFhBbojSJzBdLI/edit#gid=1810309357'
"""URL for the HXL dataset defining the core attributes."""

hashtag_defs = {}
"""Hashtag definitions (HXL rows)."""

hashtags_by_category = {}
"""Hashtags grouped by category."""

hashtag_attribute_map = {}
"""Hashtag-attribute associations."""

attribute_defs = {}
"""Attribute definitions (HXL rows)."""

attributes_by_category = {}
"""Attributes grouped by category."""

attribute_hashtag_map = {}
"""Attribute-hashtag associations."""


def process_hashtag_def (row):
    """Process a hashtag definition."""
    hashtag = row.get('#valid_tag')

    # Save the hashtag definition
    if hashtag:
        # TODO report duplicate definitions
        hashtag_defs[hashtag] = row
    else:
        return # TODO print warning to STDERR

    # Group hashtags by category
    category = row.get('#meta +category')
    if category:
        if not hashtags_by_category.get(category):
            hashtags_by_category[category] = []
        hashtags_by_category[category].append(hashtag)
    else:
        pass # TODO warning of missing category

def process_attribute_def (row):
    """Process an attribute definition."""
    attribute = row.get('#valid_attribute')

    # Save the attribute definition
    if attribute:
        # TODO report duplicate definitions
        attribute_defs[attribute] = row
    else:
        return # TODO report warning to STDERR
    
    # Group attribute defs by category
    category = row.get('#meta +category')
    if category:
        if not attributes_by_category.get(category):
            attributes_by_category[category] = []
        attributes_by_category[category].append(attribute)
    else:
        pass # TODO warning of missing category

    # Reverse map the associated hashtags
    for hashtag in re.split('\s*,\s*', row.get('#valid_hashtags +list', 0, '')):
        if not hashtag:
            continue
        # TODO report non-existant hashtag
        if not hashtag_attribute_map.get(hashtag):
            hashtag_attribute_map[hashtag] = set()
        hashtag_attribute_map[hashtag].add(attribute)
        if not attribute_hashtag_map.get(attribute):
            attribute_hashtag_map[attribute] = set()
        attribute_hashtag_map[attribute].add(hashtag)
    

# Read the HXL hashtag definitions
hashtag_data = hxl.data(HASHTAGS_URL)
for row in hashtag_data:
    process_hashtag_def(row)

# Read the HXL attribute definitions
attribute_data = hxl.data(ATTRIBUTES_URL)
for row in attribute_data:
    process_attribute_def(row)


# Generate the output
env = jinja2.Environment(
    loader=jinja2.PackageLoader('gen-hxl-dict', 'templates'),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

template = env.get_template('dictionary.html')

print(
    template.render(
        hashtag_defs=hashtag_defs,
        hashtags_by_category=hashtags_by_category,
        hashtag_attribute_map=hashtag_attribute_map,
        attribute_defs=attribute_defs,
        attributes_by_category=attributes_by_category,
        attribute_hashtag_map=attribute_hashtag_map
    ))
