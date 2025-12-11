import pytest
from unittest.mock import Mock, patch
from pieces.command_interface.auth_commands import LoginCommand, LogoutCommand
from pieces.settings import Settings
from pieces._vendor.pieces_os_client.models.allocation_status_enum import (
    AllocationStatusEnum,
)
from pieces._vendor.pieces_os_client.models.user_profile import UserProfile


class TestLoginCommand:
    """Comprehensive tests for the LoginCommand class."""

    @pytest.fixture
    def login_command(self):
        """Create a LoginCommand instance for testing."""
        return LoginCommand()

    @pytest.fixture
    def mock_user_profile(self):
        """Create a mock user profile."""
        profile = Mock(spec=UserProfile)
        profile.name = "Test User"
        profile.email = "test@example.com"
        profile.id = "test_user_id"
        profile.vanityname = "testuser"
        return profile

    def test_get_name(self, login_command):
        """Test that the command name is correctly set."""
        assert login_command.get_name() == "login"

    def test_get_help(self, login_command):
        """Test that help text is returned."""
        help_text = login_command.get_help()
        assert isinstance(help_text, str)
        assert "Sign into PiecesOS" in help_text

    def test_get_description(self, login_command):
        """Test that description is returned."""
        description = login_command.get_description()
        assert isinstance(description, str)
        assert "Authenticate" in description

    def test_get_docs(self, login_command):
        """Test that docs URL is returned."""
        docs = login_command.get_docs()
        assert isinstance(docs, str)
        assert len(docs) > 0

    def test_add_arguments(self, login_command):
        """Test that add_arguments doesn't raise an error."""
        mock_parser = Mock()
        login_command.add_arguments(mock_parser)
        # Should not raise any exceptions

    @patch.object(Settings, "logger")
    @patch.object(Settings, "pieces_client")
    def test_execute_logged_in_but_disconnected(
        self, mock_pieces_client, mock_logger, login_command, mock_user_profile
    ):
        """Test login when user is logged in but disconnected from cloud."""
        # Setup: User is logged in but disconnected
        mock_user = Mock()
        mock_user.user_profile = mock_user_profile
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        mock_user.cloud_status = AllocationStatusEnum.DISCONNECTED

        mock_pieces_client.user = mock_user
        mock_pieces_client.user_api.user_snapshot.return_value.user = mock_user_profile

        # Execute
        result = login_command.execute()

        # Assert
        assert result == 0
        assert mock_logger.print.call_count == 2
        mock_user.connect.assert_called_once()

        # Verify the messages
        first_call_args = mock_logger.print.call_args_list[0][0][0]
        assert "Test User" in first_call_args
        assert "Disconnected" in first_call_args

        second_call_args = mock_logger.print.call_args_list[1][0][0]
        assert "Connecting to the Pieces Cloud" in second_call_args

    @patch.object(Settings, "logger")
    @patch.object(Settings, "pieces_client")
    def test_execute_not_logged_in(
        self, mock_pieces_client, mock_logger, login_command
    ):
        """Test login when user is not logged in."""
        # Setup: User is not logged in
        mock_user = Mock()
        mock_user.user_profile = None
        mock_user.login = Mock()

        mock_pieces_client.user = mock_user
        mock_pieces_client.user_api.user_snapshot.return_value.user = None

        # Execute
        result = login_command.execute()

        # Assert
        assert result == 0
        mock_user.login.assert_called_once_with(True)

    @patch.object(Settings, "logger")
    @patch.object(Settings, "pieces_client")
    def test_execute_login_exception(
        self, mock_pieces_client, mock_logger, login_command
    ):
        """Test login when an exception occurs during login."""
        # Setup: Login raises an exception
        mock_user = Mock()
        mock_user.user_profile = None
        mock_user.login = Mock(side_effect=RuntimeError("Connection error"))

        mock_pieces_client.user = mock_user
        mock_pieces_client.user_api.user_snapshot.return_value.user = None

        # Execute
        result = login_command.execute()

        # Assert
        assert result == 0
        mock_user.login.assert_called_once_with(True)
        mock_logger.error.assert_called_once()
        error_message = mock_logger.error.call_args[0][0]
        assert "Sign in failed" in error_message
        assert "Connection error" in error_message

    @patch.object(Settings, "logger")
    @patch.object(Settings, "pieces_client")
    def test_execute_user_snapshot_exception(
        self, mock_pieces_client, mock_logger, login_command
    ):
        """Test login when user_snapshot raises an exception."""
        # Setup: user_snapshot raises an exception
        mock_user = Mock()
        mock_user.user_profile = None
        mock_pieces_client.user = mock_user
        mock_pieces_client.user_api.user_snapshot.side_effect = ConnectionError(
            "Failed to fetch user snapshot"
        )

        # Execute and expect exception to propagate
        with pytest.raises(ConnectionError):
            login_command.execute()

    @patch.object(Settings, "logger")
    @patch.object(Settings, "pieces_client")
    def test_execute_connect_exception(
        self, mock_pieces_client, mock_logger, login_command, mock_user_profile
    ):
        """Test login when connect operation fails."""
        # Setup: User is disconnected and connect raises exception
        mock_user = Mock()
        mock_user.user_profile = mock_user_profile
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        mock_user.cloud_status = AllocationStatusEnum.DISCONNECTED
        mock_user.connect.side_effect = RuntimeError("Cloud connection failed")

        mock_pieces_client.user = mock_user
        mock_pieces_client.user_api.user_snapshot.return_value.user = mock_user_profile

        # Execute and expect exception to propagate
        with pytest.raises(RuntimeError, match="Cloud connection failed"):
            login_command.execute()


