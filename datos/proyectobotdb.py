from pathlib import Path
from sqlalchemy import create_engine

root = Path(__file__).resolve().parent.parent
path = root / "_docs" / "dulcineadb" / "proyectobot.db"

engine = create_engine(f"sqlite:///{path}")

# probar conexión
with engine.connect() as conn:
    print("Conexión exitosa")
    print("\n"*5)


from sqlalchemy import inspect

inspector = inspect(engine)

tables = inspector.get_table_names()
print("Tablas:", tables)
print("\n"*5)



for table in tables:
    print(f"\nTabla: {table}")
    columns = inspector.get_columns(table)

    for col in columns:
        print(f"  {col['name']} - {col['type']}")

print("\n"*5)


for table in tables:
    print(f"\nTabla: {table}")

    print("  Columnas:")
    for col in inspector.get_columns(table):
        print(f"    {col['name']} ({col['type']})")

    print("  PK:")
    print(inspector.get_pk_constraint(table))

    print("  FK:")
    for fk in inspector.get_foreign_keys(table):
        print(f"    {fk}")


"""

python3 -m datos.proyectobotdb

"""

