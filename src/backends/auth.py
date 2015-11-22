from clients.models import User


class ModelBackend(object):

    def authenticate(self, username=None, password=None, **kwargs):
        if username and password:
            user = User.get_by_email(username)
            if user and user.check_password(password):
                return user
        # Run the default password hasher once to reduce the timing
        # difference between an existing and a non-existing user
        User(email='fake@fake.com').set_password(password)

    def get_user(self, user_id):
        result = User.get_by_id(user_id)
        return result
