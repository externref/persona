from motor.motor_asyncio import AsyncIOMotorClient

from persona.types import BiometricProfile


class Database:
    client: AsyncIOMotorClient

    def __init__(self, client: AsyncIOMotorClient) -> None:
        self.client = client

    async def add_user(self, payload: BiometricProfile) -> str:
        data = (
           await self.client.get_database("persona")
            .get_collection("biometric_templates")
            .insert_one(payload)
        )
        return str(data.inserted_id)

    async def fetch_user_index(self, user_id: str) -> BiometricProfile:
        return await (
            self.client.get_database("persona")
            .get_collection("biometric_templates")
            .find_one({"user_id": user_id})
        )
    
    async def add_anomaly(self, anomaly_payload: BiometricProfile) -> str:
        data = await self.client.get_database("persona").get_collection("biometric_anamolies").insert_one(anomaly_payload)
        return str(data.inserted_id)

    async def add_multi_index(self, user_id, payload: BiometricProfile) -> None:
        assert await self.fetch_user_indexes(user_id)
        await self.add_user(payload)
