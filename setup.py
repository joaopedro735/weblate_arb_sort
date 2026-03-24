from setuptools import setup, find_packages

setup(
    name="weblate_arb_sort",
    version="0.1.0",
    author="joaopedro735",
    author_email="yourname@example.com",
    description="Weblate addon to sort Flutter ARB keys alphabetically, keeping @metadata keys adjacent to their parent key.",
    license="GPLv3+",
    keywords="Weblate ARB Flutter sort addon",
    packages=find_packages(),
    install_requires=[
        "weblate>=4.0",
    ],
    entry_points={
        "weblate.addons": [
            "weblate_arb_sort.arb_sort.ArbSortAddon = weblate_arb_sort.arb_sort:ArbSortAddon",
        ],
    },
)
