from dataclasses import dataclass


# slots=True removes __dict__ and prevents dynamic attribute assignment
@dataclass(frozen=True, slots=True)
class ApiInfoItem:
    """Closed value object for an ApiResponse code and message."""

    CODE: str
    MESSAGE: str


class ApiInfo:
    """Namespace for predefined ApiResponse codes and messages."""

    USER_CREATED = ApiInfoItem(
        CODE="USER_CREATED",
        MESSAGE="User created successfully.",
    )

    USER_ALREADY_EXISTS = ApiInfoItem(
        CODE="USER_ALREADY_EXISTS",
        MESSAGE="User already exists.",
    )

    USER_DOES_NOT_EXISTS = ApiInfoItem(
        CODE="USER_DOES_NOT_EXISTS",
        MESSAGE="User does not exists."
    )

    INCORRECT_PASSWORD = ApiInfoItem(
        CODE="INCORRECT_PASSWORD",
        MESSAGE="Password is incorrect.",
    )

    SAME_PASSWORD = ApiInfoItem(
        CODE= "SAME_PASSWORD",
        MESSAGE="New password can not be the same."
    )

    PASSWORD_CHANGED_SUCCESSFULLY = ApiInfoItem(
        CODE="PASSWORD_CHANGED_SUCCESSFULLY",
        MESSAGE="Password changed successfully."
    )

    USER_RETRIEVED = ApiInfoItem(
        CODE="USER_RETRIEVED",
        MESSAGE="User retrieved successfully.",
    )

    INVALID_CREDENTIALS = ApiInfoItem(
        CODE="INVALID_CREDENTIALS",
        MESSAGE="Invalid credentials.",
    )

    NOT_AUTHENTICATED = ApiInfoItem(
        CODE="NOT_AUTHENTICATED",
        MESSAGE="Not authenticated.",
    )

    AUTHENTICATION_FAILED = ApiInfoItem(
        CODE="AUTHENTICATION_FAILED",
        MESSAGE="Authentication failed.",
    )

    HTTP_ERROR = ApiInfoItem(
        CODE="HTTP_ERROR",
        MESSAGE="HTTP error.",
    )

    VALIDATION_ERROR = ApiInfoItem(
        CODE="VALIDATION_ERROR",
        MESSAGE="Invalid request data.",
    )

    RESPONSE_VALIDATION_ERROR = ApiInfoItem(
        CODE="RESPONSE_VALIDATION_ERROR",
        MESSAGE="Invalid response data.",
    )

    INTERNAL_SERVER_ERROR = ApiInfoItem(
        CODE="INTERNAL_SERVER_ERROR",
        MESSAGE="Internal server error.",
    )

    FORBIDDEN = ApiInfoItem(
        CODE="FORBIDDEN",
        MESSAGE="Insufficient permissions."
    )

    EVENT_CREATED = ApiInfoItem(
        CODE="EVENT_CREATED",
        MESSAGE="Event created successfully.",
    )

    TRANSACTION_REFUSED = ApiInfoItem(
        CODE="TRANSACTION_REFUSED",
        MESSAGE="Requested transaction has been refused.",
    )

    EVENT_RETRIEVED = ApiInfoItem(
        CODE="EVENT_RETRIEVED",
        MESSAGE="Event retrieved successfully.",
    )

    EVENTS_RETRIEVED = ApiInfoItem(
        CODE="EVENTS_RETRIEVED",
        MESSAGE="Events retrieved successfully.",
    )

    EVENT_DOES_NOT_EXIST = ApiInfoItem(
        CODE="EVENT_DOES_NOT_EXIST",
        MESSAGE="Event does not exist.",
    )

    CANNOT_MODIFY_OWN_PERMISSIONS = ApiInfoItem(
        CODE="CANNOT_MODIFY_OWN_PERMISSIONS",
        MESSAGE="Cannot target own permissions.",
    )

    SAME_ROLE = ApiInfoItem(
        CODE="SAME_ROLE",
        MESSAGE="Account role is the same as requested.",
    )
    
    ROLE_CHANGED = ApiInfoItem(
        CODE="ROLE_CHANGED",
        MESSAGE="Account role changed successfully.",
    )

    ME_INFO_RETRIEVED = ApiInfoItem(
        CODE="ME_INFO_RETRIEVED",
        MESSAGE="Me info retrieved successfully.",
    )

    ME_PROFILE_UPDATED = ApiInfoItem(
        CODE="ME_PROFILE_UPDATED",
        MESSAGE="Profile updated successfully.",
    )

    BOOKING_CREATED = ApiInfoItem(
        CODE="BOOKING_CREATED",
        MESSAGE="Ticket booked successfully.",
    )

    BOOKING_ALREADY_EXISTS = ApiInfoItem(
        CODE="BOOKING_ALREADY_EXISTS",
        MESSAGE="Event is already booked by this account.",
    )

    EVENT_NOT_BOOKABLE = ApiInfoItem(
        CODE="EVENT_NOT_BOOKABLE",
        MESSAGE="Event does not accept bookings.",
    )

    NOT_ENOUGH_TICKETS = ApiInfoItem(
        CODE="NOT_ENOUGH_TICKETS",
        MESSAGE="Not enough tickets left for this event.",
    )

    ME_BOOKINGS_RETRIEVED = ApiInfoItem(
        CODE="ME_BOOKINGS_RETRIEVED",
        MESSAGE="Bookings retrieved successfully.",
    )

    BOOKING_CANCELLED = ApiInfoItem(
        CODE="BOOKING_CANCELLED",
        MESSAGE="Booking cancelled successfully.",
    )

    BOOKING_DOES_NOT_EXIST = ApiInfoItem(
        CODE="BOOKING_DOES_NOT_EXIST",
        MESSAGE="Booking does not exist.",
    )

    BOOKING_ALREADY_CANCELLED = ApiInfoItem(
        CODE="BOOKING_ALREADY_CANCELLED",
        MESSAGE="Booking is already cancelled.",
    )

    ME_EVENTS_RETRIEVED = ApiInfoItem(
        CODE="ME_EVENTS_RETRIEVED",
        MESSAGE="Own events retrieved successfully.",
    )

    PARTICIPANTS_RETRIEVED = ApiInfoItem(
        CODE="PARTICIPANTS_RETRIEVED",
        MESSAGE="Participants retrieved successfully.",
    )

    EVENT_STATUS_CHANGED = ApiInfoItem(
        CODE="EVENT_STATUS_CHANGED",
        MESSAGE="Event status changed successfully.",
    )

    SAME_STATUS = ApiInfoItem(
        CODE="SAME_STATUS",
        MESSAGE="Event already holds the requested status.",
    )

    INVALID_STATUS_TRANSITION = ApiInfoItem(
        CODE="INVALID_STATUS_TRANSITION",
        MESSAGE="Event cannot move to the requested status.",
    )

    EVENT_PUBLISHED = ApiInfoItem(
        CODE="EVENT_PUBLISHED",
        MESSAGE="Event published successfully.",
    )

    EVENT_ALREADY_PUBLISHED = ApiInfoItem(
        CODE="EVENT_ALREADY_PUBLISHED",
        MESSAGE="Event is already published.",
    )

    EVENT_NOT_PUBLISHABLE = ApiInfoItem(
        CODE="EVENT_NOT_PUBLISHABLE",
        MESSAGE="Only an active event can be published.",
    )

    EVENT_UPDATED = ApiInfoItem(
        CODE="EVENT_UPDATED",
        MESSAGE="Event updated successfully.",
    )

    EVENT_DATES_LOCKED_BY_BOOKINGS = ApiInfoItem(
        CODE="EVENT_DATES_LOCKED_BY_BOOKINGS",
        MESSAGE="Event dates cannot change once tickets are booked.",
    )

    EVENT_NOT_EDITABLE = ApiInfoItem(
        CODE="EVENT_NOT_EDITABLE",
        MESSAGE="Finished and cancelled events cannot be edited.",
    )

    CAPACITY_BELOW_BOOKED_TICKETS = ApiInfoItem(
        CODE="CAPACITY_BELOW_BOOKED_TICKETS",
        MESSAGE="Capacity cannot be lower than the tickets already booked.",
    )

    EVENT_CANCELLED = ApiInfoItem(
        CODE="EVENT_CANCELLED",
        MESSAGE="Event cancelled successfully.",
    )

    EVENT_ALREADY_CANCELLED = ApiInfoItem(
        CODE="EVENT_ALREADY_CANCELLED",
        MESSAGE="Event is already cancelled.",
    )

    EVENT_NOT_CANCELLABLE = ApiInfoItem(
        CODE="EVENT_NOT_CANCELLABLE",
        MESSAGE="A finished event cannot be cancelled.",
    )

    EVENT_DELETED = ApiInfoItem(
        CODE="EVENT_DELETED",
        MESSAGE="Event deleted successfully.",
    )

    EVENT_NOT_DELETABLE = ApiInfoItem(
        CODE="EVENT_NOT_DELETABLE",
        MESSAGE="Only a draft can be deleted.",
    )
