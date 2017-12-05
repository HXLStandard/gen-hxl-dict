#!/usr/bin/python3
"""Generate the HXL hashtag and attribute dictionary from the master schema.

Requires Python 3.2 or higher.

Usage:

  python gen-hxl-dict.py > output.html
"""
  
import datetime, hxl, html, jinja2, logging, re, sys

# Die if not at least Python 3.2
if sys.version_info < (3, 2):
    raise SystemExit("gen-hxl-dict requires at least Python 3.2")

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

hashtag_categories = []
"""Hashtag category definitions."""

hashtag_category_titles = set()
"""Lookup to make sure categories exist."""

hashtag_defs = {}
"""Hashtag definitions (HXL rows)."""

hashtags_by_category = {}
"""Hashtags grouped by category."""

hashtag_attribute_map = {}
"""Hashtag-attribute associations."""

attribute_categories = []
"""Attribute category definitions."""

attribute_category_titles = set()
"""Lookup to make sure categories exist."""

attribute_defs = {}
"""Attribute definitions (HXL rows)."""

attributes_by_category = {}
"""Attributes grouped by category."""

attribute_hashtag_map = {}
"""Attribute-hashtag associations."""

#
# Functions
#

def process_hashtag_def (row):
    """Process a hashtag definition."""
    hashtag = row.get('#valid_tag')

    # Save the hashtag definition
    if hashtag:
        if hashtag in hashtag_defs:
            logging.warning('Duplicate hashtag: {}').format(hashtag)
        else:
            hashtag_defs[hashtag] = row
    else:
        logging.warning('Missing hashtag in row: {}'.format(str(row)))
        return

    # Group hashtags by category
    category = row.get('#meta +category')
    if category:
        if not hashtags_by_category.get(category):
            hashtags_by_category[category] = []
        hashtags_by_category[category].append(hashtag)
        if not category in hashtag_category_titles:
            logging.warning("Unknown hashtag category: {}".format(category))
    else:
        logging.warning('Skipping hashtag (no category): {}'.format(hashtag))

def process_attribute_def (row):
    """Process an attribute definition."""
    attribute = row.get('#valid_attribute')

    # Save the attribute definition
    if attribute:
        if attribute in attribute_defs:
             logging.warning('Duplicate attribute: {}'.format(attribute))
        else:
             attribute_defs[attribute] = row
    else:
        logging.warning('Missing attribute name in row: {}'.format(str(row)))
        return
    
    # Group attribute defs by category
    category = row.get('#meta +category')
    if category:
        if not attributes_by_category.get(category):
            attributes_by_category[category] = []
        attributes_by_category[category].append(attribute)
        if not category in attribute_category_titles:
            logging.warning("Unknown attribute category: {}".format(category))
    else:
        logging.warning('Skipping attribute (does not belong to any category): {}'.format(attribute))

    # Reverse map the associated hashtags
    for hashtag in re.split('\s*,\s*', row.get('#valid_hashtags +list', 0, '')):
        if not hashtag:
            continue
        if not hashtag in hashtag_defs:
             logging.warning('Attribute {} refers to non-existant hashtag {}'.format(attribute, hashtag))
        if not hashtag_attribute_map.get(hashtag):
            hashtag_attribute_map[hashtag] = set()
        hashtag_attribute_map[hashtag].add(attribute)
        if not attribute_hashtag_map.get(attribute):
            attribute_hashtag_map[attribute] = set()
        attribute_hashtag_map[attribute].add(hashtag)

        
def run(hashtag_categories_url, hashtags_url, attribute_categories_url, attributes_url):
    """Run the processes to generate the HTML dictionary."""

    # Set up Jinja2 template environment for rendering HTML
    env = jinja2.Environment(
        loader=jinja2.PackageLoader('gen-hxl-dict', 'templates'),
        autoescape=jinja2.select_autoescape(['html', 'xml'])
    )

    logging.info("Reading hashtag category definitions from {}...".format(hashtag_categories_url))
    category_data = hxl.data(hashtag_categories_url).sort('#meta+category')
    for row in category_data:
        hashtag_category_titles.add(row.get('#meta+category'))
        hashtag_categories.append(row)

    logging.info("Reading hashtag definitions from {}...".format(hashtags_url))
    hashtag_data = hxl.data(hashtags_url).with_rows(['#status=Released', '#status=Pre-release'])
    for row in hashtag_data:
        process_hashtag_def(row)

    logging.info("Reading attribute category definitions from {}...".format(attribute_categories_url))
    category_data = hxl.data(attribute_categories_url).sort('#meta+category')
    for row in category_data:
        attribute_category_titles.add(row.get('#meta+category'))
        attribute_categories.append(row)

    logging.info("Reading attribute definitions from {}...".format(attributes_url))
    attribute_data = hxl.data(attributes_url).with_rows(['#status=Released', '#status=Pre-release'])
    for row in attribute_data:
        process_attribute_def(row)

    logging.info("Generating output...")
    template = env.get_template('dictionary.html')
    print(
        template.render(
            now=datetime.datetime.utcnow(),
            hashtag_defs=hashtag_defs,
            hashtag_categories=hashtag_categories,
            hashtags_by_category=hashtags_by_category,
            hashtag_attribute_map=hashtag_attribute_map,
            attribute_defs=attribute_defs,
            attribute_categories=attribute_categories,
            attributes_by_category=attributes_by_category,
            attribute_hashtag_map=attribute_hashtag_map,
            index_items = sorted(list(hashtag_defs.keys()) + list(attribute_defs.keys()), key=lambda key: key[1:])
        ))

#
# If called as a command-line script.
#
if __name__ == '__main__':
    # log to STDERR
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    run(HASHTAG_CATEGORIES_URL, HASHTAGS_URL, ATTRIBUTE_CATEGORIES_URL, ATTRIBUTES_URL)

# end