class TestLogoutCommand:
    """Comprehensive tests for the LogoutCommand class."""

    @pytest.fixture
    def logout_command(self):
        """Create a LogoutCommand instance for testing."""
        return LogoutCommand()

    def test_get_name(self, logout_command):
        """Test that the command name is correctly set."""
        assert logout_command.get_name() == "logout"

    def test_get_help(self, logout_command):
        """Test that help text is returned."""
        help_text = logout_command.get_help()
        assert isinstance(help_text, str)
        assert "Sign out from PiecesOS" in help_text

    def test_get_description(self, logout_command):
        """Test that description is returned."""
        description = logout_command.get_description()
        assert isinstance(description, str)
        assert "Sign out" in description

    def test_get_docs(self, logout_command):
        """Test that docs URL is returned."""
        docs = logout_command.get_docs()
        assert isinstance(docs, str)
        assert len(docs) > 0

    def test_add_arguments(self, logout_command):
        """Test that add_arguments doesn't raise an error."""
        mock_parser = Mock()
        logout_command.add_arguments(mock_parser)
        # Should not raise any exceptions

    @patch.object(Settings, "logger")
    @patch.object(Settings, "pieces_client")
    def test_execute_successful_logout(
        self, mock_pieces_client, mock_logger, logout_command
    ):
        """Test successful logout operation."""
        # Setup
        mock_user = Mock()
        mock_user.logout = Mock()
        mock_pieces_client.user = mock_user

        # Execute
        result = logout_command.execute()

        # Assert
        assert result == 0
        mock_user.logout.assert_called_once()
        mock_logger.error.assert_not_called()

    @patch.object(Settings, "logger")
    @patch.object(Settings, "pieces_client")
    def test_execute_logout_with_connection_error(
        self, mock_pieces_client, mock_logger, logout_command
    ):
        """Test logout when a connection error occurs."""
        # Setup: Logout raises a connection error
        mock_user = Mock()
        mock_user.logout = Mock(side_effect=ConnectionError("Network error"))
        mock_pieces_client.user = mock_user

        # Execute
        result = logout_command.execute()

        # Assert
        assert result == 0
        mock_user.logout.assert_called_once()
        mock_logger.error.assert_called_once()
        error_message = mock_logger.error.call_args[0][0]
        assert "Sign out failed" in error_message
        assert "Network error" in error_message

    @patch.object(Settings, "logger")
    @patch.object(Settings, "pieces_client")
    def test_execute_logout_with_runtime_error(
        self, mock_pieces_client, mock_logger, logout_command
    ):
        """Test logout when a runtime error occurs."""
        # Setup: Logout raises a runtime error
        mock_user = Mock()
        mock_user.logout = Mock(side_effect=RuntimeError("Unexpected error"))
        mock_pieces_client.user = mock_user

        # Execute
        result = logout_command.execute()

        # Assert
        assert result == 0
        mock_user.logout.assert_called_once()
        mock_logger.error.assert_called_once()
        error_message = mock_logger.error.call_args[0][0]
        assert "Sign out failed" in error_message
        assert "Unexpected error" in error_message

    @patch.object(Settings, "logger")
    @patch.object(Settings, "pieces_client")
    def test_execute_logout_with_permission_error(
        self, mock_pieces_client, mock_logger, logout_command
    ):
        """Test logout when a permission error occurs."""
        # Setup: Logout raises a permission error
        mock_user = Mock()
        mock_user.logout = Mock(side_effect=PermissionError("Access denied"))
        mock_pieces_client.user = mock_user

        # Execute
        result = logout_command.execute()

        # Assert
        assert result == 0
        mock_user.logout.assert_called_once()
        mock_logger.error.assert_called_once()
        error_message = mock_logger.error.call_args[0][0]
        assert "Sign out failed" in error_message
        assert "Access denied" in error_message

    @patch.object(Settings, "logger")
    @patch.object(Settings, "pieces_client")
    def test_execute_multiple_logout_calls(
        self, mock_pieces_client, mock_logger, logout_command
    ):
        """Test multiple logout calls in succession."""
        # Setup
        mock_user = Mock()
        mock_user.logout = Mock()
        mock_pieces_client.user = mock_user

        # Execute multiple times
        result1 = logout_command.execute()
        result2 = logout_command.execute()
        result3 = logout_command.execute()

        # Assert
        assert result1 == 0
        assert result2 == 0
        assert result3 == 0
        assert mock_user.logout.call_count == 3
        mock_logger.error.assert_not_called()


