def test_add_two():
    """Test that 1 + 2 = 3."""
    x = 1
    y = 2
    assert x + y == 3


def test_dict_contains():
    """Test that dict contains key."""
    x = {"a": 1, "b": 2}

    expected = {"a": 1}

    # x should contain all the key-value pairs in expected
    assert expected.items() <= x.items()
