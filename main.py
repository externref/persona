import os
import asyncio
import dotenv
import uvicorn

from persona.sever import Server
from persona.biometrics import compare_payloads_isolation_forest

dotenv.load_dotenv()

if __name__ == "__main__":
    server = Server.new()
    
    # async def main():
        
    #     sarthak = await server.database.fetch_user_index("aryan2")
    #     sarthak1 = await  server.database.fetch_user_index("aryan3")

    #     print(compare_payloads_isolation_forest(sarthak, sarthak1, anomaly_threshold=0.5))
    # asyncio.run(main())
    uvicorn.run(server.app, host=os.getenv("HOST", "127.0.0.1"), port=os.getenv("PORT", 8000))
