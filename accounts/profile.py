from accounts.models import UserProfile

def retrieve(request):
    """ note that this requires an authenticated user before we try calling it """
    try:
        profile = request.user.get_profile()
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)
        profile.save()
    return profile

