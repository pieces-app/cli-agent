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


from typing import Optional
from pydantic.v1 import BaseModel, Field
from pieces._vendor.pieces_os_client.models.allocation_cloud_url import AllocationCloudUrl
from pieces._vendor.pieces_os_client.models.embedded_model_schema import EmbeddedModelSchema

class AllocationCloudUrls(BaseModel):
    """
    you will have at minimum 2 urls,  base: is the default url of your cloud.  id: is the branded url, uuid.pieces.cloud.  (optional) vanity: is the custom branded url, mark.pieces.cloud  # noqa: E501
    """
    var_schema: Optional[EmbeddedModelSchema] = Field(default=None, alias="schema")
    base: AllocationCloudUrl = Field(...)
    id: AllocationCloudUrl = Field(...)
    vanity: Optional[AllocationCloudUrl] = None
    __properties = ["schema", "base", "id", "vanity"]

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
    def from_json(cls, json_str: str) -> AllocationCloudUrls:
        """Create an instance of AllocationCloudUrls from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic.v1 by calling `to_dict()` of var_schema
        if self.var_schema:
            _dict['schema'] = self.var_schema.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of base
        if self.base:
            _dict['base'] = self.base.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of id
        if self.id:
            _dict['id'] = self.id.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of vanity
        if self.vanity:
            _dict['vanity'] = self.vanity.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> AllocationCloudUrls:
        """Create an instance of AllocationCloudUrls from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return AllocationCloudUrls.parse_obj(obj)

        _obj = AllocationCloudUrls.parse_obj({
            "var_schema": EmbeddedModelSchema.from_dict(obj.get("schema")) if obj.get("schema") is not None else None,
            "base": AllocationCloudUrl.from_dict(obj.get("base")) if obj.get("base") is not None else None,
            "id": AllocationCloudUrl.from_dict(obj.get("id")) if obj.get("id") is not None else None,
            "vanity": AllocationCloudUrl.from_dict(obj.get("vanity")) if obj.get("vanity") is not None else None
        })
        return _obj


