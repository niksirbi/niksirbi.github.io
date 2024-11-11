import pyalex

pyalex.config.email = "niko.sirbiladze@gmail.com"

# My OpenAlex ID
my_id = "A5086452643"

my_pubs = pyalex.Works().filter(
    authorships = {"author": {"id": my_id}},
    type="article",
    ).get()

# add specific publications by ID
# These were missed by the filter above (because my authorship position
# was >100 and the API call truncates the list of authors in the response)
extra_pub_ids = ["W3209642529"]
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
        for idx, authorship in enumerate(authorships):
            if authorship["author"]["id"].endswith(my_id):
                new_pub["my_position"] = idx
                new_pub["me_first_author"] = authorship["author_position"] == "first"
                new_pub["me_corresponding"] = authorship["is_corresponding"]
                new_pub["my_affiliations"] = [
                    aff["display_name"] for aff in authorship["institutions"]
                ]
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
        if not idx:
            cleaned_pubs.append(pub)
        elif len(idx) > 1: 
            raise ValueError("Publication titles in cleaned_pubs are not unique")
        else:
            idx = idx[0]
            if pub["source_type"] == "journal":
                cleaned_pubs[idx] = pub
    return cleaned_pubs


if __name__ == "__main__":
    my_processed_pubs = process_pubs(
        my_pubs, exclude_keywords=["StandardRat", "Author Correction"]
    )
    print(len(my_processed_pubs))
    for pub in my_processed_pubs:
        print(pub["title"])
        print(pub["source_name"])
        print("num_authors:", pub["num_authors"])
        print("my_position:", pub["my_position"])
        print("---")
