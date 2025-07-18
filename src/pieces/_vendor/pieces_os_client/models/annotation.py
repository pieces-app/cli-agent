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
from pydantic.v1 import BaseModel, Field, StrictBool, StrictStr
from pieces._vendor.pieces_os_client.models.annotation_type_enum import AnnotationTypeEnum
from pieces._vendor.pieces_os_client.models.embedded_model_schema import EmbeddedModelSchema
from pieces._vendor.pieces_os_client.models.flattened_anchors import FlattenedAnchors
from pieces._vendor.pieces_os_client.models.flattened_assets import FlattenedAssets
from pieces._vendor.pieces_os_client.models.flattened_conversation_messages import FlattenedConversationMessages
from pieces._vendor.pieces_os_client.models.flattened_conversations import FlattenedConversations
from pieces._vendor.pieces_os_client.models.flattened_persons import FlattenedPersons
from pieces._vendor.pieces_os_client.models.flattened_tags import FlattenedTags
from pieces._vendor.pieces_os_client.models.flattened_websites import FlattenedWebsites
from pieces._vendor.pieces_os_client.models.flattened_workstream_events import FlattenedWorkstreamEvents
from pieces._vendor.pieces_os_client.models.flattened_workstream_summaries import FlattenedWorkstreamSummaries
from pieces._vendor.pieces_os_client.models.grouped_timestamp import GroupedTimestamp
from pieces._vendor.pieces_os_client.models.mechanism_enum import MechanismEnum
from pieces._vendor.pieces_os_client.models.referenced_anchor import ReferencedAnchor
from pieces._vendor.pieces_os_client.models.referenced_asset import ReferencedAsset
from pieces._vendor.pieces_os_client.models.referenced_conversation import ReferencedConversation
from pieces._vendor.pieces_os_client.models.referenced_model import ReferencedModel
from pieces._vendor.pieces_os_client.models.referenced_person import ReferencedPerson
from pieces._vendor.pieces_os_client.models.referenced_workstream_summary import ReferencedWorkstreamSummary
from pieces._vendor.pieces_os_client.models.score import Score

