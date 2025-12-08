from fastapi import Depends, HTTPException, status

from ..core.security import get_current_user
from ..db import models


def require_admin(current_user: models.User = Depends(get_current_user)):
    """
    Dependency that ensures the current user has ADMIN permission level.
    Raises 403 Forbidden if the user is not an admin.
    """
    if current_user.permission_level != models.PermissionLevel.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


def require_admin_or_manager(current_user: models.User = Depends(get_current_user)):
    """
    Dependency that ensures the current user has ADMIN or MANAGER permission level.
    Raises 403 Forbidden if the user is not an admin or manager.
    """
    if current_user.permission_level not in (models.PermissionLevel.ADMIN, models.PermissionLevel.MANAGER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin or Manager access required"
        )
    return current_user
