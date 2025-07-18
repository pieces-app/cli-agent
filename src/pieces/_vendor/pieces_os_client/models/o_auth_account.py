# coding: utf-8

"""
    Pieces Isomorphic OpenAPI

    Endpoints for Assets, Formats, Users, Asset, Format, User.

    The version of the OpenAPI document: 1.0
    Contact: tsavo@pieces.app
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json



from pydantic.v1 import BaseModel, Field, constr

class OAuthAccount(BaseModel):
    """
    A Model to support account creation to Auth0's Database.  # noqa: E501
    """
    client_id: constr(strict=True, min_length=1) = Field(default=..., description="The client_id of your client.")
    email: constr(strict=True, min_length=1) = Field(default=..., description="The user's email address.")
    connection: constr(strict=True, min_length=1) = Field(default=..., description="The name of the database configured to your client.")
    username: constr(strict=True, min_length=1) = Field(default=..., description="The user's username. Only valid if the connection requires a username.")
    given_name: constr(strict=True, min_length=1) = Field(default=..., description="The user's given name(s).")
    family_name: constr(strict=True, min_length=1) = Field(default=..., description="The user's family name(s).")
    name: constr(strict=True, min_length=1) = Field(default=..., description="The user's full name.")
    picture: constr(strict=True, min_length=1) = Field(default=..., description="A URI pointing to the user's picture.")
    nickname: constr(strict=True, min_length=1) = Field(default=..., description="The user's nickname.")
    __properties = ["client_id", "email", "connection", "username", "given_name", "family_name", "name", "picture", "nickname"]

    class Config:
        """Pydantic configuration"""
        allow_population_by_field_name = True
        validate_assignment = True

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.dict(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> OAuthAccount:
        """Create an instance of OAuthAccount from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> OAuthAccount:
        """Create an instance of OAuthAccount from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return OAuthAccount.parse_obj(obj)

        _obj = OAuthAccount.parse_obj({
            "client_id": obj.get("client_id"),
            "email": obj.get("email"),
            "connection": obj.get("connection"),
            "username": obj.get("username"),
            "given_name": obj.get("given_name"),
            "family_name": obj.get("family_name"),
            "name": obj.get("name"),
            "picture": obj.get("picture"),
            "nickname": obj.get("nickname")
        })
        return _obj


