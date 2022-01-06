from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    """
    This Permission is responsible for checking whether obj.user == request.user
    This class is more general, if there are other places that also use this class in the future,
    can put the file in a shared location
    Permission will be executed one by one
    - If it is an action with detail=False, only has_permission is checked
    - If it is an action with detail=True, check has_permission and has_object_permission at the same time
    If something goes wrong, the default error message will display the content in IsObjectOwner.message
    """
    message = "You do not have permission to access this object"

    # POST /api/comments/ -> create
    # GET /api/comments/ -> list
    def has_permission(self, request, view):
        return True

    # GET /api/comments/1/ -> retrieve
    # DELETE /api/comments/1/ -> destroy
    # PATCH /api/comments/1/ -> partial_update
    # PUT /api/comments/1/ -> update
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user