import yaml
import pyalex

pyalex.config.email = "niko.sirbiladze@gmail.com"

# My OpenAlex ID
my_id = "A5086452643"

my_pubs = []
for work_type in ["article", "review", "preprint"]:
    my_pubs += pyalex.Works().filter(
        authorships={"author": {"id": my_id}},
        type=work_type
    ).get()

# add specific publications by ID
# These were missed by the filter above (because my authorship position
# was >100 and the API call truncates the list of authors in the response)
extra_pub_ids = ["W3209642529", "W3131396636"]
my_pubs += [pyalex.Works()[pub_id] for pub_id in extra_pub_ids]

# If the author list is truncated, fetch work with the full author list
for i, pub in enumerate(my_pubs):
    if "is_authors_truncated" in pub and pub["is_authors_truncated"]:
        full_pub = pyalex.Works()[pub["id"]]
        my_pubs[i] = full_pub


def process_pubs(
    pubs: list[dict],
    exclude_keywords: list[str],
):
    processed_pubs = []

    for pub in pubs:

        # Exclude publications with certain keywords in the title
        if any(kw in pub["title"] for kw in exclude_keywords):
            continue

        # If the author list is truncated, fetch work with the full author list
        trunc_key = "is_authors_truncated"
        if trunc_key in pub and pub[trunc_key]:
            pub = pyalex.Works()[pub["id"]]

        # Extract some data to the top level of the publication (for convenience)
        new_pub = pub.copy()
        authorships = pub["authorships"]
        new_pub["num_authors"] = len(authorships)
        author_names = []
        for idx, authorship in enumerate(authorships):
            author_names.append(authorship["author"]["display_name"])
            if authorship["author"]["id"].endswith(my_id):
                new_pub["my_position"] = idx
                new_pub["me_first_author"] = authorship["author_position"] == "first"
                new_pub["me_corresponding"] = authorship["is_corresponding"]
                new_pub["my_affiliations"] = [
                    aff["display_name"] for aff in authorship["institutions"]
                ]

        my_pos = new_pub["my_position"]
        # If I am one of the first 3 authors, list author names
        # until my position, followed by "et al."
        if my_pos < 3:
            new_pub["authors_str"] = ", ".join(author_names[:my_pos + 1])
            if new_pub["num_authors"] > my_pos + 1:
                new_pub["authors_str"] += " et al."
            new_pub["categories"] = ["Main Author"]
        # If I am not among the first 3 authors, list only the first author
        # followed by "et al."
        else:
            new_pub["authors_str"] = author_names[0]
            if new_pub["num_authors"] > 1:
                new_pub["authors_str"] += " et al."
            new_pub["categories"] = ["Contributing Author"]
            
        source = pub["primary_location"]["source"]
        new_pub["source_type"] = source["type"]
        new_pub["source_name"] = source["display_name"].split("(")[0].strip()

        processed_pubs.append(new_pub)

    # Remove duplicates
    processed_pubs = remove_duplicate_pubs(processed_pubs)
    
    return processed_pubs


def remove_duplicate_pubs(
    pubs: list[dict],
) -> list[dict]:
    """
    Remove duplicate publications from the list of publications.

    Sometimes publications with the same title are seen as different publications,
    especially when they are from different sources. This function removes such
    duplicates from the list of publications, preferring the one from a journal
    source (as opposed to a preprint source).
    """
    cleaned_pubs = []
    for pub in pubs:
        idx = [
            i for i, p in enumerate(cleaned_pubs) if p["title"] == pub["title"]
        ]
        if not idx:  # If the title is not already in cleaned_pubs
            cleaned_pubs.append(pub)
        elif len(idx) > 1:   # If multiple "clean" publications share a title
            raise ValueError("Publication titles in cleaned_pubs are not unique")
        else:  # If the title is already in cleaned_pubs once
            idx = idx[0]
            if pub["source_type"] == "journal":
                cleaned_pubs[idx] = pub
    return cleaned_pubs


if __name__ == "__main__":
    my_processed_pubs = process_pubs(
        my_pubs, exclude_keywords=[
            "Author Correction",
            "How Variable Are Our Rat",  # conference proceedings
            # preprints that has been subsequently published in a journal
            # under a different title
            "StandardRat",
            "Preserving functional network structure under anesthesia",
            "Circuits in the absence of cortical layers",
        ]
    )

    # Order publications first by my position in the author list (ascending)
    # and then by reverse publication date (recent first)
    my_sorted_pubs = sorted(
        my_processed_pubs,
        key=lambda pub: (
            pub["my_position"], -int(pub["publication_date"].replace("-", ""))
        ),
    )

    pubs_yaml_content = []
    for pub in my_sorted_pubs:
        pub_dict = {
            "path": pub["doi"],
            "title": pub["title"],
            "subtitle": pub["source_name"],
            "date": pub["publication_date"],
            "author": pub["authors_str"],
            "description": str(pub["cited_by_count"]),
        }
        pubs_yaml_content.append(pub_dict)

    with open("publications/publications.yml", "w") as f:
        yaml.dump(
            pubs_yaml_content, f, sort_keys=False
        )
