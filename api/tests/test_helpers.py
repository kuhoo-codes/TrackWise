from fastapi.testclient import TestClient

from src.schemas.users import Token

# 1. Changed to a dictionary for easy key-based lookup
PREDEFINED_USER_DATA: dict[str, dict[str, str]] = {
    "appa": {"email": "appa@example.com", "password": "Password@123", "name": "Appa Singh"},
    "momo": {"email": "momo@example.com", "password": "Password@123", "name": "Momo Jaiswal"},
    "suki": {"email": "suki@example.com", "password": "Password@123", "name": "Suki Bhatt"},
}


class AuthHelper:
    """A helper class for user authentication and management in tests."""

    def __init__(self, client: TestClient) -> None:
        self.client = client
        # This will store the full API response, keyed by the name
        # e.g., self.users["appa"] = {"access_token": "...", "user": {...}}
        self.users: dict[str, Token] = {}

    def setup_predefined_users(self) -> None:
        """
        Creates the predefined users (appa, momo, suki) in the test database.
        """
        if self.users:  # Only run once
            return

        for key, user_data in PREDEFINED_USER_DATA.items():
            try:
                user_response = self.create_user(
                    email=user_data["email"],
                    password=user_data["password"],
                    name=user_data["name"],
                )
                # Store the response dict by its key (e.g., "appa")
                self.users[key] = user_response
            except Exception:
                raise

    # 2. Updated to accept a string key
    def get_predefined_user(self, key: str) -> Token:
        """
        Returns the full API response dict for a predefined user by key ("appa", "momo", or "suki").
        You must call `setup_predefined_users()` once before using this.
        Returns:
            A dict, e.g.: {"access_token": "...", "token_type": "Bearer", "user": {...}}
        """
        if not self.users:
            msg = (
                "AuthHelper error: Predefined users not created. "
                "Call `auth_helper.setup_predefined_users()` in your test."
            )
            raise Exception(msg)
        try:
            return self.users[key]
        except KeyError as err:
            msg = f"Invalid user key '{key}'. Valid keys are: {', '.join(self.users.keys())}"
            raise KeyError(msg) from err

    # 3. create_user remains the same, it's a general-purpose helper
    def create_user(self, email: str, password: str, name: str) -> Token:
        """
        Signs up a new user via the API.
        Returns:
            The full JSON response from the /auth/signup endpoint.
        """
        response = self.client.post(
            "/auth/signup",
            json={"email": email, "password": password, "name": name},
        )

        response.raise_for_status()
        return response.json()

    # Bonus helper also updated to use the string key
    def get_auth_headers(self, key: str) -> dict[str, str]:
        """
        A helper to quickly get auth headers for a predefined user.
        """
        user_data = self.get_predefined_user(key)
        token = user_data["access_token"]
        return {"Authorization": f"Bearer {token}"}
