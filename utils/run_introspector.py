from schema_introspector import introspect_all, format_for_kb

connections = [
    {"db_type": "mongodb", "name": "yelp_businessinfo", "params": {"uri": "mongodb://127.0.0.1:27017", "database": "yelp_db"}},
    {"db_type": "duckdb",  "name": "yelp_user",         "params": {"db_path": "db/yelp_user.db"}},
]

result = introspect_all(connections)
print(format_for_kb(result))
print("## Join Key Mismatch Hints")
for h in result["join_key_hints"]:
    print("-", h)
