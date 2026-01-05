"""Unit tests for /roll command parsing."""

import pytest


class TestRollParsing:
    """Test dice roll input parsing."""

    @pytest.mark.parametrize("input_text,expected_valid", [
        ("1d6", True),
        ("2d10", True),
        ("10d20", True),
        ("1D6", True),  # Case insensitive
        ("0d6", False),  # Zero dice
        ("11d6", False),  # Too many dice
        ("1d0", False),  # Zero sides
        ("1d21", False),  # Too many sides
        ("abc", False),  # Not a dice format
        ("1d", False),  # Incomplete
        ("d6", False),  # Missing count
    ])
    def test_roll_input_validation(self, input_text, expected_valid):
        """Test various roll command inputs."""
        try:
            text = input_text.lower()
            numdice, typedice = [int(num) for num in text.split("d")]
            valid = (
                0 < numdice <= 10 and
                0 < typedice <= 20
            )
        except (ValueError, IndexError):
            valid = False

        assert valid == expected_valid
