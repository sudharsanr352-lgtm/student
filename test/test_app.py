import pytest
from src.backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestHealth:
    def test_health_endpoint(self, client):
        res = client.get('/health')
        assert res.status_code == 200
        assert b"healthy" in res.data

class TestAuthentication:
    def test_login_redirects_to_dashboard(self, client):
        res = client.post('/login', data={'username': 'any', 'password': 'any'})
        # Flask redirect returns 302 by default
        assert res.status_code == 302
        assert res.location.endswith('/dashboard')

class TestStudentsAPI:
    def test_get_students(self, client):
        res = client.get('/api/students')
        assert res.status_code == 200
        assert isinstance(res.json, list)

    def test_create_student(self, client):
        new_student = {"reg_no": "999", "name": "Test", "cgpa": 9.0}
        res = client.post('/api/students', json=new_student)
        assert res.status_code == 201
        assert res.json['message'] == "Student created"

    def test_delete_student(self, client):
        # first add one
        client.post('/api/students', json={"reg_no": "DEL1", "name": "ToDelete", "cgpa": 7.0})
        res = client.delete('/api/students?reg_no=DEL1')
        assert res.status_code == 200
        # verify gone
        get_res = client.get('/api/students')
        assert not any(s['reg_no'] == 'DEL1' for s in get_res.json)

class TestStatsAPI:
    def test_stats_endpoint(self, client):
        res = client.get('/api/stats')
        assert res.status_code == 200
        assert 'total_students' in res.json
        assert 'avg_cgpa' in res.json