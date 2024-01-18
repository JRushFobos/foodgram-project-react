from support_classes.custom_client import CustomClient as client


class TestUsers:
    def test_get_all_users_status_code(self):
        response = client().nonauth_user().get('/api/users/')
        assert response.status_code == 200, 'Status code not 200'
