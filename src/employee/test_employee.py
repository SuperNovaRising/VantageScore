from fastapi.testclient import TestClient
from employee import app

client = TestClient(app)

def test_create_employee():
    response = client.post("/employees/", json={"employee_id": 1, "employee_name": "John Doe"})
    assert response.status_code == 200
    assert response.json() == {"employee_id": 1, "employee_name": "John Doe"}

def test_create_employee_failure():
    response = client.post("/employees/", json={"employee_id": 1, "employee_name": "John Doe"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Employee already exists"}

def test_read_employee():
    client.post("/employees/", json={"employee_id": 2, "employee_name": "Jane Doe"})
    response = client.get("/employees/2")
    assert response.status_code == 200
    assert response.json() == {"employee_id": 2, "employee_name": "Jane Doe"}

def test_read_employee_failure():
    response = client.get("/employees/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Employee not found"}

def test_update_employee():
    client.post("/employees/", json={"employee_id": 3, "employee_name": "Jim Doe"})
    response = client.put("/employees/3", json={"employee_id": 3, "employee_name": "Jimmy Doe"})
    assert response.status_code == 200
    assert response.json() == {"employee_id": 3, "employee_name": "Jimmy Doe"}

def test_update_employee_failure():
    response = client.put("/employees/999", json={"employee_id": 999, "employee_name": "Nonexistent"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Employee not found"}

def test_delete_employee():
    client.post("/employees/", json={"employee_id": 4, "employee_name": "Jenny Doe"})
    response = client.delete("/employees/4")
    assert response.status_code == 200
    assert response.json() == {"employee_id": 4, "employee_name": "Jenny Doe"}

def test_delete_employee_failure():
    response = client.delete("/employees/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Employee not found"}
