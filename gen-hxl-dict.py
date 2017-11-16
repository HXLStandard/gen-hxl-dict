import hxl, html, jinja2, re, sys

if sys.version_info < (3, 2):
    raise SystemExit("gen-hxl-dict requires at least Python 3.2")

# Set up Jinja2 template environment
env = jinja2.Environment(
    loader=jinja2.PackageLoader('gen-hxl-dict', 'templates'),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

#
# Constants
#

HASHTAGS_URL = 'https://docs.google.com/spreadsheets/d/1En9FlmM8PrbTWgl3UHPF_MXnJ6ziVZFhBbojSJzBdLI/edit#gid=319251406'
"""URL for the HXL dataset defining the core hashtags."""

HASHTAG_CATEGORIES_URL = 'https://docs.google.com/spreadsheets/d/1En9FlmM8PrbTWgl3UHPF_MXnJ6ziVZFhBbojSJzBdLI/edit#gid=1821230611'
"""URL for the definitions of hashtag categories."""

ATTRIBUTES_URL = 'https://docs.google.com/spreadsheets/d/1En9FlmM8PrbTWgl3UHPF_MXnJ6ziVZFhBbojSJzBdLI/edit#gid=1810309357'
"""URL for the HXL dataset defining the core attributes."""

ATTRIBUTE_CATEGORIES_URL = 'https://docs.google.com/spreadsheets/d/1En9FlmM8PrbTWgl3UHPF_MXnJ6ziVZFhBbojSJzBdLI/edit#gid=227333887'
"""URL for the definitions of hashtag categories."""

#
# Variables
#

hashtag_defs = {}
"""Hashtag definitions (HXL rows)."""

hashtag_categories = []
"""Hashtag category definitions."""

hashtags_by_category = {}
"""Hashtags grouped by category."""

hashtag_attribute_map = {}
"""Hashtag-attribute associations."""

attribute_defs = {}
"""Attribute definitions (HXL rows)."""

attribute_categories = []
"""Attribute category definitions."""

attributes_by_category = {}
"""Attributes grouped by category."""

attribute_hashtag_map = {}
"""Attribute-hashtag associations."""

#
# Functions
#

def alert (message):
    """Print a warning to stderr."""
    print("[W] " + message, file=sys.stderr)

def process_hashtag_def (row):
    """Process a hashtag definition."""
    hashtag = row.get('#valid_tag')

    # Save the hashtag definition
    if hashtag:
        if hashtag in hashtag_defs:
            alert('Duplicate hashtag: {}').format(hashtag)
        else:
            hashtag_defs[hashtag] = row
    else:
        alert('Missing hashtag in row: {}'.format(str(row)))
        return

    # Group hashtags by category
    category = row.get('#meta +category')
    if category:
        if not hashtags_by_category.get(category):
            hashtags_by_category[category] = []
        hashtags_by_category[category].append(hashtag)
    else:
        alert('Skipping hashtag (no category): {}'.format(hashtag))

def process_attribute_def (row):
    """Process an attribute definition."""
    attribute = row.get('#valid_attribute')

    # Save the attribute definition
    if attribute:
        if attribute in attribute_defs:
             alert('Duplicate attribute: {}'.format(attribute))
        else:
             attribute_defs[attribute] = row
    else:
        alert('Missing attribute name in row: {}'.format(str(row)))
        return
    
    # Group attribute defs by category
    category = row.get('#meta +category')
    if category:
        if not attributes_by_category.get(category):
            attributes_by_category[category] = []
        attributes_by_category[category].append(attribute)
    else:
        alert('Skipping attribute (does not belong to any category): {}'.format(attribute))

    # Reverse map the associated hashtags
    for hashtag in re.split('\s*,\s*', row.get('#valid_hashtags +list', 0, '')):
        if not hashtag:
            continue
        if not hashtag in hashtag_defs:
             alert('Attribute {} refers to non-existant hashtag {}'.format(attribute, hashtag))
        if not hashtag_attribute_map.get(hashtag):
            hashtag_attribute_map[hashtag] = set()
        hashtag_attribute_map[hashtag].add(attribute)
        if not attribute_hashtag_map.get(attribute):
            attribute_hashtag_map[attribute] = set()
        attribute_hashtag_map[attribute].add(hashtag)

#
# Runtime code
#

# Read the HXL hashtag definitions
hashtag_data = hxl.data(HASHTAGS_URL).with_rows(['#status=Released', '#status=Pre-release'])
for row in hashtag_data:
    process_hashtag_def(row)

# Read the hashtag categories
category_data = hxl.data(HASHTAG_CATEGORIES_URL).sort('#meta+category')
for row in category_data:
    hashtag_categories.append(row)

# Read the HXL attribute definitions
attribute_data = hxl.data(ATTRIBUTES_URL).with_rows(['#status=Released', '#status=Pre-release'])
for row in attribute_data:
    process_attribute_def(row)

# Read the attribute categories
category_data = hxl.data(ATTRIBUTE_CATEGORIES_URL).sort('#meta+category')
for row in category_data:
    attribute_categories.append(row)

# Generate the output
template = env.get_template('dictionary.html')

print(
    template.render(
        hashtag_defs=hashtag_defs,
        hashtag_categories=hashtag_categories,
        hashtags_by_category=hashtags_by_category,
        hashtag_attribute_map=hashtag_attribute_map,
        attribute_defs=attribute_defs,
        attribute_categories=attribute_categories,
        attributes_by_category=attributes_by_category,
        attribute_hashtag_map=attribute_hashtag_map
    ))

sys.exit(0)
