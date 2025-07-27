
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from controllers import authenticationController, membersController, attendanceController, notificationController, firstTimersController, helperFunctionController
from fastapi_login import LoginManager






SECRET = "super-secret-key"
manager = LoginManager(SECRET, '/login')




load_dotenv()



app = FastAPI(
    title= "Church Management App",
    version="0.0.1",
    description="FastAPI Application",
    openapi_tags=[
        {
            "name": "Home",
            "description": "Check health of the API"
        }
    ]
)



# from decouple import config
# JWT_SECRET = config("secret")
# JWT_ALGORITHM = config("algorithm")

# app.mount("/static", StaticFiles(directory="static"), name="static")

# Redirect root URL to your main page
# @app.get("/")
# async def main_page():
#     return RedirectResponse(url="/static/index.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(authenticationController.router, tags=["Authentication"]),
app.include_router(membersController.router, tags=["Members"]),
app.include_router(attendanceController.router, tags=["Attendance"]),
app.include_router(notificationController.router, tags=["Notification"]),
app.include_router(firstTimersController.router, tags=["FirstTimers"])
app.include_router(helperFunctionController.router, tags=["HelperEndpoint"])

