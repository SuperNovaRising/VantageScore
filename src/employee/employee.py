from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict
from auth import get_current_active_user, get_current_active_admin, User

app = FastAPI()

# Sample resource: Employee
class Employee(BaseModel):
    employee_id: int
    employee_name: str

# In-memory "database"
employees: Dict[int, Employee] = {}

# CRUD operations
@app.post("/employees/", response_model=Employee)
def create_employee(employee: Employee, _: User = Depends(get_current_active_admin)):
    """
    Create a new employee record in the system.

    Parameters:
    - employee: Employee object containing employee details.

    Returns:
    - The created Employee object.

    Raises:
    - HTTPException: 400 error if an employee with the given ID already exists.
    """
    if employee.employee_id in employees:
        raise HTTPException(status_code=400, detail="Employee already exists")
    employees[employee.employee_id] = employee
    return employee

@app.get("/employees/{employee_id}", response_model=Employee)
def read_employee(employee_id: int, _: User = Depends(get_current_active_user)):
    """
    Retrieve an employee's details by their ID.

    Parameters:
    - employee_id: Integer representing the unique ID of the employee.

    Returns:
    - The Employee object corresponding to the given employee ID.

    Raises:
    - HTTPException: 404 error if no employee with the given ID is found.
    """
    if employee_id not in employees:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employees[employee_id]

@app.put("/employees/{employee_id}", response_model=Employee)
def update_employee(employee_id: int, employee_update: Employee, _: User = Depends(get_current_active_admin)):
    """
    Update an existing employee's details.

    Parameters:
    - employee_id: Integer representing the unique ID of the employee to update.
    - employee_update: Employee object containing the updated details.

    Returns:
    - The updated Employee object.

    Raises:
    - HTTPException: 404 error if no employee with the given ID is found.
    - HTTPException: 400 error if the provided employee ID does not match the ID of the employee to be updated.
    """
    if employee_id not in employees:
        raise HTTPException(status_code=404, detail="Employee not found")
    # Validate employee_update's employee id is legit
    if employee_update.employee_id != employee_id:
        raise HTTPException(status_code=400, detail="Employee id change is not supported")
    employees[employee_id] = employee_update
    return employees[employee_id]

@app.delete("/employees/{employee_id}", response_model=Employee)
def delete_employee(employee_id: int, _: User = Depends(get_current_active_admin)):
    """
    Delete an employee from the system by their ID.

    Parameters:
    - employee_id: Integer representing the unique ID of the employee to delete.

    Returns:
    - The Employee object that was deleted.

    Raises:
    - HTTPException: 404 error if no employee with the given ID is found.
    """
    if employee_id not in employees:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employees.pop(employee_id)