from fastapi import APIRouter, status

from ..api.pagination import Page
from ..api.response import ApiResponse
from ..api.info import ApiInfo
from ..schemas.users import UserResponse, ChangePasswordRequest, UpdateProfileRequest
from ..schemas.bookings import BookingResponse, CreateBookingRequest
from ..dependencies.assistants import user_assistant_dependency
from ..dependencies import pagination_dependency

### API Router ###
user_router = APIRouter(tags=["user"])


### Endpoints - minimum role USER ###
@user_router.get(
        '/me',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[UserResponse],
        )
def get_me_info(
    user_assistant: user_assistant_dependency,
    ) -> ApiResponse[UserResponse]:

    me_model = user_assistant.get_me()

    return ApiResponse[UserResponse].success(
        ApiInfo.ME_INFO_RETRIEVED,
        data=me_model,
        )


@user_router.put(
        '/me/password',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[None],
        )
def change_me_password(
    user_assistant: user_assistant_dependency,
    change_password_request: ChangePasswordRequest,
    ) -> ApiResponse[None]:

    user_assistant.change_me_password(change_password_request)

    return ApiResponse[None].success(
        ApiInfo.PASSWORD_CHANGED_SUCCESSFULLY,
        )


@user_router.put(
        '/me',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[UserResponse],
        )
def update_me_profile(
    user_assistant: user_assistant_dependency,
    update_profile_request: UpdateProfileRequest,
    ) -> ApiResponse[UserResponse]:

    me_model = user_assistant.update_me_profile(update_profile_request)

    return ApiResponse[UserResponse].success(
        ApiInfo.ME_PROFILE_UPDATED,
        data=me_model,
        )


@user_router.post(
        '/events/{event_id}/bookings',
        status_code=status.HTTP_201_CREATED,
        response_model=ApiResponse[BookingResponse],
        )
def book_event(
    event_id: int,
    user_assistant: user_assistant_dependency,
    create_booking_request: CreateBookingRequest,
    ) -> ApiResponse[BookingResponse]:

    new_booking = user_assistant.book_event(
        event_id,
        create_booking_request,
    )

    return ApiResponse[BookingResponse].success(
        ApiInfo.BOOKING_CREATED,
        data=new_booking,
        )


@user_router.get(
        '/me/bookings',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[Page[BookingResponse]],
        )
def list_me_bookings(
    user_assistant: user_assistant_dependency,
    pagination: pagination_dependency,
    ) -> ApiResponse[Page[BookingResponse]]:

    page = user_assistant.list_me_bookings(pagination)

    return ApiResponse[Page[BookingResponse]].success(
        ApiInfo.ME_BOOKINGS_RETRIEVED,
        data=page,
        )


@user_router.post(
        '/me/bookings/{booking_id}/cancel',
        status_code=status.HTTP_200_OK,
        response_model=ApiResponse[BookingResponse],
        )
def cancel_me_booking(
    booking_id: int,
    user_assistant: user_assistant_dependency,
    ) -> ApiResponse[BookingResponse]:

    cancelled_booking = user_assistant.cancel_me_booking(booking_id)

    return ApiResponse[BookingResponse].success(
        ApiInfo.BOOKING_CANCELLED,
        data=cancelled_booking,
        )
