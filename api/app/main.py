from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core import config
from app.features.images import router as images_router
from app.features.users import router as users_router, service as users_service, UserCredentials
from app.models.common import Model


class JwtConfig(Model):
    authjwt_secret_key = config.jwt_secret


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.web_url,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(images_router)
app.include_router(users_router)


@AuthJWT.load_config
def get_config():
    return JwtConfig()


@app.exception_handler(AuthJWTException)
def auth_exception_handler(_: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={'detail': exc.message}
    )


@app.on_event('startup')
def on_startup():
    if not users_service.has_user(config.admin_email):
        users_service.create_user(
            UserCredentials(email=config.admin_email, password=config.admin_password)
        )
