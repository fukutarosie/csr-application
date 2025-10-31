"""Create User Profile Controller - Business logic for role creation"""

from src.entity import Role


class CreateUserProfileController:
    REQUIRED_FIELDS = {"role_name", "role_code", "description"}

    @staticmethod
    def create_user_profile(payload):
        if payload is None:
            return {
                "success": False,
                "message": "Request payload is required"
            }, 400

        missing_fields = CreateUserProfileController.REQUIRED_FIELDS - payload.keys()
        if missing_fields:
            return {
                "success": False,
                "message": f"Missing required fields: {', '.join(sorted(missing_fields))}"
            }, 400

        result = Role.create_role(
            role_name=payload["role_name"],
            role_code=payload["role_code"],
            description=payload["description"],
            dashboard_route=payload.get("dashboard_route", "/dashboard")
        )

        if result:
            return {
                "success": True,
                "data": result,
                "message": "User profile created successfully"
            }, 201

        return {
            "success": False,
            "message": "Failed to create user profile"
        }, 400
