def send(self, query, *args):
    with self.connection.cursor(named_Tuple=True) as cursor:
        cursor.execute(query, (args))

def test(*args):
    print(args)

arg1 = 12
arg2 = 14

test(arg1, arg2)