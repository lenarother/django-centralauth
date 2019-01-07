def get_perm_hash(perm):
    """Get unique representation for application permission.

    This function is complementary to get_perm_hash from client app.

    Returns:
        str: hash of application permission
    """
    perm_str = '{app_label}-{codename}-{repr}'.format(
        app_label=perm.app_label,
        codename=perm.codename,
        repr=perm.repr
    )
    return str(hash(perm_str))
