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

from openapi_client.models.auth0 import Auth0  # noqa: E501

class TestAuth0(unittest.TestCase):
    """Auth0 unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> Auth0:
        """Test Auth0
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `Auth0`
        """
        model = Auth0()  # noqa: E501
        if include_optional:
            return Auth0(
                identity = openapi_client.models.auth0_identity.Auth0Identity(
                    connection = '', 
                    is_social = True, 
                    provider = '', 
                    user_id = '', 
                    access_token = '', 
                    expires_in = 56, ),
                user = openapi_client.models.auth0_user.Auth0User(
                    name = 'Tsavo Knott', 
                    picture = 'https://picsum.photos/200', 
                    email = 'user@pieces.app', 
                    created_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    email_verified = True, 
                    family_name = '', 
                    given_name = '', 
                    identities = [
                        openapi_client.models.auth0_identity.Auth0Identity(
                            connection = '', 
                            is_social = True, 
                            provider = '', 
                            user_id = '', 
                            access_token = '', 
                            expires_in = 56, )
                        ], 
                    nickname = '', 
                    updated_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    username = '', 
                    user_metadata = openapi_client.models.auth0_user_metadata.Auth0UserMetadata(
                        schema = openapi_client.models.embedded_model_schema.EmbeddedModelSchema(
                            migration = 56, 
                            semantic = 'MAJOR_0_MINOR_0_PATCH_1', ), 
                        global_id = '', 
                        cloud_key = '', 
                        stripe_customer_id = '', 
                        vanityname = '', 
                        allocation = openapi_client.models.auth0_user_allocation_metadata.Auth0UserAllocationMetadata(
                            project = '', 
                            region = '', ), ), 
                    locale = '', 
                    user_id = '', 
                    last_ip = '', 
                    last_login = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                    logins_count = 56, 
                    blocked_for = [
                        ''
                        ], 
                    guardian_authenticators = [
                        ''
                        ], ),
                metadata = openapi_client.models.auth0_user_metadata.Auth0UserMetadata(
                    schema = openapi_client.models.embedded_model_schema.EmbeddedModelSchema(
                        migration = 56, 
                        semantic = 'MAJOR_0_MINOR_0_PATCH_1', ), 
                    global_id = '', 
                    cloud_key = '', 
                    stripe_customer_id = '', 
                    vanityname = '', 
                    allocation = openapi_client.models.auth0_user_allocation_metadata.Auth0UserAllocationMetadata(
                        project = '', 
                        region = '', ), ),
                domain = '',
                client = '',
                audience = '',
                redirects = openapi_client.models.auth0_redirects.Auth0_redirects(
                    authenticated = '', 
                    unauthenticated = '', ),
                o_auth = openapi_client.models.o_auth_group.OAuthGroup(
                    token = openapi_client.models.o_auth_token.OAuthToken(
                        schema = openapi_client.models.embedded_model_schema.EmbeddedModelSchema(
                            migration = 56, 
                            semantic = 'MAJOR_0_MINOR_0_PATCH_1', ), 
                        access_token = '', 
                        token_type = 'Bearer', 
                        expires_in = 86400, 
                        scope = '', 
                        refresh_token = '', 
                        id_token = '', ), 
                    account = openapi_client.models.o_auth_account.OAuthAccount(
                        client_id = '0', 
                        email = '0', 
                        connection = '0', 
                        username = '0', 
                        given_name = '0', 
                        family_name = '0', 
                        name = '0', 
                        picture = '0', 
                        nickname = '0', ), ),
                namespace = ''
            )
        else:
            return Auth0(
                domain = '',
                client = '',
                audience = '',
                redirects = openapi_client.models.auth0_redirects.Auth0_redirects(
                    authenticated = '', 
                    unauthenticated = '', ),
                o_auth = openapi_client.models.o_auth_group.OAuthGroup(
                    token = openapi_client.models.o_auth_token.OAuthToken(
                        schema = openapi_client.models.embedded_model_schema.EmbeddedModelSchema(
                            migration = 56, 
                            semantic = 'MAJOR_0_MINOR_0_PATCH_1', ), 
                        access_token = '', 
                        token_type = 'Bearer', 
                        expires_in = 86400, 
                        scope = '', 
                        refresh_token = '', 
                        id_token = '', ), 
                    account = openapi_client.models.o_auth_account.OAuthAccount(
                        client_id = '0', 
                        email = '0', 
                        connection = '0', 
                        username = '0', 
                        given_name = '0', 
                        family_name = '0', 
                        name = '0', 
                        picture = '0', 
                        nickname = '0', ), ),
        )
        """

    def testAuth0(self):
        """Test Auth0"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()