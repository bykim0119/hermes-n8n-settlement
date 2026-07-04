import serve


def test_parse_investigate_params():
    assert serve.parse_investigate_params("partner=거래처C&diff=-6") == ("거래처C", -6)
    assert serve.parse_investigate_params("partner=거래처B&diff=12") == ("거래처B", 12)
