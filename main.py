from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from agent import DoctorAppointmentAgent
from langchain_core.messages import HumanMessage
import os
from groq import RateLimitError

os.environ.pop("SSL_CERT_FILE", None)
app = FastAPI()

class UserQuery(BaseModel):
    id_number:int
    messages:str

agent = DoctorAppointmentAgent()

@app.post("/execute")
def execute_agent(user_input:UserQuery):
    app_graph = agent.workflow()

    # Prepare agent state as expected by the workflow
    input = [
        HumanMessage(content=user_input.messages)
    ]
    query_data = {
        "messages": input,
        "id_number": user_input.id_number,
        "next":"",
        "query":"",
        "current_reasoning":"",
        
    }
    try:
        response = app_graph.invoke(query_data,config={"recursion_limit": 20})
        return {"messages": response["messages"]}
    except RateLimitError as exc:
        raise HTTPException(
            status_code=429,
            detail="Groq rate limit reached for the current model. Please wait and try again later, or switch to a lower-cost model.",
        ) from exc