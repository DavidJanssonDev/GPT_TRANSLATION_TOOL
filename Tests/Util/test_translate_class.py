import util.translate_class as tc

def test_translate_system_has_method():
    t = tc.TransalteSystem()
    assert hasattr(t, "_transalate")
    # Should be callable even if it's a stub
    t._transalate()
