"""
Script to help convert remaining controllers to TRUE OOP
This will be done manually but this tracks progress
"""

REMAINING_CONTROLLERS = {
    "UserAccount": [
        "suspend_user_account_controller.py",
        "view_user_account_controller.py", 
        "search_user_account_controller.py"
    ],
    "UserProfile": [
        "create_user_profile_controller.py",
        "update_user_profile_controller.py",
        "view_user_profile_controller.py",
        "suspend_user_profile_controller.py",
        "search_user_profile_controller.py"
    ],
    "Request": [
        "view_pin_request_controller.py",
        "update_pin_request_controller.py",
        "suspend_pin_request_controller.py",
        "search_pin_request_controller.py",
        "get_pin_requests_controller.py",
        "get_request_analytics_controller.py",
        "get_request_lookups_controller.py",
        "get_completed_matches_controller.py",
        "increment_view_count_controller.py"
    ],
    "Shortlist": [
        "get_shortlist_controller.py",
        "update_shortlist_status_controller.py",
        "remove_from_shortlist_controller.py",
        "get_shortlist_stats_controller.py"
    ],
    "Role": [
        "create_role_controller.py",
        "get_role_controller.py",
        "get_all_roles_controller.py",
        "get_public_roles_controller.py",
        "update_role_controller.py",
        "delete_role_controller.py"
    ]
}

print("=" * 80)
print("REMAINING CONTROLLERS TO CONVERT")
print("=" * 80)

total = 0
for category, files in REMAINING_CONTROLLERS.items():
    print(f"\n{category}: {len(files)} files")
    for f in files:
        print(f"  - {f}")
        total += 1

print(f"\n{'=' * 80}")
print(f"TOTAL: {total} controllers to convert")
print(f"{'=' * 80}")

