from __future__ import annotations

import dataclasses
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

import fastapi
import numpy as np
from motor.motor_asyncio import AsyncIOMotorClient

from persona.database import Database
from persona.types import BiometricPayload, BiometricProfile
from persona.biometrics import compare_payloads_isolation_forest
from fastapi.middleware.cors import CORSMiddleware

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)

db = Database(
            AsyncIOMotorClient(
                os.getenv("MONGO_HOST", "127.0.0.1"), os.getenv("MONGO_PORT", 27017)
            )
        )
@app.post("/api/v0/init")
async def add_user_first_time(request: fastapi.Request):
    data: BiometricPayload = await request.json()
    await db.add_user(Server.process_payload_to_db_model(data))

@app.post("/api/v0/compare")
async def compare(request: fastapi.Request):
    payload: BiometricPayload = await request.json()
    as_model = Server.process_payload_to_db_model(payload)
    biodata = await db.fetch_user_index(payload["user_id"])
    anomaly = compare_payloads_isolation_forest(biodata, as_model, anomaly_threshold=2.5)
    print(anomaly)
    # Convert numpy.bool to native Python bool for JSON serialization
    return {
        "anomaly": bool( anomaly["anomaly"])
    }

@dataclasses.dataclass
class Server:
    database: Database
    app: fastapi.FastAPI

    @classmethod
    def new(cls) -> Server:
        

     
    

        return cls(db, app)

    async def setup_for_user(self, payload: BiometricPayload) -> None:
        assert payload["is_signup"]
        database_payload = Server.process_payload_to_db_model(payload)
        response = await self.database.add_user(database_payload)
        logging.log(f"Data inserted with ID: {response}")

    @staticmethod
    def process_payload_to_db_model(payload: Dict[str, Any]) -> BiometricProfile:
        """
        Converts a BiometricPayload (raw events) into a
        BiometricProfile (statistical model) for MongoDB.
        """
        events = payload.get("events", [])
        user_id = payload.get("user_id")
        origin = payload.get("origin")

        mouse_velocities = []
        mouse_accelerations = []
        dwell_times = []
        flight_times = []

        key_press_start = {}
        last_key_release_time = None

        for i in range(len(events)):
            curr = events[i]

            if curr["type"] == "m" and i > 0:
                prev = events[i - 1]
                if prev["type"] == "m":
                    dist = np.sqrt(
                        (curr["x"] - prev["x"]) ** 2 + (curr["y"] - prev["y"]) ** 2
                    )
                    dt = curr["t"] - prev["t"]

                    if 0 < dt < 200:
                        v = dist / dt
                        mouse_velocities.append(v)

                        if len(mouse_velocities) > 1:
                            dv = mouse_velocities[-1] - mouse_velocities[-2]
                            mouse_accelerations.append(dv / dt)

            elif curr["type"] == "kd":
                key_press_start[curr["k"]] = curr["t"]
                if last_key_release_time:
                    flight_times.append(curr["t"] - last_key_release_time)

            elif curr["type"] == "ku":
                if curr["k"] in key_press_start:
                    dwell_times.append(curr["t"] - key_press_start[curr["k"]])
                    del key_press_start[curr["k"]]
                    last_key_release_time = curr["t"]

        def get_stats(data_list: List[float]):
            if not data_list:
                return {"mean": 0.0, "std_dev": 0.0, "count": 0, "weight": 0.0}
            return {
                "mean": float(np.mean(data_list)),
                "std_dev": float(np.std(data_list)),
                "count": len(data_list),
                "weight": 1.0,
            }

        db_document = {
            "user_id": user_id,
            "origin_site": origin,
            "features": {
                "mouse_velocity": get_stats(mouse_velocities),
                "mouse_acceleration": get_stats(mouse_accelerations),
                "key_dwell": get_stats(dwell_times),
                "key_flight": get_stats(flight_times),
            },
            "metadata": {
                "sw": payload["metadata"]["sw"],
                "sh": payload["metadata"]["sh"],
                "plt": payload["metadata"]["plt"],
            },
            "trust_score": 0.5 if payload.get("is_signup") else 0.0,
            "created_at": datetime.now(timezone.utc),
            "last_updated": datetime.now(timezone.utc),
            "version": 1,
        }

        return db_document
