from pieces.wrapper.basic_identifier.asset import BasicAsset
from .list_command import ListCommand

# Map search_type to descriptive text
search_type_map = {
    'ncs': 'Neural Code Search',
    'fts': 'Full Text Search',
    'fuzzy': 'Fuzzy Search'
}


def search(query, **kwargs):
    search_type = kwargs.get('search_type', 'fuzzy')

    # Join the list of strings into a single search phrase
    search_phrase = ' '.join(query)

    asset_details = BasicAsset.search(search_phrase, search_type)

    # Print the combined asset details
    if asset_details:
        search_type_text = search_type_map.get(search_type, 'Search')
        ListCommand.list_assets(
            assets=asset_details,
            footer=(f"Search Type: {search_type_text}"
                    f"| Results Found: {len(asset_details)}")
        )
    else:
        print("No matches found.")
