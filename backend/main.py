from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

# Import your centralized database helper context manager from lakebase.py
from .lakebase import get_connection 

app = FastAPI(title="Ticketing System Backend")

# --- PYDANTIC VALIDATION MODELS (BONUS CHALLENGE) ---
class TicketCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100, description="Title must be between 5 and 100 characters.")
    created_by: EmailStr = Field(..., description="Must be a valid enterprise email address.")

class MessageCreate(BaseModel):
    message_text: str = Field(..., min_length=2, description="Message body cannot be empty.")
    author: EmailStr = Field(..., description="Must be a valid author email address.")

class StatusUpdate(BaseModel):
    status: str = Field(..., description="Must be open, in_progress, or resolved.")


@app.get("/tickets")
def get_tickets(status_filter: Optional[str] = None):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                if status_filter and status_filter != "All":
                    cur.execute("SELECT * FROM tickets WHERE status = %s ORDER BY created_at DESC;", (status_filter,))
                else:
                    cur.execute("SELECT * FROM tickets ORDER BY created_at DESC;")
                return cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Read Error: {str(e)}")


@app.post("/tickets")
def create_ticket(ticket: TicketCreate):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO tickets (title, status, created_by) VALUES (%s, 'open', %s) RETURNING ticket_id;",
                    (ticket.title, ticket.created_by)
                )
                # Since lakebase.py uses RealDictCursor, we read row data as a dictionary key
                ticket_id = cur.fetchone()["ticket_id"]
                conn.commit()
                return {"message": "Ticket created successfully", "ticket_id": ticket_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tickets/{ticket_id}/messages")
def get_messages(ticket_id: int):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ticket_messages WHERE ticket_id = %s ORDER BY created_at ASC;", (ticket_id,))
                return cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Message Retrieval Error: {str(e)}")


@app.post("/tickets/{ticket_id}/messages")
def add_message(ticket_id: int, msg: MessageCreate):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO ticket_messages (ticket_id, message_text, author) VALUES (%s, %s, %s);",
                    (ticket_id, msg.message_text, msg.author)
                )
                conn.commit()
                return {"message": "Message added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/tickets/{ticket_id}/status")
def update_status(ticket_id: int, payload: StatusUpdate):
    if payload.status not in ["open", "in_progress", "resolved"]:
        raise HTTPException(status_code=400, detail="Invalid status assignment value.")
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE tickets SET status = %s WHERE ticket_id = %s;", (payload.status, ticket_id))
                conn.commit()
                return {"message": "Status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status Mutation Error: {str(e)}")


@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tickets WHERE ticket_id = %s;", (ticket_id,))
                conn.commit()
                return {"message": "Ticket dropped cleanly"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion Error: {str(e)}")
