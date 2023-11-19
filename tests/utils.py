def set_current_user(security, ds, email):
    """Set up so that when request is received,
    the token will cause 'user' to be made the current_user
    """

    def token_cb(request):
        if request.headers.get("Authentication-Token") == "token":
            return ds.find_user(email=email)
        return security.login_manager.anonymous_user()

    security.login_manager.request_loader(token_cb)