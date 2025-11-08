"""User Profile package exports for controller and boundary layers"""

from .create_user_profile_controller import CreateUserProfileController
from .search_user_profile_controller import SearchUserProfileController
from .suspend_user_profile_controller import SuspendUserProfileController
from .update_user_profile_controller import UpdateUserProfileController
from .view_user_profile_controller import ViewAllUserProfilesController, ViewOneUserProfileController

from .boundary.create_user_profile_boundary import create_user_profile_boundary
from .boundary.search_user_profile_boundary import search_user_profile_boundary
from .boundary.suspend_user_profile_boundary import suspend_user_profile_boundary
from .boundary.update_user_profile_boundary import update_user_profile_boundary
from .boundary.view_user_profile_boundary import view_user_profile_boundary

user_profile_boundaries = [
    create_user_profile_boundary,
    search_user_profile_boundary,
    suspend_user_profile_boundary,
    update_user_profile_boundary,
    view_user_profile_boundary,
]

__all__ = [
    "CreateUserProfileController",
    "SearchUserProfileController",
    "SuspendUserProfileController",
    "UpdateUserProfileController",
    "ViewAllUserProfilesController",
    "ViewOneUserProfileController",
    "create_user_profile_boundary",
    "search_user_profile_boundary",
    "suspend_user_profile_boundary",
    "update_user_profile_boundary",
    "view_user_profile_boundary",
    "user_profile_boundaries",
]
