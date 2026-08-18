import pytest
from app.database.connection import SessionLocal
from app.database.repository import Repository
from app.models.database_models import UserModel, verify_password

def test_user_registration_and_authentication():
    db = SessionLocal()
    try:
        repo = Repository(db)
        test_email = "testauthuser@example.com"
        
        # Clean up if exists from previous run
        existing = repo.get_user_by_email(test_email)
        if existing:
            db.delete(existing)
            db.commit()

        # 1. Register User
        user = repo.create_user(name="Alice Learner", email=test_email, password="securepassword123")
        assert user.id is not None
        assert user.email == test_email
        assert user.name == "Alice Learner"
        assert user.token is not None
        assert verify_password("securepassword123", user.password_hash) is True

        # 2. Re-registration with same email should fail
        with pytest.raises(ValueError, match="already registered"):
            repo.create_user(name="Alice Copy", email=test_email, password="password456")

        # 3. Authenticate with wrong password
        failed_auth = repo.authenticate_user(email=test_email, password="wrongpassword")
        assert failed_auth is None

        # 4. Authenticate with correct password
        success_auth = repo.authenticate_user(email=test_email, password="securepassword123")
        assert success_auth is not None
        assert success_auth.email == test_email
        assert success_auth.token is not None

        # 5. Get user by token
        by_token = repo.get_user_by_token(success_auth.token)
        assert by_token is not None
        assert by_token.id == user.id
    finally:
        db.close()
