def num_there(s):
    for i in s:
        if not i.isalpha():
            return True
    return False

def build_sql(query, a):
    return "data"