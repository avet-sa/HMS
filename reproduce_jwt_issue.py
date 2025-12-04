import os
import sys
from jose import jwt, JWTError

# Add the backend directory to sys.path to import app modules
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.core import security


def test_jwt_flow():
    print("Testing JWT Flow...")

    # 1. Test Password Hashing
    password = "testpassword"
    hashed = security.get_password_hash(password)
    print(f"Password: {password}")
    print(f"Hashed: {hashed}")

    assert security.verify_password(password, hashed)
    print("Password verification passed.")

    # 2. Test Token Generation
    username = "testuser"
    token = security.create_access_token(subject=username)
    print(f"Generated Token: {token}")

    # 3. Test Token Decoding
    try:
        payload = jwt.decode(
            token, security.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        print(f"Decoded Payload: {payload}")
        assert payload["sub"] == username
        print("Token decoding passed.")
    except JWTError as e:
        print(f"Token decoding failed: {e}")


if __name__ == "__main__":
    test_jwt_flow()
