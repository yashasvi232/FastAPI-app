from fastapi import FastAPI,Path,HTTPException,Query
import json

app = FastAPI()

def load_data():
    with open('patients.json', 'r',encoding="utf-8-sig") as f:
        data = json.load(f)
    return data

@app.get('/patients/{patient_id}')
def view(patient_id: str = Path(..., description="the patient id from the database", example="P001")):
    dataset = load_data()
    if patient_id in dataset:
        return dataset[patient_id]
    else:
        return HTTPException(status_code=404,detail="Patient not sound")

@app.get("/")
def function1():
    return{'message':'Patient Management System API'}


@app.get("/about")
def about():
    return{'message':'A fully functional API to manage your patient records'}

@app.get("/sort")
def sort_patients(sort_by: str = Query(..., description="enter the parameter to be sorted by",), order: str = Query("asc", description="enter asd or dsc based on the order you want")):

    valid_sortby = ["height","bmi","weight"]
    if sort_by not in valid_sortby:
        raise HTTPException(status_code=400, detail = "enter a value from- bmi,weight,height")
    
    valid_order = ["asc","dsc"]
    if order not in valid_order:
        raise HTTPException(status_code=400, detail="enter a value from- asc,dsc")
    
    data = load_data()
    sorted_order = True if order=="desc" else False
    sorted_data = sorted(data.values(),key=lambda x: x.get(sort_by,0),reverse= sorted_order)

    return sorted_data