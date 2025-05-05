import datetime
from typing import TYPE_CHECKING, Optional, List


if TYPE_CHECKING:
    from . import PiecesClient
    from pieces_os_client.models.workstream_pattern_engine_vision_calibration import (
        WorkstreamPatternEngineVisionCalibration,
    )
    from pieces_os_client.models.workstream_pattern_engine_status import (
        WorkstreamPatternEngineStatus,
    )


QR_CODE_BASE_64 = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyBAMAAADsEZWCAAAAKlBMVEUAAAD///+pqan7+/v+/v4QEBDu7u5WVlazs7NOTk5xcXEtLS3g4OCOjo5qPpGPAAAA0klEQVQ4y2NgGIZghZKSxgIgHaQEAV1wmUZBQcEGIB0iCAEScBlFY2NDBSAdJmwMBkIIGUNBiIwIWIswhTJI9pigyADdJgJyGzNIhyOyDMg/N8vLy4uAftERQZYBgYlA5QZAmkkYXaYQaFcqdhlDQUcqypi44JIBug27zJS0tLTToaGhHBgyrEDRPUDZZEF0GRAIE0QPUbiMiIuLIw4Z3HrIkxFBSSHIMo4oqQpJRkR2enl5NTYZYUmsqRgkI04PGWBKxC4DyiXYZZiAKbGbYZgCALuBN/D7PkRzAAAAAElFTkSuQmCC"""
QR_CODE_HIEGHT = 50
QR_CODE_WIDTH = 50


class LongTermMemory:
    ltm_status: Optional["WorkstreamPatternEngineStatus"] = None

    def __init__(self, pieces_client: "PiecesClient"):
        self.pieces_client = pieces_client

    @property
    def is_enabled(self) -> bool:
        """Checks if the LTM is enabled

        Returns:
            bool: Whether the LTM is enabled
        """
        if self.ltm_status:
            return (
                self.ltm_status.vision.activation is not None
                if self.ltm_status.vision is not None
                else False
            )  # checking the activation status
        return False

    def enable(self, show_message=False):
        """
        This will activate the long term memory (LTM)
        It blocks the main thread until the LTM is enabled and all permissions are enabled
        use PiecesClient.pool to run it in separate thread

        Args:
            show_message (bool, optional): Defaults to False.
            it show_message is True it will ask the user to enable the permissions if it is not
        Raises:
            PermissionError: If LTM permissions is not enabled
        """
        from pieces_os_client.models.anonymous_temporal_range import (
            AnonymousTemporalRange,
        )
        from pieces_os_client.models.os_permissions import OSPermissions
        from pieces_os_client.models.os_processing_permissions import (
            OSProcessingPermissions,
        )
        from pieces_os_client.models.workstream_pattern_engine_status import (
            WorkstreamPatternEngineStatus,
        )
        from pieces_os_client.models.workstream_pattern_engine_vision_status import (
            WorkstreamPatternEngineVisionStatus,
        )
        import urllib3

        if self.is_enabled:
            return

        missing_permissions = []
        missing_permissions = self.check_perms()
        if missing_permissions and show_message:
            try:
                self.pieces_client.os_api.os_permissions_request(
                    os_permissions=OSPermissions(
                        processing=OSProcessingPermissions(
                            **{perm: True for perm in missing_permissions}
                        )
                    ),
                    _request_timeout=7,
                )
            except urllib3.exceptions.TimeoutError:
                pass

            missing_permissions = self.check_perms()

        if missing_permissions:
            raise PermissionError(
                f"{', '.join(missing_permissions).capitalize()} is not enabled yet"
            )

        state = WorkstreamPatternEngineStatus(
            vision=WorkstreamPatternEngineVisionStatus(
                activation=AnonymousTemporalRange(continuous=True)
            )
        )
        self.pieces_client.work_stream_pattern_engine_api.workstream_pattern_engine_processors_vision_activate(
            state
        )

    def check_perms(self) -> List[str]:
        missing_permissions = []
        out = self.pieces_client.os_api.os_permissions()

        if out.processing:
            if not out.processing.vision:
                missing_permissions.append("vision")
            if not out.processing.accessibility:
                missing_permissions.append("accessibility")
        return missing_permissions

    def pause(self, until: Optional[datetime.datetime] = None):
        """
        This will pause the long term memory (LTM)

        Args:
            until (Optional[datetime.datetime], optional): Until when the LTM will be paused. Defaults to None (Until tunned back on).
        """
        from pieces_os_client.models.anonymous_temporal_range import (
            AnonymousTemporalRange,
        )
        from pieces_os_client.models.grouped_timestamp import GroupedTimestamp
        from pieces_os_client.models.workstream_pattern_engine_status import (
            WorkstreamPatternEngineStatus,
        )
        from pieces_os_client.models.workstream_pattern_engine_vision_status import (
            WorkstreamPatternEngineVisionStatus,
        )

        if until:
            workstream_pattern_engine_status = WorkstreamPatternEngineStatus(
                vision=WorkstreamPatternEngineVisionStatus(
                    deactivation=AnonymousTemporalRange(
                        to=GroupedTimestamp(
                            value=until,
                        )
                    ),
                )
            )
        else:
            workstream_pattern_engine_status = WorkstreamPatternEngineStatus(
                vision=WorkstreamPatternEngineVisionStatus(
                    deactivation=AnonymousTemporalRange(continuous=True),
                )
            )
        self.pieces_client.work_stream_pattern_engine_api.workstream_pattern_engine_processors_vision_deactivate(
            workstream_pattern_engine_status
        )

    def get_qrcode(self) -> str:
        """
        This will return the qrcode that needs to be placed on the corner of the Copilot window to avoid multiple capture context capture

        If you want to download the image it self you can run the following script

        ```python
        image_data = base64.b64decode(ltm.get_qrcode())
        output_file_path = "qrcode.png"
        with open(output_file_path, "wb") as file:
            file.write(image_data)
        ```

        Returns:
            str: The qrcode png image base64
        """
        return QR_CODE_BASE_64

    def capture(self) -> "WorkstreamPatternEngineVisionCalibration":
        """
        This will capture the qrcode that you got from `get_qrcode` for the LTM engine to ignore the window to avoid multiple context captures
        that will enhance the LTM quality

        Returns:
            WorkstreamPatternEngineVisionCalibration: The Captured window details
        """
        return self.pieces_client.work_stream_pattern_engine_api.workstream_pattern_engine_processors_vision_calibration_capture()
