from fastapi import APIRouter

### API Router ###
# All admin paths share the prefix, unlike the other role routers.
admin_router = APIRouter(
    prefix="/admin", 
    tags=["admin"]
    )


### Endpoints - minimum role ADMIN ###
