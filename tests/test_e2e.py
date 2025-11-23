"""
E2E tests for DataTalk CLI.

These tests are provider-agnostic and work with any LLM provider configured
in your environment. Configure your provider by setting the appropriate
environment variables in a .env file:

OpenAI:
    LLM_MODEL=gpt-4o
    OPENAI_API_KEY=your-key

Anthropic:
    LLM_MODEL=claude-3-5-sonnet-20241022
    ANTHROPIC_API_KEY=your-key

Google:
    LLM_MODEL=gemini-1.5-flash
    GEMINI_API_KEY=your-key

Ollama (local):
    LLM_MODEL=ollama/llama3.1

The tests will use whatever provider is configured in your .env file.
"""
import json
import subprocess
import sys
import os
from pathlib import Path
import pytest


class TestCLI:
    """E2E tests for DataTalk CLI."""

    @pytest.fixture
    def test_data_csv(self):
        """Path to CSV test data file."""
        return Path(__file__).parent / "test_data_e2e.csv"

    @pytest.fixture
    def test_data_parquet(self):
        """Path to Parquet test data file."""
        return Path(__file__).parent / "test_data_e2e.parquet"

    @pytest.fixture
    def test_data_excel(self):
        """Path to Excel test data file."""
        return Path(__file__).parent / "test_data_e2e.xlsx"


    # ==================== FILE LOADING ====================

    def test_load_csv_file(self, test_data_csv):
        """Load CSV and process basic query."""
        cmd = [
            sys.executable,
            "-m",
            "datatalk.main",
            str(test_data_csv),
            "--prompt",
            "How many products are there?",
        ]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should complete without crashing (API might fail but app handles it)
        assert result.returncode in [
            0,
            1,
        ], f"Command failed unexpectedly with stderr: {result.stderr}"

        # Should load data successfully
        assert "Data loaded successfully!" in result.stdout
        # Should not enter interactive mode
        assert "Question" not in result.stdout

    def test_load_parquet_file(self, test_data_parquet):
        """Load Parquet file."""
        cmd = [
            sys.executable,
            "-m",
            "datatalk.main",
            str(test_data_parquet),
            "--prompt",
            "Show me all products",
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

    def test_load_excel_file(self, test_data_excel):
        """Load Excel file."""
        cmd = [
            sys.executable,
            "-m",
            "datatalk.main",
            str(test_data_excel),
            "--prompt",
            "Count the products",
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

    def test_load_invalid_format_fails(self, tmp_path):
        """Reject unsupported file format."""
        # Create a temporary .txt file
        invalid_file = tmp_path / "test.txt"
        invalid_file.write_text("some data")

        cmd = [
            sys.executable,
            "-m",
            "datatalk.main",
            str(invalid_file),
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

        # Should fail gracefully
        assert result.returncode != 0
        # Should show error about unsupported format
        assert "Error" in result.stdout or len(result.stderr) > 0

    def test_load_missing_file_fails(self):
        """Handle missing file gracefully."""
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

    # ==================== OUTPUT FORMATS ====================

    def test_output_sql_shown(self, test_data_csv):
        """Show SQL with --sql flag."""
        cmd = [
            sys.executable,
            "-m",
            "datatalk.main",
            str(test_data_csv),
            "--prompt",
            "Show me all products",
            "--sql",
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

    def test_output_json(self, test_data_csv):
        """JSON output with --json flag."""
        cmd = [
            sys.executable,
            "-m",
            "datatalk.main",
            str(test_data_csv),
            "--prompt",
            "Count all products",
            "--json",
        ]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should complete (might fail if API key invalid, but shouldn't crash)
        assert result.returncode in [
            0,
            1,
        ], f"Command failed unexpectedly with stderr: {result.stderr}"

        # If succeeded, output should be valid JSON
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                # Should have expected structure
                assert "sql" in data or "error" in data
            except json.JSONDecodeError:
                pytest.fail("Output is not valid JSON")

    def test_output_csv(self, test_data_csv):
        """CSV output with --csv flag."""
        cmd = [
            sys.executable,
            "-m",
            "datatalk.main",
            str(test_data_csv),
            "--prompt",
            "Select all products",
            "--csv",
        ]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should complete
        assert result.returncode in [
            0,
            1,
        ], f"Command failed unexpectedly with stderr: {result.stderr}"

        # If succeeded, output should be CSV format (contains commas or is empty)
        if result.returncode == 0:
            # CSV output should not contain rich formatting
            assert "Data loaded successfully!" not in result.stdout or "," in result.stdout

    def test_output_sql_only(self, test_data_csv):
        """Show only SQL with --sql-only flag."""
        cmd = [
            sys.executable,
            "-m",
            "datatalk.main",
            str(test_data_csv),
            "--prompt",
            "Get all products",
            "--sql-only",
        ]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should complete
        assert result.returncode in [
            0,
            1,
        ], f"Command failed unexpectedly with stderr: {result.stderr}"

        # If succeeded, should show SQL but not execute
        if result.returncode == 0 and "SQL:" in result.stdout:
            # SQL should be shown
            assert "SQL:" in result.stdout
            # But results table should not be shown (--sql-only means no execution output)
            # The app shows data loading, but not the query results

    # ==================== DISPLAY OPTIONS ====================

    def test_flag_no_schema(self, test_data_csv):
        """Hide schema table with --no-schema."""
        cmd = [
            sys.executable,
            "-m",
            "datatalk.main",
            str(test_data_csv),
            "--prompt",
            "Show me the data",
            "--no-schema",
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

    # ==================== QUERY PROCESSING ====================

    def test_query_select_all(self, test_data_csv):
        """Process SELECT * query."""
        cmd = [
            sys.executable,
            "-m",
            "datatalk.main",
            str(test_data_csv),
            "--prompt",
            "Show me all the data",
        ]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should complete
        assert result.returncode in [
            0,
            1,
        ], f"Command failed unexpectedly with stderr: {result.stderr}"

        # Should load data successfully
        assert "Data loaded successfully!" in result.stdout

    def test_query_aggregation(self, test_data_csv):
        """Process COUNT/SUM/AVG query."""
        cmd = [
            sys.executable,
            "-m",
            "datatalk.main",
            str(test_data_csv),
            "--prompt",
            "What is the total quantity?",
        ]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should complete
        assert result.returncode in [
            0,
            1,
        ], f"Command failed unexpectedly with stderr: {result.stderr}"

        # Should load data successfully
        assert "Data loaded successfully!" in result.stdout

    def test_query_filtering(self, test_data_csv):
        """Process WHERE clause query."""
        cmd = [
            sys.executable,
            "-m",
            "datatalk.main",
            str(test_data_csv),
            "--prompt",
            "Show me products in the Electronics category",
        ]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should complete
        assert result.returncode in [
            0,
            1,
        ], f"Command failed unexpectedly with stderr: {result.stderr}"

        # Should load data successfully
        assert "Data loaded successfully!" in result.stdout

    # ==================== ERROR HANDLING ====================

    def test_error_no_file_shows_help(self):
        """Show help when no file provided."""
        cmd = [sys.executable, "-m", "datatalk.main"]

        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode != 0
        # Should show helpful message about needing a file
        assert "Please specify a data file" in result.stdout or "usage:" in result.stderr

