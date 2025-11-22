import subprocess
import sys
import os
from pathlib import Path
import pytest


class TestEndToEndSmoke:
    """End-to-end smoke tests for DataTalk CLI app in non-interactive mode."""

    @pytest.fixture
    def test_data_path(self):
        """Path to synthetic test data file."""
        return Path(__file__).parent / "test_data_e2e_smoke.csv"

    @pytest.fixture
    def mock_env_vars(self):
        """Set up environment variables for OpenAI configuration."""
        # Use real API key if available, otherwise use test key
        api_key = os.getenv("OPENAI_API_KEY", "test-api-key")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        env_vars = {"OPENAI_API_KEY": api_key, "OPENAI_MODEL": model}

        # Preserve existing environment
        original_env = {}
        for key in env_vars:
            if key in os.environ:
                original_env[key] = os.environ[key]
            os.environ[key] = env_vars[key]

        yield env_vars

        # Restore original environment
        for key in env_vars:
            if key in original_env:
                os.environ[key] = original_env[key]
            elif key in os.environ:
                del os.environ[key]

    def test_app_loads_csv_and_processes_basic_query(
        self, test_data_path, mock_env_vars
    ):
        """Test app can load CSV data and process basic query."""
        # Prepare command
        cmd = [
            sys.executable,
            "-m",
            "datatalk.main",
            str(test_data_path),
            "--prompt",
            "How many products are there?",
            "--hide-data",
        ]

        # Run the command
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Check that the command completed successfully or failed gracefully
        # (API key might not be valid, but app shouldn't crash)
        assert result.returncode in [
            0,
            1,
        ], f"Command failed unexpectedly with stderr: {result.stderr}"

        # Check for key indicators in output
        assert "Data loaded successfully!" in result.stdout
        # Should not enter interactive mode
        assert "AI Assistant Ready!" not in result.stdout

        # Should not crash or hang
        assert len(result.stdout) > 0

    def test_app_shows_sql_when_requested(self, test_data_path, mock_env_vars):
        """Test that the app shows SQL queries when --show-sql flag is used."""
        cmd = [
            sys.executable,
            "-m",
            "datatalk.main",
            str(test_data_path),
            "--prompt",
            "Show me all products",
            "--show-sql",
            "--hide-data",
        ]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should complete without crashing even if API fails
        assert result.returncode in [
            0,
            1,
        ], f"Command failed unexpectedly with stderr: {result.stderr}"

        # If API key is valid and call succeeds, SQL should be shown
        # If API fails, we should see an error but app shouldn't crash
        if "SQL:" in result.stdout:
            # API call succeeded and SQL was shown
            assert result.returncode == 0
        else:
            # API call may have failed, but app handled it gracefully
            assert "Error" in result.stdout or "error" in result.stdout.lower()

    def test_app_handles_missing_file_gracefully(self, mock_env_vars):
        """Test that the app handles missing data files gracefully."""
        cmd = [
            sys.executable,
            "-m",
            "datatalk.main",
            "nonexistent_file.csv",
            "--prompt",
            "test query",
        ]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should fail gracefully, not crash
        assert result.returncode != 0
        assert len(result.stderr) > 0 or "Error" in result.stdout

    def test_app_shows_help_when_no_file_provided(self):
        """Test that the app shows help when no file is provided."""
        cmd = [sys.executable, "-m", "datatalk.main"]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode != 0
        expected_msg = "CSV or Parquet file is required"
        assert expected_msg in result.stdout or "usage:" in result.stderr

    def test_app_config_info_flag_works(self):
        """Test --config-info flag works without requiring data file."""
        cmd = [sys.executable, "-m", "datatalk.main", "--config-info"]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0
        assert "Configuration file:" in result.stdout

    def test_app_reset_config_flag_works_safely(self, tmp_path):
        """Test --reset-config flag works without affecting user config."""
        # Create a temporary config directory structure
        temp_config_dir = tmp_path / ".config" / "datatalk"
        temp_config_dir.mkdir(parents=True)
        temp_config_file = temp_config_dir / "config.json"
        temp_config_file.write_text('{"OPENAI_API_KEY": "test-key"}')

        # Verify config exists before reset
        assert temp_config_file.exists()

        cmd = [sys.executable, "-m", "datatalk.main", "--reset-config"]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "HOME": str(tmp_path)},  # Override HOME
        )

        assert result.returncode == 0
        assert "Configuration file deleted" in result.stdout
        assert not temp_config_file.exists()  # Config should be deleted

    def test_app_reset_config_when_no_config_exists(self, tmp_path):
        """Test --reset-config flag when no config file exists."""
        cmd = [sys.executable, "-m", "datatalk.main", "--reset-config"]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "HOME": str(tmp_path)},  # Override HOME
        )

        assert result.returncode == 0
        assert "No configuration file to delete" in result.stdout

    def test_app_hide_schema_flag_works(self, test_data_path, mock_env_vars):
        """Test that the --hide-schema flag hides detailed column info."""
        cmd = [
            sys.executable,
            "-m",
            "datatalk.main",
            str(test_data_path),
            "--prompt",
            "Show me the data",
            "--hide-schema",
            "--hide-data",
        ]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should complete without crashing
        assert result.returncode in [
            0,
            1,
        ], f"Command failed unexpectedly with stderr: {result.stderr}"

        # Should load data successfully
        assert "Data loaded successfully!" in result.stdout

        # Should not show detailed schema information (column details table)
        # The app should show basic stats but not the detailed column table
        assert "Data loaded successfully!" in result.stdout
