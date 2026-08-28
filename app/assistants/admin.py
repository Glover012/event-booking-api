from ..db.models import Users, Events
from ..schemas.users import UserRole, ChangeRoleRequest
from ..schemas.events import EventResponseOwner
from .organizer import OrganizerAssistant
from ..api.exceptions import HTTPError
from ..schemas.users import UserResponseAdmin
from ..api.pagination import PaginationParams, Page


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

    def get_user(self, user_id: int) -> Users:
        """
        Returns User model account by id.
        """
        target_model = self.users_service.find_by_identity(user_id)

        if target_model is None:
            raise HTTPError.USER_DOES_NOT_EXISTS()

        return target_model

    def list_users(
            self,
            pagination: PaginationParams,
            ) -> Page[UserResponseAdmin]:
        """
        Returns one page of every account in the system.

        The page is built here, not in the router, so every listing endpoint
        stays a single call plus the ApiResponse wrapper.
        """
        models, total = self.users_service.list_models(
            limit=pagination.per_page,
            offset=pagination.offset,
        )

        return Page[UserResponseAdmin].create(
            items=models,
            total=total,
            pagination=pagination,
        )

    def get_event(self, event_id: int) -> Events:
        """
        Returns any event, regardless of owner, status and visibility.

        Admin does not go through the ownership filter. The guard
        belongs to the organizer, where acting on someone else's
        event has to be impossible.
        """
        return self.events_service.get_model(event_id)

    def list_events(
            self,
            pagination: PaginationParams,
            ) -> Page[EventResponseOwner]:
        """
        Returns one page of every event in the system, drafts included.

        The page is built here, not in the router, so every listing endpoint
        stays a single call plus the ApiResponse wrapper.
        """
        models, total = self.events_service.list_models(
            limit=pagination.per_page,
            offset=pagination.offset,
        )

        return Page[EventResponseOwner].create(
            items=models,
            total=total,
            pagination=pagination,
        )
