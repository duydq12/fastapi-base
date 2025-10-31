class ErrorMessages:
    class Base:
        @staticmethod
        def create_entity_failed(target: str | None =None):
            return f"Create {target} failed! Please try again!" if target else "Create entities failed! Please try again!"

        @staticmethod
        def update_entity_failed(target: str | None =None):
            return f"Update {target} failed! Please try again!" if target else "Update entities failed! Please try again!"

        @staticmethod
        def soft_delete_failed(target: str | None =None):
            return f"Soft delete {target} already delete! Please try again!" if target else "Entities already delete! Please try again!"

        @staticmethod
        def hard_delete_failed(target: str | None =None):
            return f"Hard delete {target} failed! Please try again" if target else "Hard delete entities  failed! Please try again"

        @staticmethod
        def restore_failed(target: str | None =None):
            return f"Restore {target} failed! Please try again" if target else "Restore entities failed! Please try again"

        @staticmethod
        def deactivate_failed(target: str | None =None):
            return f"Deactivate {target} failed! Please try again" if target else "Deactivate entities failed! Please try again"

        @staticmethod
        def active_failed(target: str | None =None):
            return f"Active {target} failed! Please try again" if target else "Active entities failed! Please try again"

        @staticmethod
        def update_conflict(target: str | None =None):
            return f"The {target} has been modified. Please refresh and try again." if target else "The entities has been modified. Please refresh and try again."

        @staticmethod
        def not_found_record(target: str | None =None):
            return f"{target} not found! Please try again!" if target else "None not found! Please try again!"

        @staticmethod
        def duplicate_record(target: str | None =None):
            return f"{target} already exists! Please try again!" if target else "Entities already exists! Please try again!"

        @staticmethod
        def not_active_record(target: str | None =None):
            return f"{target} is not verified! Please active your account!" if target else "Entities already exists! Please try again!"

        @staticmethod
        def soft_delete_record(target: str | None =None):
            return f"{target} already delete! Please try again!" if target else "Entities already delete! Please try again!"

    @staticmethod
    def invalid_record(target: str ):
        return f"Invalid {target}! Please try again!"

    @staticmethod
    def not_match_with_old_password():
        return "Not match with old password! Please try another again!"

    @staticmethod
    def not_match_with_password():
        return "Not match with password! Please try another again!"

    @staticmethod
    def not_support_provider():
        return "This account not support this provider! Please try again!"

    @staticmethod
    def expired_session():
        return "Session expired! Please log in again!"

    @staticmethod
    def expired_target(target: str ):
        return f"{target} expired!"

    @staticmethod
    def is_used_target(target: str):
        return f"{target}  has been used!"

    not_enough_permission = "You do not have enough permission to access this resource"
    unauthorized = "You must be logged in to access this resource."

    class Schema:
        invalid_schema_array_element = "Invalid Schema array element"

    class Password:
        password_err_type = "Password must contain at least 8 characters, including uppercase, lowercase, number and special character"

    class Otp:
        otp_length_too_short = "OTP must longer than 6 character!"

    class PushNotification:
        not_exist_device_token_or_user_is_deactivate_receive_notification = (
            "Device token not exist or user is deactivate receive notification"
        )
        cannot_update_push = "Cannot update push notification! Please try again!"

    class BaseService:
        invalid_object_id_mongo = "Invalid ObjectID MongoDB"
        update_conflict = "The entity has been modified. Please refresh and try again."
