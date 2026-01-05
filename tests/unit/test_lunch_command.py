"""Unit tests for LunchCommand parsing logic."""

import pytest

from pybot.endpoints.slack.utils.slash_lunch import LunchCommand


class TestLunchCommandParsing:
    """Test input parsing without making API calls."""

    def test_empty_input_uses_defaults(self):
        cmd = LunchCommand("C123", "U456", "", "testuser")
        params = cmd.lunch_api_params

        assert params["term"] == "lunch"
        assert "location" in params
        assert "range" in params

    def test_zipcode_only_input(self):
        cmd = LunchCommand("C123", "U456", "90210", "testuser")
        params = cmd.lunch_api_params

        assert params["location"] == 90210
        assert params["term"] == "lunch"

    def test_zipcode_with_distance(self):
        cmd = LunchCommand("C123", "U456", "90210 5", "testuser")
        params = cmd.lunch_api_params

        assert params["location"] == 90210
        # 5 miles in meters
        assert params["range"] == int(5 * 1609.34)

    def test_invalid_zipcode_raises_error(self):
        """Invalid zipcode input should raise ValueError from zipcodes library."""

        with pytest.raises(ValueError, match="Invalid format"):
            LunchCommand("C123", "U456", "not-a-zip", "testuser")

    def test_negative_distance_converted_to_positive(self):
        cmd = LunchCommand("C123", "U456", "90210 -5", "testuser")
        params = cmd.lunch_api_params

        # Should use absolute value
        assert params["range"] == int(5 * 1609.34)

    def test_distance_capped_at_max(self):
        cmd = LunchCommand("C123", "U456", "90210 100", "testuser")
        params = cmd.lunch_api_params

        # Should cap at default (20 miles)
        assert params["range"] == int(20 * 1609.34)


class TestLunchCommandResponse:
    """Test response building."""

    def test_build_response_text(self):
        cmd = LunchCommand("C123", "U456", "90210", "testuser")

        mock_location = {
            "name": "Test Restaurant",
            "location": {"display_address": ["123 Main St", "Los Angeles, CA 90210"]},
        }

        response = cmd._build_response_text(mock_location)

        assert response["user"] == "U456"
        assert response["channel"] == "C123"
        assert "Test Restaurant" in response["text"]
        assert "123 Main St" in response["text"]


class TestYelpRequest:
    """Test Yelp API request building."""

    def test_yelp_request_structure(self):
        cmd = LunchCommand("C123", "U456", "90210", "testuser")
        request = cmd.get_yelp_request()

        assert request["url"] == "https://api.yelp.com/v3/businesses/search"
        assert "Authorization" in request["headers"]
        assert "params" in request
