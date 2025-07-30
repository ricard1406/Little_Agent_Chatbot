## 🔮 WORKING IN PROGRESS

-  SQL database agent support
-  Chatbot can retrive data from local SQL database
-  testing MariaDB support

```
example:
this is our table:

MariaDB [MYSTORE]> desc FRUITS;
+----------+-------------+------+-----+---------+-------+|
 Field    | Type        | Null | Key | Default | Extra |
+----------+-------------+------+-----+---------+-------+
| ITEM     | varchar(50) | YES  |     | NULL    |       |
| QUANTITY | int(11)     | YES  |     | NULL    |       |
+----------+-------------+------+-----+---------+-------+
2 rows in set (0.001 sec)

MariaDB [MYSTORE]> select * from FRUITS;
+---------+----------+
| ITEM    | QUANTITY |
+---------+----------+
| APPLES  |        2 |
| ORANGE  |        3 |
| APRICOT |        5 |
| GRAPES  |        4 |
| BANANA  |        1 |
+---------+----------+
5 rows in set (0.000 sec)

Prompt : do we have orange in our warehouse ?

(LLM)..... Entering new AgentExecutor chain...
Invoking: `get_SQL_response` with `{'SQL_statement': 'SELECT ITEM, QUANTITY FROM FRUITS'} .....

Response :
Based on the response from our warehouse management system, we do have oranges in stock.
The quantity of oranges available is 3 units.


