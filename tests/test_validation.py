from utils.validation import parse_number, valid_juristic_id


def test_valid_juristic_id_requires_13_digits():
    assert valid_juristic_id("0107542000011")
    assert not valid_juristic_id("010754200001")
    assert not valid_juristic_id("010754200001A")


def test_parse_number_handles_commas_and_nulls():
    assert parse_number("1,234.50") == 1234.5
    assert parse_number("-") is None

