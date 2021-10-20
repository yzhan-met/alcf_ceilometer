# Configuration file for the Sphinx documentation builder.

# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html


# -- Path setup --------------------------------------------------------------

from datetime import datetime
import os
from pkg_resources import get_distribution
import sys

PROJECT = "alcf_ceilometer"


# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
sys.path.insert(0, os.path.abspath("../.."))
sys.path.insert(0, os.path.abspath("../../lambdas/alcf_ceilometer/function"))

# -- Project information -----------------------------------------------------

project = PROJECT
year = datetime.now().year
project_copyright = "{year}, FR&D".format(year=year)
author = 'MetService Forecast Research & Development'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "m2r2",
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx_rtd_theme",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'boto3': ('https://boto3.amazonaws.com/v1/documentation/api/latest', None),
    'cdk': ('https://docs.aws.amazon.com/cdk/api/latest/python', None)
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# -- Options for viewcode
viewcode_follow_imported_members = True

# -- Options for napoleon
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
