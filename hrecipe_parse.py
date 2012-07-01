#! /usr/bin/env python
#
# Ben Osment
# Sun Jul  1 11:16:47 2012

"""
Given a website, scrape hRecipe microformat (http://microformats.org/wiki/hrecipe) 
information and stores it in a common format (plaintext or XML)

This is intended to be a tool; recipes can be downloaded and stored in a common 
format so that an app (perhaps a recipe notebook) can make use of them

Example: hRecipe_parse.py -u "http://www.bonappetit.com/recipes/2012/06/peach-blueberry-ice-cream-pie" -o "peach_blueberry_ice_cream_pie.xml"
"""

import argparse
import sys
import urllib2
from BeautifulSoup import BeautifulSoup

verbose = False

def hrecipe_parse(argv=[]):
    # build the command line parser
    parser = argparse.ArgumentParser(description='Given a website, pulls hRecipe microformat '
                                     '(http://microformats.org/wiki/hrecipe) information '
                                     'and stores it in well-formed XML.')
    parser.add_argument('-u', '--url', help='URL to parse')
    parser.add_argument('-o', '--outfile', help='filename to write the XML result')
    parser.add_argument('--dowload_pictures', action='store_true', help='Download any '
                        'associated pictures')
    parser.add_argument('--verbose', action='store_true')

    # get cli options
    args = parser.parse_args(argv[1:])
    global verbose
    verbose = args.verbose

    if not args.url or not args.outfile:
        print "Error: both URL and output file must be specified"
        parser.print_help()
        sys.exit()
        
    hrecipes = review_scrape(args.url)
    if verbose:
        print "Successfully parsed %d recipes" % len(hrecipes)

    # write recipe out to file 
    # TODO: support other kinds of formats
    with open(args.outfile, 'w') as f:
        for recipe in hrecipes:
            f.write(recipe['fn'])
            f.write('\n')
            f.write('-' * len(recipe['fn']))
            f.write('\n')
            if 'author' in recipe:
                f.write('\nAuthor: %s\n' % recipe['author'])
            if 'published' in recipe:
                f.write('\nPublished: %s\n' % recipe['published'])
            if 'summary' in recipe:
                f.write('\n')
                f.write(recipe['summary'])
                f.write('\n')
            if 'duration' in recipe:
                f.write('\nTime: %s\n' % recipe['duration'])
            f.write('\nIngredients\n')
            f.write('-----------\n')
            for ingredient in recipe['ingredient']:
                f.write(" - %s\n" % ingredient)

            if 'instructions' in recipe:
                f.write('\nInstructions\n')
                f.write('------------\n')
                for (i, instruction) in enumerate(recipe['instructions']):
                    f.write(" %d. %s\n" % (i+1, instruction))

            if 'yield' in recipe:
                f.write("\nYields: %s\n" % recipe['yield'])
            if 'nutrition' in recipe:
                f.write("\nNutrition: %s\n" % recipe['nutrition'])
            if 'tags' in recipe:
                f.write("\nTags: ")
                for tag in recipe['tags']:
                    f.write("%s " % tag)

def review_scrape(url):
    """ Given a URL, find all hRecipes listed and return a dictionary of
        the attributes"""
    try:
        page = urllib2.urlopen(url)
    except Exception as e:
        print "Failed to fetch", url
        if verbose:
            print e
        sys.exit()
    try:
        soup = BeautifulSoup(page)
    except Exception as e:
        print "Failed to parse", url
        if verbose:
            print e
        sys.exit()

    hrecipes = soup.findAll(True, 'hrecipe')
    if verbose:
        print "Found %d recipes" % len(hrecipes)
    return [soup_to_dict(hrecipe) for hrecipe in hrecipes]

def soup_to_dict(hrecipe):
    d = {}
    # only fn and ingredient are mandatory, all other fields
    # are optional
    d['fn'] = hrecipe.find(True, 'fn').text
    # ingredients (multiple)
    ingredients = hrecipe.findAll(True, 'ingredient')
    i = []
    for ingredient in ingredients:
        q = ingredient.find(True, 'quantity')
        u = ingredient.find(True, 'unit')
        n = ingredient.find(True, 'name')
        if q and u and n:
            i.append('%s %s %s' % (q.text, u.text, n.text))
        else:
            i.append(ingredient.text)
    d['ingredient'] = i

    # TODO -- this could probably be refactored
    # yield
    _yield = hrecipe.find(True, 'yield')
    if _yield:
        d['yield'] = _yield.text
    # instructions (multiple)
    instructions = hrecipe.findAll('span', 'instructions')
    if instructions:
        d['instructions'] = [instruction.text for instruction in instructions]
    # duration
    duration = hrecipe.find(True, 'duration')
    if duration:
        d['duration'] = duration.text
    # summary
    summary = hrecipe.find(True, 'summary')
    if summary:
        d['summary'] = summary.text
    # author
    author = hrecipe.find(True, 'author')
    if author:
        d['author'] = author.text
    # published
    published = hrecipe.find(True, 'published')
    if published:
        d['published'] = published.text
    # nutrition
    nutrition = hrecipe.find(True, 'nutrition')
    if nutrition:
        d['nutrition'] = nutrition.text
    # tag (multiple)
    tags = hrecipe.findAll(True, 'tag')
    if tags:
        d['tag'] = [tag.text for tag in tags]

    if verbose:
        for key,value in d.items():
            print key, ":",  value
    return d

if __name__ == '__main__':
    hrecipe_parse(sys.argv)
