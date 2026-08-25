from ..db.models import Users
from ..schemas.users import UserRole, ChangeRoleRequest
from .organizer import OrganizerAssistant
from ..api.exceptions import HTTPError


class AdminAssistant(OrganizerAssistant):
    """
    Helper for admin level routes.
    """

    MINIMUM_ROLE = UserRole.ADMIN

    def change_user_role(
            self,
            user_id: int,
            change_role_request: ChangeRoleRequest,
            ) -> Users:
        """
        Sets the role of another account.
        """

        target_model = self.users_service.find_by_identity(
            user_id
        )

        if target_model is None:
            raise HTTPError.USER_DOES_NOT_EXISTS()

        # Identity operator works here, because
        # each model was delivered by the same db session, 
        # therefore SQLAlchemy identity map returns the same
        # object for the same row in db
        if target_model is self.me_model:
            raise HTTPError.CANNOT_MODIFY_OWN_PERMISSIONS()

        if target_model.role == change_role_request.role:
            raise HTTPError.SAME_ROLE()

        return self.users_service.update_role(
            target_model, 
            change_role_request.role,
            )
