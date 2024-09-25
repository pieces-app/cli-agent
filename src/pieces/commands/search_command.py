from pieces.wrapper.basic_identifier.asset import BasicAsset


def search(query, **kwargs):
    search_type = kwargs.get('search_type', 'fuzzy')

    # Join the list of strings into a single search phrase
    search_phrase = ' '.join(query)

    asset_details = BasicAsset.search(search_phrase,search_type)

    # Print the combined asset details
    if asset_details:
        # Map search_type to descriptive text
        search_type_map = {
            'ncs': 'Neural Code Search',
            'fts': 'Full Text Search',
            'fuzzy': 'Fuzzy Search'
        }
        search_type_text = search_type_map.get(search_type, 'Search')

        print(f"\n{search_type_text}\n")
        print("Asset Matches:")
        for index, asset in enumerate(asset_details, start=1):
            print(f"{index}: {asset.name}")
        print()
    else:
        print("No matches found.")