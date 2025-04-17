import yaml
import pyalex
from typing import List, Dict, Any

# Configuration
AUTHOR_ID = "A5086452643"
EMAIL = "niko.sirbiladze@gmail.com"
OUTPUT_PATH = "publications/publications.yml"
EXTRA_PUB_IDS = ["W3209642529", "W3131396636"]
EXCLUDE_KEYWORDS = [
    "Author Correction",
    "How Variable Are Our Rat",  # conference proceedings
    # preprints that have been subsequently published
    # in a journal under a different title
    "StandardRat",
    "Preserving functional network structure under anesthesia",
    "Circuits in the absence of cortical layers",
]


def fetch_publications() -> List[Dict[Any, Any]]:
    """Fetch publications from OpenAlex API."""
    publications = []

    # Fetch publications by work type
    for work_type in ["article", "review", "preprint"]:
        publications += pyalex.Works().filter(
            authorships={"author": {"id": AUTHOR_ID}},
            type=work_type
        ).get()

    # Add specific publications by ID that were missed by the filter
    # (because I was not among the first 100 listed authors)
    publications += [pyalex.Works()[pub_id] for pub_id in EXTRA_PUB_IDS]

    # Fetch full publication data if author list is truncated
    for i, pub in enumerate(publications):
        if "is_authors_truncated" in pub and pub["is_authors_truncated"]:
            publications[i] = pyalex.Works()[pub["id"]]

    return publications


def format_authors(
    authorships: List[Dict], my_position: int, num_authors: int
) -> str:
    """Format author string based on my position in the author list."""
    author_names = [a["author"]["display_name"] for a in authorships]

    # If am among the first three authors, include me before "et al."
    if my_position < 3:
        authors_str = ", ".join(author_names[:my_position + 1])
        if num_authors > my_position + 1:
            authors_str += " et al."
    # Otherwise, include only the first author and "et al."
    else:
        authors_str = author_names[0]
        if num_authors > 1:
            authors_str += " et al."

    return authors_str


def extract_author_info(authorships: List[Dict]) -> Dict:
    """Extract author-specific information."""
    author_info = {}
    author_names = []

    for idx, authorship in enumerate(authorships):
        author_names.append(authorship["author"]["display_name"])
        if authorship["author"]["id"].endswith(AUTHOR_ID):
            author_info["my_position"] = idx
            author_info["me_first_author"] = (
                authorship["author_position"] == "first"
            )
            author_info["me_corresponding"] = authorship["is_corresponding"]
            author_info["my_affiliations"] = [
                aff["display_name"] for aff in authorship["institutions"]
            ]

    return author_info


def format_publication(pub: Dict) -> Dict:
    """Transform publication data into a convenient format,
    by adding extra fields and formatting author information.
    """
    new_pub = pub.copy()
    authorships = pub["authorships"]

    # Extract author information
    new_pub["num_authors"] = len(authorships)
    author_info = extract_author_info(authorships)
    new_pub.update(author_info)

    # Format author string and determine category
    my_pos = new_pub["my_position"]
    new_pub["authors_str"] = format_authors(
        authorships, my_pos, new_pub["num_authors"]
    )
    new_pub["categories"] = (
        ["Main Author"] if my_pos < 3 else ["Contributing Author"]
    )

    # Extract source information
    source = pub["primary_location"]["source"]
    new_pub["source_type"] = source["type"]
    new_pub["source_name"] = source["display_name"].split("(")[0].strip()

    return new_pub


def remove_duplicate_pubs(pubs: List[Dict]) -> List[Dict]:
    """
    Remove duplicates, preferring journal publications over preprints.
    """
    cleaned_pubs = []
    for pub in pubs:
        idx = [
            i for i, p in enumerate(cleaned_pubs) if p["title"] == pub["title"]
        ]
        if not idx:  # If the title is not already in cleaned_pubs
            cleaned_pubs.append(pub)
        elif len(idx) > 1:   # If multiple "clean" publications share a title
            raise ValueError(
                "Publication titles in cleaned_pubs are not unique"
            )
        else:  # If the title is already in cleaned_pubs once
            idx = idx[0]
            if pub["source_type"] == "journal":
                cleaned_pubs[idx] = pub
    return cleaned_pubs


def sort_publications(pubs: List[Dict]) -> List[Dict]:
    """
    Sort publications by my position (ascending)
    and then by publication date (descending).
    """
    return sorted(
        pubs,
        key=lambda pub: (
            pub["my_position"], -int(pub["publication_date"].replace("-", ""))
        ),
    )


def process_pubs(pubs: List[Dict]) -> List[Dict]:
    """Process a list of publications.

    1. Exclude publications with certain keywords in the title.
    2. Fetch work with the full author list if truncated.
    3. Format each publication for convenient access.
    4. Remove duplicates.
    5. Sort by my position and publication date.
    """
    processed_pubs = []

    for pub in pubs:
        # Exclude publications with certain keywords in the title
        if any(kw in pub["title"] for kw in EXCLUDE_KEYWORDS):
            continue

        # If the author list is truncated, fetch work with the full author list
        if pub.get("is_authors_truncated", False):
            pub = pyalex.Works()[pub["id"]]

        # Process the publication
        processed_pubs.append(format_publication(pub))

    # Remove duplicates
    return sort_publications(remove_duplicate_pubs(processed_pubs))


def write_yaml(pubs: List[Dict], output_path: str):
    """Write the processed publications to a YAML file."""
    content = []
    for pub in pubs:
        pub_dict = {
            "path": pub["doi"],
            "title": pub["title"],
            "subtitle": pub["source_name"],
            "date": pub["publication_date"],
            "author": pub["authors_str"],
            "description": str(pub["cited_by_count"]),
        }
        content.append(pub_dict)

    with open(output_path, "w") as f:
        yaml.dump(content, f, sort_keys=False)


def main():
    """Main function to run the script."""
    pyalex.config.email = EMAIL
    pubs = fetch_publications()
    processed_pubs = process_pubs(pubs)
    write_yaml(processed_pubs, OUTPUT_PATH)


if __name__ == "__main__":
    main()
