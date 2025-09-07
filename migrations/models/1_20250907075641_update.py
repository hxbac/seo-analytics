from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "article" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "url" VARCHAR(255),
    "lastmod" TIMESTAMPTZ,
    "changefreq" VARCHAR(50),
    "title" VARCHAR(255),
    "description" TEXT,
    "content" TEXT,
    "headline" VARCHAR(255),
    "author" VARCHAR(100),
    "datePublished" DATE,
    "dateModified" DATE,
    "h1" VARCHAR(255),
    "h2" JSONB,
    "word_count" INT,
    "image" VARCHAR(255),
    "keywords" JSONB,
    "website_id" INT NOT NULL REFERENCES "website" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "article";"""
