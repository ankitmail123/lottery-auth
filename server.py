from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ticket_verifier import TicketVerifier
from ticket_generator import TicketGenerator
import uvicorn

app = FastAPI()

# Initialize generator and verifier with same key (in production, use secure key management)
generator = TicketGenerator()
verifier = TicketVerifier(generator.secret_key)

class TicketData(BaseModel):
    encoded_data: str

@app.post("/verify-ticket/")
async def verify_ticket(ticket: TicketData):
    is_valid, message = verifier.verify_ticket(ticket.encoded_data)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@app.post("/generate-ticket/{ticket_id}")
async def generate_ticket(ticket_id: str):
    encoded = generator.generate_ticket_data(ticket_id)
    return {"ticket_data": encoded}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
