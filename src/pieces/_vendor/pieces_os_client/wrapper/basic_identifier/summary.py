from pieces._vendor.pieces_os_client.wrapper.basic_identifier.basic import Basic
from pieces._vendor.pieces_os_client.wrapper.basic_identifier.annotation import (
    BasicAnnotation,
)
from typing import TYPE_CHECKING, List, Optional

from pieces._vendor.pieces_os_client.wrapper.streamed_identifiers.workstream_summary_snapshot import (
    WorkstreamSummarySnapshot,
)

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.workstream_summary import (
        WorkstreamSummary,
    )


class BasicSummary(Basic):
    """
    A class to represent a summary of basic identifiers.
    This class is used to store and manage basic identifier summaries.
    """

    @property
    def id(self) -> str:
        return self.summary.id

    @property
    def summary(self) -> "WorkstreamSummary":
        summary = WorkstreamSummarySnapshot.identifiers_snapshot.get(self.id)
        if not summary:
            raise ValueError(f"Summary with id {self.id} not found.")
        return summary

    @property
    def content_annotation(self) -> Optional[BasicAnnotation]:
        if self.summary.annotations and self.summary.annotations.indices:
            annotations: List[BasicAnnotation] = self._from_indices(
                self.summary.annotations.indices,
                lambda id: BasicAnnotation.from_id(
                    WorkstreamSummarySnapshot.pieces_client, id
                ),
            )
            for annotation in annotations:
                if annotation.type == "SUMMARY":
                    return annotation

    @property
    def raw_content(self) -> str:
        """
        Get the raw content of the summary.

        Returns:
            str: The raw content of the summary.
        """
        return self.content_annotation.raw_content if self.content_annotation else ""

    @raw_content.setter
    def raw_content(self, value: str):
        if self.content_annotation:
            self.content_annotation.raw_content = value
        else:
            raise ValueError("No content annotation found to set raw content.")

    @raw_content.setter
    def raw_content(self, value: str):
        self.raw_content = value

    @property
    def name(self) -> str:
        """
        Get the name of the summary.

        Returns:
            str: The name of the summary.
        """
        return self.summary.name

    def delete(self) -> None:
        """
        Delete the summary.
        """
        WorkstreamSummarySnapshot.pieces_client.workstream_summaries_api.workstream_summaries_delete_specific_workstream_summary(
            self.id
        )
