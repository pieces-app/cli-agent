# coding: utf-8

"""
    Pieces Isomorphic OpenAPI

    Endpoints for Assets, Formats, Users, Asset, Format, User.

    The version of the OpenAPI document: 1.0
    Contact: tsavo@pieces.app
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest
import datetime

from openapi_client.models.tracked_asset_event_format_reclassification_metadata import TrackedAssetEventFormatReclassificationMetadata  # noqa: E501

class TestTrackedAssetEventFormatReclassificationMetadata(unittest.TestCase):
    """TrackedAssetEventFormatReclassificationMetadata unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> TrackedAssetEventFormatReclassificationMetadata:
        """Test TrackedAssetEventFormatReclassificationMetadata
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `TrackedAssetEventFormatReclassificationMetadata`
        """
        model = TrackedAssetEventFormatReclassificationMetadata()  # noqa: E501
        if include_optional:
            return TrackedAssetEventFormatReclassificationMetadata(
                var_schema = openapi_client.models.embedded_model_schema.EmbeddedModelSchema(
                    migration = 56, 
                    semantic = 'MAJOR_0_MINOR_0_PATCH_1', ),
                previous = openapi_client.models.classification.Classification(
                    schema = openapi_client.models.embedded_model_schema.EmbeddedModelSchema(
                        migration = 56, 
                        semantic = 'MAJOR_0_MINOR_0_PATCH_1', ), 
                    generic = 'CODE', 
                    specific = 'csx', 
                    rendering = 'HTML', ),
                current = openapi_client.models.classification.Classification(
                    schema = openapi_client.models.embedded_model_schema.EmbeddedModelSchema(
                        migration = 56, 
                        semantic = 'MAJOR_0_MINOR_0_PATCH_1', ), 
                    generic = 'CODE', 
                    specific = 'csx', 
                    rendering = 'HTML', )
            )
        else:
            return TrackedAssetEventFormatReclassificationMetadata(
        )
        """

    def testTrackedAssetEventFormatReclassificationMetadata(self):
        """Test TrackedAssetEventFormatReclassificationMetadata"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()