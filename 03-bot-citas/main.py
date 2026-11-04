"""API de citas con recordatorio. Uso: uvicorn main:app --reload"""
import sqlite3
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

DB = "citas.db"
ESTADOS = {"pendiente", "confirmada", "cancelada"}

app = FastAPI(title="Bot de citas")


def conectar():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute(
        """CREATE TABLE IF NOT EXISTS citas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            servicio TEXT NOT NULL,
            fecha_hora TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'pendiente',
            creada TEXT NOT NULL)"""
    )
    return con


class CitaEntrada(BaseModel):
    nombre: str
    telefono: str
    servicio: str
    fecha_hora: str


def fila_a_dict(fila):
    return dict(fila)


@app.get("/")
def inicio():
    return FileResponse("static/index.html")


@app.post("/citas", status_code=201)
def crear_cita(datos: CitaEntrada):
    try:
        datetime.fromisoformat(datos.fecha_hora)
    except ValueError:
        raise HTTPException(400, "fecha_hora debe ser ISO, ej 2026-11-10T09:30")

    con = conectar()
    cur = con.execute(
        "INSERT INTO citas(nombre,telefono,servicio,fecha_hora,creada) VALUES(?,?,?,?,?)",
        (datos.nombre, datos.telefono, datos.servicio, datos.fecha_hora,
         datetime.now().isoformat(timespec="seconds")),
    )
    con.commit()
    cita = fila_a_dict(con.execute("SELECT * FROM citas WHERE id=?", (cur.lastrowid,)).fetchone())
    con.close()
    return cita


@app.get("/citas")
def listar_citas(fecha: str | None = None):
    con = conectar()
    if fecha:
        filas = con.execute(
            "SELECT * FROM citas WHERE substr(fecha_hora,1,10)=? ORDER BY fecha_hora",
            (fecha,)).fetchall()
    else:
        filas = con.execute("SELECT * FROM citas ORDER BY fecha_hora").fetchall()
    con.close()
    return [fila_a_dict(f) for f in filas]


@app.get("/citas/proximas")
def citas_proximas(horas: int = 24):
    desde = datetime.now()
    hasta = desde + timedelta(hours=horas)
    con = conectar()
    filas = con.execute(
        "SELECT * FROM citas WHERE estado != 'cancelada' AND fecha_hora BETWEEN ? AND ? ORDER BY fecha_hora",
        (desde.isoformat(timespec="minutes"), hasta.isoformat(timespec="minutes")),
    ).fetchall()
    con.close()
    return [fila_a_dict(f) for f in filas]


@app.patch("/citas/{cita_id}/estado")
def cambiar_estado(cita_id: int, estado: str):
    if estado not in ESTADOS:
        raise HTTPException(400, f"estado invalido, usa: {sorted(ESTADOS)}")
    con = conectar()
    cur = con.execute("UPDATE citas SET estado=? WHERE id=?", (estado, cita_id))
    con.commit()
    if cur.rowcount == 0:
        con.close()
        raise HTTPException(404, "cita no encontrada")
    cita = fila_a_dict(con.execute("SELECT * FROM citas WHERE id=?", (cita_id,)).fetchone())
    con.close()
    return cita