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

from openapi_client.models.conversation_messages import ConversationMessages  # noqa: E501

class TestConversationMessages(unittest.TestCase):
    """ConversationMessages unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> ConversationMessages:
        """Test ConversationMessages
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `ConversationMessages`
        """
        model = ConversationMessages()  # noqa: E501
        if include_optional:
            return ConversationMessages(
                var_schema = openapi_client.models.embedded_model_schema.EmbeddedModelSchema(
                    migration = 56, 
                    semantic = 'MAJOR_0_MINOR_0_PATCH_1', ),
                iterable = [
                    openapi_client.models.conversation_message.ConversationMessage(
                        schema = openapi_client.models.embedded_model_schema.EmbeddedModelSchema(
                            migration = 56, 
                            semantic = 'MAJOR_0_MINOR_0_PATCH_1', ), 
                        id = '', 
                        created = openapi_client.models.grouped_timestamp.GroupedTimestamp(
                            value = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                            readable = 'Last week - June 3rd, 3:33 a.m.', ), 
                        updated = openapi_client.models.grouped_timestamp.GroupedTimestamp(
                            value = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                            readable = 'Last week - June 3rd, 3:33 a.m.', ), 
                        deleted = , 
                        model = openapi_client.models.model.Model(
                            id = '', 
                            version = '', 
                            created = , 
                            name = '', 
                            description = '', 
                            cloud = True, 
                            type = 'BALANCED', 
                            usage = 'OCR', 
                            bytes = openapi_client.models.byte_descriptor.ByteDescriptor(
                                value = 33600, 
                                readable = '33.6 KB', ), 
                            ram = openapi_client.models.byte_descriptor.ByteDescriptor(
                                value = 33600, 
                                readable = '33.6 KB', ), 
                            quantization = '', 
                            foundation = 'GPT_3.5', 
                            downloaded = True, 
                            loaded = True, 
                            unique = '', 
                            parameters = 1.337, 
                            provider = 'APPLE', 
                            cpu = True, 
                            downloading = True, ), 
                        fragment = openapi_client.models.fragment_format.FragmentFormat(
                            string = openapi_client.models.transferable_string.TransferableString(
                                raw = '', 
                                base64 = '', 
                                base64_url = '', 
                                data_url = '', ), 
                            metadata = openapi_client.models.fragment_metadata.FragmentMetadata(
                                ext = 'csx', ), ), 
                        conversation = openapi_client.models.referenced_conversation.ReferencedConversation(
                            id = '', 
                            reference = openapi_client.models.flattened_conversation.FlattenedConversation(
                                id = '', 
                                name = '', 
                                created = , 
                                updated = , 
                                favorited = True, 
                                application = openapi_client.models.application.Application(
                                    id = '', 
                                    name = 'SUBLIME', 
                                    version = '', 
                                    platform = 'WEB', 
                                    onboarded = True, 
                                    privacy = 'OPEN', 
                                    capabilities = 'LOCAL', 
                                    mechanism = 'MANUAL', 
                                    automatic_unload = True, ), 
                                annotations = openapi_client.models.flattened_annotations.FlattenedAnnotations(
                                    iterable = [
                                        openapi_client.models.referenced_annotation.ReferencedAnnotation(
                                            id = '', )
                                        ], 
                                    indices = {
                                        'key' : 56
                                        }, 
                                    score = openapi_client.models.score.Score(
                                        manual = 56, 
                                        automatic = 56, 
                                        priority = 56, 
                                        reuse = 56, 
                                        update = 56, ), ), 
                                messages = openapi_client.models.flattened_conversation_messages.FlattenedConversationMessages(
                                    iterable = [
                                        openapi_client.models.referenced_conversation_message.ReferencedConversationMessage(
                                            id = '', )
                                        ], ), 
                                assets = openapi_client.models.flattened_assets_[dag_safety].FlattenedAssets [DAG Safety](), 
                                anchors = openapi_client.models.flattened_anchors.FlattenedAnchors(
                                    iterable = [
                                        openapi_client.models.referenced_anchor.ReferencedAnchor(
                                            id = '', )
                                        ], ), 
                                type = 'COPILOT', 
                                grounding = openapi_client.models.conversation_grounding.ConversationGrounding(), 
                                score = openapi_client.models.score.Score(
                                    manual = 56, 
                                    automatic = 56, 
                                    priority = 56, 
                                    reuse = 56, 
                                    update = 56, ), ), ), 
                        sentiment = 'LIKE', 
                        role = 'USER', 
                        score = , 
                        annotations = openapi_client.models.flattened_annotations.FlattenedAnnotations(
                            iterable = [
                                openapi_client.models.referenced_annotation.ReferencedAnnotation(
                                    id = '', )
                                ], ), )
                    ],
                indices = {
                    'key' : 56
                    },
                score = openapi_client.models.score.Score(
                    schema = openapi_client.models.embedded_model_schema.EmbeddedModelSchema(
                        migration = 56, 
                        semantic = 'MAJOR_0_MINOR_0_PATCH_1', ), 
                    manual = 56, 
                    automatic = 56, 
                    priority = 56, 
                    reuse = 56, 
                    update = 56, 
                    reference = 56, )
            )
        else:
            return ConversationMessages(
                iterable = [
                    openapi_client.models.conversation_message.ConversationMessage(
                        schema = openapi_client.models.embedded_model_schema.EmbeddedModelSchema(
                            migration = 56, 
                            semantic = 'MAJOR_0_MINOR_0_PATCH_1', ), 
                        id = '', 
                        created = openapi_client.models.grouped_timestamp.GroupedTimestamp(
                            value = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                            readable = 'Last week - June 3rd, 3:33 a.m.', ), 
                        updated = openapi_client.models.grouped_timestamp.GroupedTimestamp(
                            value = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                            readable = 'Last week - June 3rd, 3:33 a.m.', ), 
                        deleted = , 
                        model = openapi_client.models.model.Model(
                            id = '', 
                            version = '', 
                            created = , 
                            name = '', 
                            description = '', 
                            cloud = True, 
                            type = 'BALANCED', 
                            usage = 'OCR', 
                            bytes = openapi_client.models.byte_descriptor.ByteDescriptor(
                                value = 33600, 
                                readable = '33.6 KB', ), 
                            ram = openapi_client.models.byte_descriptor.ByteDescriptor(
                                value = 33600, 
                                readable = '33.6 KB', ), 
                            quantization = '', 
                            foundation = 'GPT_3.5', 
                            downloaded = True, 
                            loaded = True, 
                            unique = '', 
                            parameters = 1.337, 
                            provider = 'APPLE', 
                            cpu = True, 
                            downloading = True, ), 
                        fragment = openapi_client.models.fragment_format.FragmentFormat(
                            string = openapi_client.models.transferable_string.TransferableString(
                                raw = '', 
                                base64 = '', 
                                base64_url = '', 
                                data_url = '', ), 
                            metadata = openapi_client.models.fragment_metadata.FragmentMetadata(
                                ext = 'csx', ), ), 
                        conversation = openapi_client.models.referenced_conversation.ReferencedConversation(
                            id = '', 
                            reference = openapi_client.models.flattened_conversation.FlattenedConversation(
                                id = '', 
                                name = '', 
                                created = , 
                                updated = , 
                                favorited = True, 
                                application = openapi_client.models.application.Application(
                                    id = '', 
                                    name = 'SUBLIME', 
                                    version = '', 
                                    platform = 'WEB', 
                                    onboarded = True, 
                                    privacy = 'OPEN', 
                                    capabilities = 'LOCAL', 
                                    mechanism = 'MANUAL', 
                                    automatic_unload = True, ), 
                                annotations = openapi_client.models.flattened_annotations.FlattenedAnnotations(
                                    iterable = [
                                        openapi_client.models.referenced_annotation.ReferencedAnnotation(
                                            id = '', )
                                        ], 
                                    indices = {
                                        'key' : 56
                                        }, 
                                    score = openapi_client.models.score.Score(
                                        manual = 56, 
                                        automatic = 56, 
                                        priority = 56, 
                                        reuse = 56, 
                                        update = 56, ), ), 
                                messages = openapi_client.models.flattened_conversation_messages.FlattenedConversationMessages(
                                    iterable = [
                                        openapi_client.models.referenced_conversation_message.ReferencedConversationMessage(
                                            id = '', )
                                        ], ), 
                                assets = openapi_client.models.flattened_assets_[dag_safety].FlattenedAssets [DAG Safety](), 
                                anchors = openapi_client.models.flattened_anchors.FlattenedAnchors(
                                    iterable = [
                                        openapi_client.models.referenced_anchor.ReferencedAnchor(
                                            id = '', )
                                        ], ), 
                                type = 'COPILOT', 
                                grounding = openapi_client.models.conversation_grounding.ConversationGrounding(), 
                                score = openapi_client.models.score.Score(
                                    manual = 56, 
                                    automatic = 56, 
                                    priority = 56, 
                                    reuse = 56, 
                                    update = 56, ), ), ), 
                        sentiment = 'LIKE', 
                        role = 'USER', 
                        score = , 
                        annotations = openapi_client.models.flattened_annotations.FlattenedAnnotations(
                            iterable = [
                                openapi_client.models.referenced_annotation.ReferencedAnnotation(
                                    id = '', )
                                ], ), )
                    ],
        )
        """

    def testConversationMessages(self):
        """Test ConversationMessages"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()