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
from pydantic.v1 import BaseModel, Field, StrictStr, validator
from pieces._vendor.pieces_os_client.models.embedded_model_schema import EmbeddedModelSchema

class TrackedAssetEventIdentifierDescriptionPairs(BaseModel):
    """
    These are all of the available event types that are permitted in an object pair notation.  # noqa: E501
    """
    var_schema: Optional[EmbeddedModelSchema] = Field(default=None, alias="schema")
    asset_created: Optional[StrictStr] = Field(default='UNKNOWN', description="The key value pair for an asset being created.")
    asset_viewed: Optional[StrictStr] = Field(default='UNKNOWN', description="An asset was viewed")
    asset_format_copied: Optional[StrictStr] = Field(default='UNKNOWN', description="An asset's format was copied")
    asset_format_downloaded: Optional[StrictStr] = Field(default='UNKNOWN', description="An asset's format was downloaded")
    asset_deleted: Optional[StrictStr] = Field(default='UNKNOWN', description="An asset was deleted or not")
    asset_description_updated: Optional[StrictStr] = Field(default='UNKNOWN', description="An asset was redescribed by the user")
    asset_name_updated: Optional[StrictStr] = Field(default='UNKNOWN', description="An asset was renamed by the user")
    asset_format_generic_classification_updated: Optional[StrictStr] = Field(default='UNKNOWN', description="A generic classification was changed on a format within an asset")
    asset_format_specific_classification_updated: Optional[StrictStr] = Field(default='UNKNOWN', description="A specific classification was changed on a format within an asset")
    asset_creation_failed: Optional[StrictStr] = 'UNKNOWN'
    asset_tag_added: Optional[StrictStr] = 'UNKNOWN'
    asset_link_added: Optional[StrictStr] = 'UNKNOWN'
    asset_link_generated: Optional[StrictStr] = Field(default='UNKNOWN', description="user generated a link for the asset")
    asset_link_deleted: Optional[StrictStr] = 'UNKNOWN'
    asset_tag_deleted: Optional[StrictStr] = 'UNKNOWN'
    asset_updated: Optional[StrictStr] = Field(default='UNKNOWN', description="This is just a generic string for an asset was updated.")
    asset_format_value_edited: Optional[StrictStr] = Field(default='UNKNOWN', description="This is a side effect event for a format value getting edited that exists on an asset.")
    asset_format_updated: Optional[StrictStr] = Field(default='UNKNOWN', description="This is a generic activity event for an asset getting updated because our format was updated for some reason.")
    asset_link_revoked: Optional[StrictStr] = Field(default='UNKNOWN', description="This means that a shareable link was revoked.")
    asset_person_added: Optional[StrictStr] = Field(default='UNKNOWN', description="This just means that a person was added via the user.")
    asset_person_deleted: Optional[StrictStr] = Field(default='UNKNOWN', description="This just means that a person was deleted via the user.")
    asset_sensitive_added: Optional[StrictStr] = Field(default='UNKNOWN', description="This just means that a sensitive was added via the user.")
    asset_sensitive_deleted: Optional[StrictStr] = Field(default='UNKNOWN', description="This just means that a sensitive was deleted via the user.")
    suggested_asset_referenced: Optional[StrictStr] = Field(default='UNKNOWN', description="This means that an asset was view/used while the user was looking at the suggestion view.")
    searched_asset_referenced: Optional[StrictStr] = Field(default='UNKNOWN', description="This means that an asset was view/used while the user was looking at the searching view.")
    asset_referenced: Optional[StrictStr] = Field(default='UNKNOWN', description="This means that an asset was view/used while the user was looking at the default view.")
    activity_asset_referenced: Optional[StrictStr] = Field(default='UNKNOWN', description="This means that a user referenced an asset by first clicking on an asset within an activity event.(ie from the activity view)")
    asset_annotation_added: Optional[StrictStr] = 'UNKNOWN'
    asset_annotation_deleted: Optional[StrictStr] = 'UNKNOWN'
    asset_annotation_updated: Optional[StrictStr] = 'UNKNOWN'
    asset_hint_added: Optional[StrictStr] = 'UNKNOWN'
    asset_hint_deleted: Optional[StrictStr] = 'UNKNOWN'
    asset_hint_updated: Optional[StrictStr] = 'UNKNOWN'
    asset_anchor_added: Optional[StrictStr] = 'UNKNOWN'
    asset_anchor_deleted: Optional[StrictStr] = 'UNKNOWN'
    asset_anchor_updated: Optional[StrictStr] = 'UNKNOWN'
    __properties = ["schema", "asset_created", "asset_viewed", "asset_format_copied", "asset_format_downloaded", "asset_deleted", "asset_description_updated", "asset_name_updated", "asset_format_generic_classification_updated", "asset_format_specific_classification_updated", "asset_creation_failed", "asset_tag_added", "asset_link_added", "asset_link_generated", "asset_link_deleted", "asset_tag_deleted", "asset_updated", "asset_format_value_edited", "asset_format_updated", "asset_link_revoked", "asset_person_added", "asset_person_deleted", "asset_sensitive_added", "asset_sensitive_deleted", "suggested_asset_referenced", "searched_asset_referenced", "asset_referenced", "activity_asset_referenced", "asset_annotation_added", "asset_annotation_deleted", "asset_annotation_updated", "asset_hint_added", "asset_hint_deleted", "asset_hint_updated", "asset_anchor_added", "asset_anchor_deleted", "asset_anchor_updated"]

    @validator('asset_created')
    def asset_created_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'an_asset_was_created',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'an_asset_was_created')")
        return value

    @validator('asset_viewed')
    def asset_viewed_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'an_asset_was_viewed',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'an_asset_was_viewed')")
        return value

    @validator('asset_format_copied')
    def asset_format_copied_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'an_asset_preview_format_was_copied',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'an_asset_preview_format_was_copied')")
        return value

    @validator('asset_format_downloaded')
    def asset_format_downloaded_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'an_asset_format_was_downloaded',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'an_asset_format_was_downloaded')")
        return value

    @validator('asset_deleted')
    def asset_deleted_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'an_asset_was_deleted',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'an_asset_was_deleted')")
        return value

    @validator('asset_description_updated')
    def asset_description_updated_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'an_asset_was_redescribed_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'an_asset_was_redescribed_by_the_user')")
        return value

    @validator('asset_name_updated')
    def asset_name_updated_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'an_asset_was_renamed_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'an_asset_was_renamed_by_the_user')")
        return value

    @validator('asset_format_generic_classification_updated')
    def asset_format_generic_classification_updated_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_generic_classification_was_changed_on_a_format_within_an_asset',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_generic_classification_was_changed_on_a_format_within_an_asset')")
        return value

    @validator('asset_format_specific_classification_updated')
    def asset_format_specific_classification_updated_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_specific_classification_was_changed_on_a_format_within_an_asset',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_specific_classification_was_changed_on_a_format_within_an_asset')")
        return value

    @validator('asset_creation_failed')
    def asset_creation_failed_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'an_asset_failed_to_be_created',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'an_asset_failed_to_be_created')")
        return value

    @validator('asset_tag_added')
    def asset_tag_added_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_tag_was_added_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_tag_was_added_by_the_user')")
        return value

    @validator('asset_link_added')
    def asset_link_added_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_link_was_added_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_link_was_added_by_the_user')")
        return value

    @validator('asset_link_generated')
    def asset_link_generated_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'an_asset_link_was_generated',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'an_asset_link_was_generated')")
        return value

    @validator('asset_link_deleted')
    def asset_link_deleted_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_link_was_deleted_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_link_was_deleted_by_the_user')")
        return value

    @validator('asset_tag_deleted')
    def asset_tag_deleted_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_tag_was_deleted_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_tag_was_deleted_by_the_user')")
        return value

    @validator('asset_updated')
    def asset_updated_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'an_asset_was_updated',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'an_asset_was_updated')")
        return value

    @validator('asset_format_value_edited')
    def asset_format_value_edited_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_specific_format_value_was_edited_on_an_asset',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_specific_format_value_was_edited_on_an_asset')")
        return value

    @validator('asset_format_updated')
    def asset_format_updated_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_specific_format_was_updated_on_an_asset',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_specific_format_was_updated_on_an_asset')")
        return value

    @validator('asset_link_revoked')
    def asset_link_revoked_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'an_asset_link_was_revoked',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'an_asset_link_was_revoked')")
        return value

    @validator('asset_person_added')
    def asset_person_added_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_person_was_added_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_person_was_added_by_the_user')")
        return value

    @validator('asset_person_deleted')
    def asset_person_deleted_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_person_was_deleted_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_person_was_deleted_by_the_user')")
        return value

    @validator('asset_sensitive_added')
    def asset_sensitive_added_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_sensitive_was_added_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_sensitive_was_added_by_the_user')")
        return value

    @validator('asset_sensitive_deleted')
    def asset_sensitive_deleted_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_sensitive_was_deleted_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_sensitive_was_deleted_by_the_user')")
        return value

    @validator('suggested_asset_referenced')
    def suggested_asset_referenced_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_suggested_asset_was_referenced_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_suggested_asset_was_referenced_by_the_user')")
        return value

    @validator('searched_asset_referenced')
    def searched_asset_referenced_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_searched_asset_was_referenced_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_searched_asset_was_referenced_by_the_user')")
        return value

    @validator('asset_referenced')
    def asset_referenced_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'an_asset_was_referenced_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'an_asset_was_referenced_by_the_user')")
        return value

    @validator('activity_asset_referenced')
    def activity_asset_referenced_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'an_activity_asset_was_referenced_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'an_activity_asset_was_referenced_by_the_user')")
        return value

    @validator('asset_annotation_added')
    def asset_annotation_added_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'an_annotation_was_added_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'an_annotation_was_added_by_the_user')")
        return value

    @validator('asset_annotation_deleted')
    def asset_annotation_deleted_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'an_annotation_was_deleted_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'an_annotation_was_deleted_by_the_user')")
        return value

    @validator('asset_annotation_updated')
    def asset_annotation_updated_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'an_annotation_was_updated_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'an_annotation_was_updated_by_the_user')")
        return value

    @validator('asset_hint_added')
    def asset_hint_added_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_hint_was_added_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_hint_was_added_by_the_user')")
        return value

    @validator('asset_hint_deleted')
    def asset_hint_deleted_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_hint_was_deleted_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_hint_was_deleted_by_the_user')")
        return value

    @validator('asset_hint_updated')
    def asset_hint_updated_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_hint_was_updated_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_hint_was_updated_by_the_user')")
        return value

    @validator('asset_anchor_added')
    def asset_anchor_added_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_anchor_was_added_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_anchor_was_added_by_the_user')")
        return value

    @validator('asset_anchor_deleted')
    def asset_anchor_deleted_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_anchor_was_deleted_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_anchor_was_deleted_by_the_user')")
        return value

    @validator('asset_anchor_updated')
    def asset_anchor_updated_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in ('UNKNOWN', 'a_anchor_was_updated_by_the_user',):
            raise ValueError("must be one of enum values ('UNKNOWN', 'a_anchor_was_updated_by_the_user')")
        return value

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
    def from_json(cls, json_str: str) -> TrackedAssetEventIdentifierDescriptionPairs:
        """Create an instance of TrackedAssetEventIdentifierDescriptionPairs from a JSON string"""
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
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> TrackedAssetEventIdentifierDescriptionPairs:
        """Create an instance of TrackedAssetEventIdentifierDescriptionPairs from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return TrackedAssetEventIdentifierDescriptionPairs.parse_obj(obj)

        _obj = TrackedAssetEventIdentifierDescriptionPairs.parse_obj({
            "var_schema": EmbeddedModelSchema.from_dict(obj.get("schema")) if obj.get("schema") is not None else None,
            "asset_created": obj.get("asset_created") if obj.get("asset_created") is not None else 'UNKNOWN',
            "asset_viewed": obj.get("asset_viewed") if obj.get("asset_viewed") is not None else 'UNKNOWN',
            "asset_format_copied": obj.get("asset_format_copied") if obj.get("asset_format_copied") is not None else 'UNKNOWN',
            "asset_format_downloaded": obj.get("asset_format_downloaded") if obj.get("asset_format_downloaded") is not None else 'UNKNOWN',
            "asset_deleted": obj.get("asset_deleted") if obj.get("asset_deleted") is not None else 'UNKNOWN',
            "asset_description_updated": obj.get("asset_description_updated") if obj.get("asset_description_updated") is not None else 'UNKNOWN',
            "asset_name_updated": obj.get("asset_name_updated") if obj.get("asset_name_updated") is not None else 'UNKNOWN',
            "asset_format_generic_classification_updated": obj.get("asset_format_generic_classification_updated") if obj.get("asset_format_generic_classification_updated") is not None else 'UNKNOWN',
            "asset_format_specific_classification_updated": obj.get("asset_format_specific_classification_updated") if obj.get("asset_format_specific_classification_updated") is not None else 'UNKNOWN',
            "asset_creation_failed": obj.get("asset_creation_failed") if obj.get("asset_creation_failed") is not None else 'UNKNOWN',
            "asset_tag_added": obj.get("asset_tag_added") if obj.get("asset_tag_added") is not None else 'UNKNOWN',
            "asset_link_added": obj.get("asset_link_added") if obj.get("asset_link_added") is not None else 'UNKNOWN',
            "asset_link_generated": obj.get("asset_link_generated") if obj.get("asset_link_generated") is not None else 'UNKNOWN',
            "asset_link_deleted": obj.get("asset_link_deleted") if obj.get("asset_link_deleted") is not None else 'UNKNOWN',
            "asset_tag_deleted": obj.get("asset_tag_deleted") if obj.get("asset_tag_deleted") is not None else 'UNKNOWN',
            "asset_updated": obj.get("asset_updated") if obj.get("asset_updated") is not None else 'UNKNOWN',
            "asset_format_value_edited": obj.get("asset_format_value_edited") if obj.get("asset_format_value_edited") is not None else 'UNKNOWN',
            "asset_format_updated": obj.get("asset_format_updated") if obj.get("asset_format_updated") is not None else 'UNKNOWN',
            "asset_link_revoked": obj.get("asset_link_revoked") if obj.get("asset_link_revoked") is not None else 'UNKNOWN',
            "asset_person_added": obj.get("asset_person_added") if obj.get("asset_person_added") is not None else 'UNKNOWN',
            "asset_person_deleted": obj.get("asset_person_deleted") if obj.get("asset_person_deleted") is not None else 'UNKNOWN',
            "asset_sensitive_added": obj.get("asset_sensitive_added") if obj.get("asset_sensitive_added") is not None else 'UNKNOWN',
            "asset_sensitive_deleted": obj.get("asset_sensitive_deleted") if obj.get("asset_sensitive_deleted") is not None else 'UNKNOWN',
            "suggested_asset_referenced": obj.get("suggested_asset_referenced") if obj.get("suggested_asset_referenced") is not None else 'UNKNOWN',
            "searched_asset_referenced": obj.get("searched_asset_referenced") if obj.get("searched_asset_referenced") is not None else 'UNKNOWN',
            "asset_referenced": obj.get("asset_referenced") if obj.get("asset_referenced") is not None else 'UNKNOWN',
            "activity_asset_referenced": obj.get("activity_asset_referenced") if obj.get("activity_asset_referenced") is not None else 'UNKNOWN',
            "asset_annotation_added": obj.get("asset_annotation_added") if obj.get("asset_annotation_added") is not None else 'UNKNOWN',
            "asset_annotation_deleted": obj.get("asset_annotation_deleted") if obj.get("asset_annotation_deleted") is not None else 'UNKNOWN',
            "asset_annotation_updated": obj.get("asset_annotation_updated") if obj.get("asset_annotation_updated") is not None else 'UNKNOWN',
            "asset_hint_added": obj.get("asset_hint_added") if obj.get("asset_hint_added") is not None else 'UNKNOWN',
            "asset_hint_deleted": obj.get("asset_hint_deleted") if obj.get("asset_hint_deleted") is not None else 'UNKNOWN',
            "asset_hint_updated": obj.get("asset_hint_updated") if obj.get("asset_hint_updated") is not None else 'UNKNOWN',
            "asset_anchor_added": obj.get("asset_anchor_added") if obj.get("asset_anchor_added") is not None else 'UNKNOWN',
            "asset_anchor_deleted": obj.get("asset_anchor_deleted") if obj.get("asset_anchor_deleted") is not None else 'UNKNOWN',
            "asset_anchor_updated": obj.get("asset_anchor_updated") if obj.get("asset_anchor_updated") is not None else 'UNKNOWN'
        })
        return _obj


