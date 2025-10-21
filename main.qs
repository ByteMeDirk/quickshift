my_data = source(type=csv, path='data.csv')
my_data1 = source(
    type=parquet,
    path='path/to/data/*.parquet',
    schema=schema(
        column(name='col1', type=str, nullable=True),
        column(name='col2', type=int, nullable=True),
        column(name='col2', type=int, nullable=False),
    )
)
my_data2 = source(
    type=postgres,
    path='postgres://user:password@host:port/database',
    table='table_name',
    schema=schema(
        column(name='col1', type=str, nullable=True),
        column(name='col2', type=int, nullable=True),
    )
)