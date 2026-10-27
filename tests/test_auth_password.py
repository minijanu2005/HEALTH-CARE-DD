from auth import hash_password, verify_password


def test_hash_and_verify() -> None:
    h = hash_password("Demo@2026!")
    assert verify_password(h, "Demo@2026!")
    assert not verify_password(h, "wrong")
