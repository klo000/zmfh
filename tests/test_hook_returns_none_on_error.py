from zmfh.hook.meta_path import ZMFHMetaPathFinder


def test_finder_returns_none_for_dotted_names():
    f = ZMFHMetaPathFinder()
    assert f.find_spec("this.will.never.be.handled") is None
