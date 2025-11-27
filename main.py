from fastapi import FastAPI,Path,HTTPException,Query
from pydantic import BaseModel, Field, computed_field
from typing import Annotated,Literal, Optional
from fastapi.responses import JSONResponse
import json

class Patient(BaseModel):
    id : Annotated[str, Field(...,description="patient_id", examples=["P001"])]
    name : Annotated[str, Field(...,description="Name of the Patient")]
    city : Annotated[str, Field(description="City of residence")]
    age : Annotated[int, Field(description="Enter the Patient's name")]
    gender : Annotated[Literal["Female","Male","Trans"], Field(description="Enter the gender of the patient")]
    height :  Annotated[float, Field(description="Enter the Patient's height")]
    weight : Annotated[float, Field(description="Enter the Patient's weight")]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = self.weight/(self.height**2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi<=18:
            verdict = "Underweight"
        elif self.bmi<=25:
            verdict = "Normal"
        elif self.bmi<=30:
            verdict = "Overweight"
        else:
            verdict = "Obese"
        return verdict

app = FastAPI()

def load_data():
    with open('patients.json', 'r',encoding="utf-8-sig") as f:
        data = json.load(f)
    return data

def save_data(data):
    with open("patients.json","w") as f:
        json.dump(data,f)

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

@app.post("/create")
def create(patient:Patient):
    data = load_data()

    #check if the patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient already in the records")
    
    #if not, create a new pateint in the database
    data[patient.id] = patient.model_dump(exclude=["id"])
    save_data(data)

    return JSONResponse(status_code=201, content={'message':'patient created successfully'})

class PatientUpdate(BaseModel):
    name : Annotated[Optional[str], Field(default=None)]
    city : Annotated[Optional[str], Field(default=None)]
    age : Annotated[Optional[int],Field(default=None, gt= 0)]
    gender : Annotated[Optional[Literal["Male","Female"]], Field(default=None)]
    height : Annotated[Optional[float], Field(default=None, gt=0)]
    weight : Annotated[Optional[float], Field(default=None, gt=0)]

@app.put("/edit/{patient_id}")
def update_patient(patient_update: PatientUpdate, patient_id: str):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail = "patient not found")
    existing = data[patient_id] #this is a dictionary
    #convert the new patient details to dictionary
    new = patient_update.model_dump(exclude_unset=True)

    for key,value in new.items():
        existing[key] = value

    # now we need to verify the updated data, basically data validation.
    # so for that, we convert the new existing dict to pydantic model.
    # Also, we need to add id:value pair to the dict
    existing[id] = patient_id
    existing_pydantic = Patient(**existing)
    final_patient_dict = existing_pydantic.model_dump(exclude=["id"])
    data[id] = final_patient_dict

    #save the finsl dict to the database
    save_data(data)

    
