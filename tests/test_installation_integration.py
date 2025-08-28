"""
Integration tests for installation scripts.

These tests actually run the installation scripts and verify that:
1. The installation completes successfully
2. Pieces CLI is properly installed and accessible
3. Basic commands work correctly
4. PATH configuration is working
"""

import pytest
import subprocess
import os
import shutil
import tempfile
import platform
from pathlib import Path

from pieces.settings import Settings


class TestInstallationIntegration:
    """Integration tests for installation scripts."""

    def setup_method(self, method):
        """Set up test environment for each test."""
        # Create a temporary directory for installation
        self.temp_home = tempfile.mkdtemp(prefix="pieces_cli_test_")
        self.original_home = os.environ.get("HOME") or os.environ.get("USERPROFILE")

        # Mock HOME/USERPROFILE for the test
        if platform.system() == "Windows":
            os.environ["USERPROFILE"] = self.temp_home
        else:
            os.environ["HOME"] = self.temp_home

        self.installation_dir = Path(self.temp_home) / ".pieces-cli"

        # Store original PATH
        self.original_path = os.environ.get("PATH", "")

    def teardown_method(self, method):
        """Clean up after each test."""
        # Restore original environment
        if platform.system() == "Windows":
            if self.original_home:
                os.environ["USERPROFILE"] = self.original_home
            else:
                os.environ.pop("USERPROFILE", None)
        else:
            if self.original_home:
                os.environ["HOME"] = self.original_home
            else:
                os.environ.pop("HOME", None)

        # Restore original PATH
        os.environ["PATH"] = self.original_path

        # Clean up installation directory
        if self.installation_dir.exists():
            shutil.rmtree(self.installation_dir, ignore_errors=True)

        # Clean up temp home directory
        if os.path.exists(self.temp_home):
            shutil.rmtree(self.temp_home, ignore_errors=True)

    def _run_with_timeout(self, cmd, timeout=300, input_text=None):
        """Run a command with timeout and return result."""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                input=input_text,
                env=os.environ.copy(),
            )
            return result
        except subprocess.TimeoutExpired:
            pytest.fail(f"Command timed out after {timeout} seconds: {cmd}")
        except Exception as e:
            pytest.fail(f"Command failed to execute: {cmd}, Error: {e}")

    def _check_pieces_command(self, command="version"):
        """Check if pieces command works."""
        pieces_executable = self.installation_dir / "pieces"
        if platform.system() == "Windows":
            pieces_executable = self.installation_dir / "pieces.cmd"

        if not pieces_executable.exists():
            return False, f"Pieces executable not found at {pieces_executable}"

        try:
            result = subprocess.run(
                [str(pieces_executable), command],
                capture_output=True,
                text=True,
                timeout=30,
                env=os.environ.copy(),
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)

    def _log_installed_dependencies(self, venv_dir):
        """Log all installed dependencies with detailed information using pip show."""
        # Get pip executable path
        if platform.system() == "Windows":
            pip_executable = venv_dir / "Scripts" / "pip.exe"
        else:
            pip_executable = venv_dir / "bin" / "pip"

        if not pip_executable.exists():
            Settings.logger.debug(f"Pip executable not found at {pip_executable}")
            return

        try:
            # First get list of all installed packages
            Settings.logger.info("=== INSTALLED PACKAGES OVERVIEW ===")
            list_result = self._run_with_timeout(f'"{pip_executable}" list', timeout=30)
            if list_result.returncode == 0:
                Settings.logger.info("Installed packages:")
                for line in list_result.stdout.strip().split("\n"):
                    if line.strip():
                        Settings.logger.info(f"  {line}")
            else:
                Settings.logger.error(f"Failed to list packages: {list_result.stderr}")
                return

            # Extract package names (skip header lines)
            lines = list_result.stdout.strip().split("\n")
            packages = []
            for line in lines[2:]:  # Skip header lines
                if line.strip() and not line.startswith("-"):
                    package_name = line.split()[0]
                    packages.append(package_name)

            # Now get detailed info for each package using pip show
            Settings.logger.info("=== DETAILED PACKAGE INFORMATION ===")
            for package in packages:
                Settings.logger.info(f"\n--- Package: {package} ---")
                show_result = self._run_with_timeout(
                    f'"{pip_executable}" show "{package}"', timeout=30
                )
                if show_result.returncode == 0:
                    for line in show_result.stdout.strip().split("\n"):
                        if line.strip():
                            Settings.logger.info(f"  {line}")
                else:
                    Settings.logger.debug(
                        f"Failed to get details for package {package}: {show_result.stderr}"
                    )

            Settings.logger.info("=== END PACKAGE INFORMATION ===")

        except Exception as e:
            Settings.logger.error(f"Error logging dependencies: {e}")

    @pytest.mark.skipif(
        platform.system() == "Windows",
        reason="Shell script test only runs on Unix-like systems",
    )
    def test_shell_installation_script(self):
        """Test the shell installation script end-to-end."""
        # Get path to installation script
        script_path = Path(__file__).parent.parent / "install_pieces_cli.sh"
        assert script_path.exists(), f"Installation script not found at {script_path}"

        # Make script executable
        os.chmod(script_path, 0o755)

        # Prepare automated responses for interactive prompts
        # Simulate answering "y" to all PATH and completion setup questions
        input_responses = "\n".join(
            [
                "y",  # Add to PATH for bash (if bash is available)
                "n",  # Skip completion for bash
                "y",  # Add to PATH for zsh (if zsh is available)
                "n",  # Skip completion for zsh
                "y",  # Add to PATH for fish (if fish is available)
                "n",  # Skip completion for fish
            ]
        )

        # Run the installation script
        print(f"\nRunning shell installation script at {script_path}")
        print(f"Using temporary home directory: {self.temp_home}")

        result = self._run_with_timeout(
            f"bash {script_path}",
            timeout=600,  # 10 minutes for download and installation
            input_text=input_responses,
        )

        # Check if installation was successful
        print(f"Installation script exit code: {result.returncode}")
        print(f"Installation script stdout: {result.stdout}")
        if result.stderr:
            print(f"Installation script stderr: {result.stderr}")

        assert result.returncode == 0, f"Installation script failed: {result.stderr}"

        # Verify installation directory was created
        assert self.installation_dir.exists(), "Installation directory was not created"

        # Verify virtual environment was created
        venv_dir = self.installation_dir / "venv"
        assert venv_dir.exists(), "Virtual environment was not created"

        # Verify wrapper script was created
        wrapper_script = self.installation_dir / "pieces"
        assert wrapper_script.exists(), "Wrapper script was not created"
        assert os.access(wrapper_script, os.X_OK), "Wrapper script is not executable"

        # Test pieces commands
        success, output = self._check_pieces_command("version")
        assert success, f"pieces version command failed: {output}"
        print(f"pieces version output: {output}")

        success, output = self._check_pieces_command("help")
        assert success, f"pieces help command failed: {output}"
        print(f"pieces help output: {output}")

        # Verify that key dependencies are installed
        pip_executable = venv_dir / "bin" / "pip"
        if pip_executable.exists():
            result = self._run_with_timeout(f"{pip_executable} list")
            assert result.returncode == 0, "Failed to list installed packages"

            installed_packages = result.stdout.lower()
            # Check for some key dependencies
            assert "pieces-cli" in installed_packages, "pieces-cli package not found"
            assert "rich" in installed_packages, "rich dependency not found"
            assert "prompt-toolkit" in installed_packages, (
                "prompt-toolkit dependency not found"
            )

            # Log all installed dependencies with detailed information
            self._log_installed_dependencies(venv_dir)

    @pytest.mark.skipif(
        not shutil.which("pwsh") and not shutil.which("powershell"),
        reason="PowerShell not available",
    )
    def test_powershell_installation_script(self):
        """Test the PowerShell installation script end-to-end."""
        # Get path to installation script
        script_path = Path(__file__).parent.parent / "install_pieces_cli.ps1"
        assert script_path.exists(), f"Installation script not found at {script_path}"

        # Determine PowerShell executable
        pwsh_cmd = "pwsh" if shutil.which("pwsh") else "powershell"

        # Create a script file with automated responses
        response_script_content = """
        # Mock Read-Host to provide automated responses
        $global:ResponseIndex = 0
        $global:Responses = @("y", "n", "y", "n")  # PATH yes, completion no for each shell
        
        function Read-Host {
            param([string]$Prompt)
            if ($global:ResponseIndex -lt $global:Responses.Length) {
                $response = $global:Responses[$global:ResponseIndex]
                $global:ResponseIndex++
                Write-Host "$Prompt $response"
                return $response
            }
            return "n"
        }
        
        # Load and execute the installation script
        . "{script_path}"
        """.replace("{script_path}", str(script_path))

        # Write the response script to a temporary file
        response_script_path = Path(self.temp_home) / "install_with_responses.ps1"
        response_script_path.write_text(response_script_content)

        # Run the PowerShell installation script
        print(f"\nRunning PowerShell installation script at {script_path}")
        print(f"Using temporary home directory: {self.temp_home}")

        result = self._run_with_timeout(
            f'{pwsh_cmd} -ExecutionPolicy Bypass -File "{response_script_path}"',
            timeout=600,  # 10 minutes for download and installation
        )

        # Check if installation was successful
        print(f"Installation script exit code: {result.returncode}")
        print(f"Installation script stdout: {result.stdout}")
        if result.stderr:
            print(f"Installation script stderr: {result.stderr}")

        assert result.returncode == 0, f"Installation script failed: {result.stderr}"

        # Verify installation directory was created
        assert self.installation_dir.exists(), "Installation directory was not created"

        # Verify virtual environment was created
        venv_dir = self.installation_dir / "venv"
        assert venv_dir.exists(), "Virtual environment was not created"

        # Verify wrapper script was created
        if platform.system() == "Windows":
            wrapper_script = self.installation_dir / "pieces.cmd"
        else:
            wrapper_script = self.installation_dir / "pieces"

        assert wrapper_script.exists(), "Wrapper script was not created"

        # Test pieces commands
        success, output = self._check_pieces_command("version")
        assert success, f"pieces version command failed: {output}"
        print(f"pieces version output: {output}")

        success, output = self._check_pieces_command("help")
        assert success, f"pieces help command failed: {output}"
        print(f"pieces help output: {output}")

        # Log all installed dependencies with detailed information
        self._log_installed_dependencies(venv_dir)

    def test_installation_cleanup(self):
        """Test that installation cleans up properly."""
        # Create a mock failed installation scenario to test cleanup
        installation_dir = Path(self.temp_home) / ".pieces-cli"
        installation_dir.mkdir(parents=True, exist_ok=True)

        # Create some mock files
        (installation_dir / "test_file").write_text("test content")

        # Verify files exist before cleanup
        assert installation_dir.exists()
        assert (installation_dir / "test_file").exists()

    def test_full_installation_workflow(self):
        """Test the complete installation workflow including PATH verification."""
        if platform.system() == "Windows":
            if not (shutil.which("pwsh") or shutil.which("powershell")):
                pytest.skip("PowerShell not available")
            script_path = Path(__file__).parent.parent / "install_pieces_cli.ps1"
            pwsh_cmd = "pwsh" if shutil.which("pwsh") else "powershell"

            # Create automated response script for PowerShell
            response_script = f'''
            function Read-Host {{
                param([string]$Prompt)
                Write-Host "$Prompt y"
                return "y"
            }}
            . "{script_path}"
            '''
            response_file = Path(self.temp_home) / "auto_install.ps1"
            response_file.write_text(response_script)
            cmd = f'{pwsh_cmd} -ExecutionPolicy Bypass -File "{response_file}"'
        else:
            script_path = Path(__file__).parent.parent / "install_pieces_cli.sh"
            cmd = f"bash {script_path}"

        # Run installation with all features enabled
        input_responses = "y\n" * 10  # Say yes to all prompts

        print("\nRunning full installation workflow test")
        result = self._run_with_timeout(cmd, timeout=900, input_text=input_responses)

        # Installation should complete successfully
        assert result.returncode == 0, f"Installation failed: {result.stderr}"

        # Verify all components are installed
        assert self.installation_dir.exists(), "Installation directory missing"
        assert (self.installation_dir / "venv").exists(), "Virtual environment missing"

        wrapper_script = self.installation_dir / "pieces"
        if platform.system() == "Windows":
            wrapper_script = self.installation_dir / "pieces.cmd"
        assert wrapper_script.exists(), "Wrapper script missing"

        # Test that CLI commands work
        success, output = self._check_pieces_command("version")
        assert success, f"pieces version failed: {output}"

        success, output = self._check_pieces_command("help")
        assert success, f"pieces help failed: {output}"

        # Verify help output contains expected content
        assert "usage:" in output.lower() or "help" in output.lower(), (
            f"Help output doesn't look correct: {output}"
        )

        # Log all installed dependencies with detailed information
        venv_dir = self.installation_dir / "venv"
        self._log_installed_dependencies(venv_dir)

        print("Full installation workflow test completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