class TestLoginLogoutIntegration:
    """Integration tests for login and logout commands working together."""

    @pytest.fixture
    def login_command(self):
        return LoginCommand()

    @pytest.fixture
    def logout_command(self):
        return LogoutCommand()

    @pytest.fixture
    def mock_user_profile(self):
        """Create a mock user profile."""
        profile = Mock(spec=UserProfile)
        profile.name = "Integration Test User"
        profile.email = "integration@example.com"
        profile.id = "integration_user_id"
        profile.vanityname = "integrationuser"
        return profile

    @patch.object(Settings, "logger")
    @patch.object(Settings, "pieces_client")
    def test_login_then_logout_workflow(
        self,
        mock_pieces_client,
        mock_logger,
        login_command,
        logout_command,
        mock_user_profile,
    ):
        """Test a complete login and logout workflow."""
        # Setup
        mock_user = Mock()
        mock_pieces_client.user = mock_user

        # Simulate login
        mock_user.user_profile = mock_user_profile
        mock_user.name = "Integration Test User"
        mock_user.email = "integration@example.com"
        mock_user.cloud_status = AllocationStatusEnum.RUNNING
        mock_pieces_client.user_api.user_snapshot.return_value.user = mock_user_profile

        # Execute login
        login_result = login_command.execute()
        assert login_result == 0

        # Setup for logout
        mock_user.logout = Mock()

        # Execute logout
        logout_result = logout_command.execute()
        assert logout_result == 0

        # Verify both operations completed successfully
        mock_logger.print.assert_called()
        mock_user.logout.assert_called_once()

    @patch.object(Settings, "logger")
    @patch.object(Settings, "pieces_client")
    def test_logout_without_login(
        self, mock_pieces_client, mock_logger, logout_command
    ):
        """Test logout when user was never logged in."""
        # Setup: User is not logged in
        mock_user = Mock()
        mock_user.logout = Mock()
        mock_pieces_client.user = mock_user

        # Execute logout (should still succeed)
        result = logout_command.execute()

        # Assert
        assert result == 0
        mock_user.logout.assert_called_once()
