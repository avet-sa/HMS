from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.security import get_current_user
from ..db import models
from ..db.session import get_db


def require_role(*allowed_roles: models.PermissionLevel):
    """
    Factory function that returns a dependency requiring one or more roles.
    
    Usage:
        Depends(require_role(PermissionLevel.ADMIN, PermissionLevel.MANAGER))
    """
    async def dependency(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> models.User:
        if current_user.permission_level not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of the following roles: {', '.join(r.value for r in allowed_roles)}"
            )
        return current_user
    
    return dependency
