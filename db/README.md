# Database

The application uses MongoDB.

## Local setup

Install MongoDB locally or start a MongoDB service with:

```bash
docker run --name placement-copilot-mongo -p 27017:27017 -d mongo:8
```

The backend uses these defaults:

- Host: `mongodb://localhost:27017`
- Database: `placement_copilot`

Collections are created automatically when the backend starts. Do not commit
database dumps, uploaded files, credentials, or other runtime data.
