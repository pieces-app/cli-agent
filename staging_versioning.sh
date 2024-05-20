#!/bin/bash
#-------------------------------- Getting the Version Data -------------------------

# Get PROD JSON With GET Request
prod_json="$(curl https://storage.googleapis.com/app-releases-production/pieces_cli/production/latest-single.json -H "Accept: application/json")"

# Get First PROD JSON Object in an array, and get the "tag" value
prod_tag=$(echo "$prod_json" | jq '.tag')

# Get STAGING JSON With GET Request
staging_json="$(curl https://storage.googleapis.com/app-releases-staging/pieces_cli/staging/latest-single.json -H "Accept: application/json")"

# Get First JSON Object in an array, and get the "tag" value
staging_tag=$(echo "$staging_json" | jq '.tag')

# Remove "-staging" from tag to manipulate numbers
staging_tag=${staging_tag//".dev1"/}
#---------------------------------------------------------------------------

#------------------------------- Version Extraction ---------------------

prod_tag_pure_num=$(echo "$prod_tag" | sed 's/"//g')
prod_major=$(echo "$prod_tag_pure_num" | cut -d. -f1)
prod_minor=$(echo "$prod_tag_pure_num" | cut -d. -f2)
prod_patch=$(echo "$prod_tag_pure_num" | cut -d. -f3)

staging_tag_pure_num=$(echo "$staging_tag" | sed 's/"//g')
staging_major=$(echo "$staging_tag_pure_num" | cut -d. -f1)
staging_minor=$(echo "$staging_tag_pure_num" | cut -d. -f2)
staging_patch=$(echo "$staging_tag_pure_num" | cut -d. -f3)

#---------------------------------------------------------------------------------

#------------------------------- Staging Versioning Logic ------------------------

# If prod major or minor is higher than staging, update staging major and minor and increment patch to prod plus 1
if [ "$prod_major" -gt "$staging_major" ] || [ "$prod_minor" -gt "$staging_minor" ]
then
  increment_patch=$(expr $prod_patch + 1)
  final_version="$prod_major.$prod_minor.$increment_patch.dev1"
# If prodMajor and prodMinor are the same as stagingMajor and stagingMinor, but prodPatch is greater than staging patch, stagingPatch will be prodPatch incremented by 1
elif [ "$prod_major" -eq "$staging_major" ] && [ "$prod_minor" -eq "$staging_minor" ] && [ "$prod_patch" -gt "$staging_patch" ]
then
  increment_patch=$(expr $prod_patch + 1)
  final_version="$prod_major.$prod_minor.$increment_patch.dev1"
# If prod hasn't changed, increment staging patch by 1
else
  increment_patch=$(expr $staging_patch + 1)
  final_version="$prod_major.$prod_minor.$increment_patch.dev1"
fi

echo $final_version