class Annotation(BaseModel):
    """
    An Annotation is the replacement for descriptions, this will enable comments, description, summaries and many more.  person on here is a reference to the description/comment/annotation about a person  NOTE: person here is NOT the creator of the annotaion. but rather the descriptions of the person. NOTE****: if we want to add \"who\" wrote the annotation, we will want to add a new field on here called author && will need to also layer in behavior the enable an author(person) and an asset both being referenced(ensure you check the side effect in the AssetsFacade.delete)  UPDATE: the singular fields on here(asset, person, anchor, conversation, and summary) are all now deprecated... an annotation will now have a many to many relationship with all of it materials.  # noqa: E501
    """
    var_schema: Optional[EmbeddedModelSchema] = Field(default=None, alias="schema")
    id: StrictStr = Field(...)
    created: GroupedTimestamp = Field(...)
    updated: GroupedTimestamp = Field(...)
    deleted: Optional[GroupedTimestamp] = None
    mechanism: Optional[MechanismEnum] = None
    asset: Optional[ReferencedAsset] = None
    person: Optional[ReferencedPerson] = None
    type: AnnotationTypeEnum = Field(...)
    text: StrictStr = Field(default=..., description="This is the text of the annotation.")
    model: Optional[ReferencedModel] = None
    pseudo: Optional[StrictBool] = None
    favorited: Optional[StrictBool] = None
    anchor: Optional[ReferencedAnchor] = None
    conversation: Optional[ReferencedConversation] = None
    score: Optional[Score] = None
    messages: Optional[FlattenedConversationMessages] = None
    summary: Optional[ReferencedWorkstreamSummary] = None
    assets: Optional[FlattenedAssets] = None
    persons: Optional[FlattenedPersons] = None
    anchors: Optional[FlattenedAnchors] = None
    conversations: Optional[FlattenedConversations] = None
    summaries: Optional[FlattenedWorkstreamSummaries] = None
    websites: Optional[FlattenedWebsites] = None
    tags: Optional[FlattenedTags] = None
    workstream_events: Optional[FlattenedWorkstreamEvents] = None
    __properties = ["schema", "id", "created", "updated", "deleted", "mechanism", "asset", "person", "type", "text", "model", "pseudo", "favorited", "anchor", "conversation", "score", "messages", "summary", "assets", "persons", "anchors", "conversations", "summaries", "websites", "tags", "workstream_events"]

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
    def from_json(cls, json_str: str) -> Annotation:
        """Create an instance of Annotation from a JSON string"""
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
        # override the default output from pydantic.v1 by calling `to_dict()` of created
        if self.created:
            _dict['created'] = self.created.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of updated
        if self.updated:
            _dict['updated'] = self.updated.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of deleted
        if self.deleted:
            _dict['deleted'] = self.deleted.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of asset
        if self.asset:
            _dict['asset'] = self.asset.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of person
        if self.person:
            _dict['person'] = self.person.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of model
        if self.model:
            _dict['model'] = self.model.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of anchor
        if self.anchor:
            _dict['anchor'] = self.anchor.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of conversation
        if self.conversation:
            _dict['conversation'] = self.conversation.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of score
        if self.score:
            _dict['score'] = self.score.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of messages
        if self.messages:
            _dict['messages'] = self.messages.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of summary
        if self.summary:
            _dict['summary'] = self.summary.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of assets
        if self.assets:
            _dict['assets'] = self.assets.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of persons
        if self.persons:
            _dict['persons'] = self.persons.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of anchors
        if self.anchors:
            _dict['anchors'] = self.anchors.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of conversations
        if self.conversations:
            _dict['conversations'] = self.conversations.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of summaries
        if self.summaries:
            _dict['summaries'] = self.summaries.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of websites
        if self.websites:
            _dict['websites'] = self.websites.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of tags
        if self.tags:
            _dict['tags'] = self.tags.to_dict()
        # override the default output from pydantic.v1 by calling `to_dict()` of workstream_events
        if self.workstream_events:
            _dict['workstream_events'] = self.workstream_events.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> Annotation:
        """Create an instance of Annotation from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return Annotation.parse_obj(obj)

        _obj = Annotation.parse_obj({
            "var_schema": EmbeddedModelSchema.from_dict(obj.get("schema")) if obj.get("schema") is not None else None,
            "id": obj.get("id"),
            "created": GroupedTimestamp.from_dict(obj.get("created")) if obj.get("created") is not None else None,
            "updated": GroupedTimestamp.from_dict(obj.get("updated")) if obj.get("updated") is not None else None,
            "deleted": GroupedTimestamp.from_dict(obj.get("deleted")) if obj.get("deleted") is not None else None,
            "mechanism": obj.get("mechanism"),
            "asset": ReferencedAsset.from_dict(obj.get("asset")) if obj.get("asset") is not None else None,
            "person": ReferencedPerson.from_dict(obj.get("person")) if obj.get("person") is not None else None,
            "type": obj.get("type"),
            "text": obj.get("text"),
            "model": ReferencedModel.from_dict(obj.get("model")) if obj.get("model") is not None else None,
            "pseudo": obj.get("pseudo"),
            "favorited": obj.get("favorited"),
            "anchor": ReferencedAnchor.from_dict(obj.get("anchor")) if obj.get("anchor") is not None else None,
            "conversation": ReferencedConversation.from_dict(obj.get("conversation")) if obj.get("conversation") is not None else None,
            "score": Score.from_dict(obj.get("score")) if obj.get("score") is not None else None,
            "messages": FlattenedConversationMessages.from_dict(obj.get("messages")) if obj.get("messages") is not None else None,
            "summary": ReferencedWorkstreamSummary.from_dict(obj.get("summary")) if obj.get("summary") is not None else None,
            "assets": FlattenedAssets.from_dict(obj.get("assets")) if obj.get("assets") is not None else None,
            "persons": FlattenedPersons.from_dict(obj.get("persons")) if obj.get("persons") is not None else None,
            "anchors": FlattenedAnchors.from_dict(obj.get("anchors")) if obj.get("anchors") is not None else None,
            "conversations": FlattenedConversations.from_dict(obj.get("conversations")) if obj.get("conversations") is not None else None,
            "summaries": FlattenedWorkstreamSummaries.from_dict(obj.get("summaries")) if obj.get("summaries") is not None else None,
            "websites": FlattenedWebsites.from_dict(obj.get("websites")) if obj.get("websites") is not None else None,
            "tags": FlattenedTags.from_dict(obj.get("tags")) if obj.get("tags") is not None else None,
            "workstream_events": FlattenedWorkstreamEvents.from_dict(obj.get("workstream_events")) if obj.get("workstream_events") is not None else None
        })
        return _obj


