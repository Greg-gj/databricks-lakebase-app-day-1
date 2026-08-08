from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = FastAPI(title="Ticketing System Backend")

DB_URL = os.environ.get("LAKEBASE_URL")

def get_db_connection():
    if not DB_URL:
        raise HTTPException(status_code=500, detail="LAKEBASE_URL environment variable is missing.")
    return psycopg2.connect(DB_URL)

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
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if status_filter and status_filter != "All":
        cur.execute("SELECT * FROM tickets WHERE status = %s ORDER BY created_at DESC;", (status_filter,))
    else:
        cur.execute("SELECT * FROM tickets ORDER BY created_at DESC;")
    tickets = cur.fetchall()
    cur.close()
    conn.close()
    return tickets

@app.post("/tickets")
def create_ticket(ticket: TicketCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO tickets (title, status, created_by) VALUES (%s, 'open', %s) RETURNING ticket_id;",
            (ticket.title, ticket.created_by)
        )
        ticket_id = cur.fetchone()[0]
        conn.commit()
        return {"message": "Ticket created successfully", "ticket_id": ticket_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/tickets/{ticket_id}/messages")
def get_messages(ticket_id: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM ticket_messages WHERE ticket_id = %s ORDER BY created_at ASC;", (ticket_id,))
    messages = cur.fetchall()
    cur.close()
    conn.close()
    return messages

@app.post("/tickets/{ticket_id}/messages")
def add_message(ticket_id: int, msg: MessageCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO ticket_messages (ticket_id, message_text, author) VALUES (%s, %s, %s);",
            (ticket_id, msg.message_text, msg.author)
        )
        conn.commit()
        return {"message": "Message added successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.put("/tickets/{ticket_id}/status")
def update_status(ticket_id: int, payload: StatusUpdate):
    if payload.status not in ["open", "in_progress", "resolved"]:
        raise HTTPException(status_code=400, detail="Invalid status assignment value.")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tickets SET status = %s WHERE ticket_id = %s;", (payload.status, ticket_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Status updated successfully"}

@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tickets WHERE ticket_id = %s;", (ticket_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Ticket dropped cleanly"}
