from sqlalchemy import create_engine, text

engine = create_engine("postgresql://saleor:saleor@db/stavi")

with engine.connect() as conn:
    result = conn.execute(text("SELECT version();"))
    for row in result:
        print(row[0])
