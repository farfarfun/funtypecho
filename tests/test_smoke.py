"""基础导入测试。"""


def test_import():
    import funtypecho

    assert funtypecho is not None
    assert funtypecho.Typecho is not None
