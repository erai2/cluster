from fastapi import FastAPI

from fastapi import APIRouter



app = FastAPI()

# default router (no API routers detected)
fallback = APIRouter()
@fallback.get('/health')
def _health():
    return {'ok': True}
app.include_router(fallback)


@app.get('/')
def root():
    return {'message': 'Suri API Running'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('suri.main:app', host='0.0.0.0', port=8000, reload=True)

