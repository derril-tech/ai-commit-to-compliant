-- Initialize ProdSprints AI database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "citext";

-- Enable row level security
ALTER DATABASE prodsprints SET row_security = on;
