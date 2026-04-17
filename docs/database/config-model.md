## Configure `alembic/env.py`
If Alembic doesn't already have access to your project root, you can manually insert
it with the following at the top of your `env.py` file.
```
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
```

Import all your project's current models and environment variables (from a `config.py` file)
```
from src.config import settings
from src.database import Base
from src.auth.models import User
from src.dummies.models import Dummy
from src.google.models import GoogleOAuthCredential, GoogleOAuthState
from src.orders.models import Orders
```


In this file, find the field `sqlalchemy.url`, which should look something like
```
sqlalchemy.url = driver://user:pass@localhost/dbname
```
Remove this line, as we will load DB link from the environments instead. Note that,
Alembic only works with a synced database, so if your database URL links toward an
async one (**which will be the case when working with FastAPI**), modify the string
so that Alembic can parse the link, as seen here.
```
sync_url = settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")
config.set_main_option("sqlalchemy.url", sync_url)
```